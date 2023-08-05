
import logging
import math
from collections import namedtuple

import pyopencl as cl
import pyopencl.clmath as clmath
import pyopencl.algorithm as clalg
import numpy as np
from mako.template import Template

from alpaca.index.view import IndexView
from alpaca.index.utils import INDEL_ALLELE, calc_genotypes, calc_genotype_ids
from alpaca.utils import CLAlgorithm, PHRED_TO_LOG_FACTOR, LOG_TO_PHRED_FACTOR, cl_logsum, cl_logsum_array, MIN_FLOAT, ElementwiseKernel, print_progress, np_index_true
from alpaca.caller.calls import Calls
from alpaca import algebra


CLSlice = namedtuple("CLSlice", "pileup_allelefreq_likelihoods candidate_sites")


class Caller(CLAlgorithm):
    def __init__(
        self,
        cl_queue,
        cl_mem_pool,
        formula,
        index,
        heterozygosity=0.001,
        min_qual=30,
        min_total_pileup_depth=1,
        max_indel_fraction=0.05,
        buffersize=1000000
    ):
        super().__init__(cl_queue, cl_mem_pool)

        self.max_reference_genotype_probability = PHRED_TO_LOG_FACTOR * min_qual
        self.max_indel_fraction = max_indel_fraction
        self.min_total_pileup_depth = min_total_pileup_depth
        self.formula = formula
        self.index = index

        self.query_samples = algebra.get_samples(self.formula)

        self.genotypes = calc_genotypes(self.index.ploidy)
        self.genotype_ids = calc_genotype_ids(self.genotypes, self.index.ploidy)
        self.calling_tree = self.build_calling_tree(heterozygosity=heterozygosity)

        self.cl_calc_candidate_sites = ElementwiseKernel(
            cl_queue.context,
            "const int site_count, "
            "const char* reference_genotypes, "
            "const char* pileup_maxlikelihood_genotypes, "
            "int* candidate_sites",
            Template(
                """
                const char ref = reference_genotypes[i];
                const int base = i * ${sample_count};
                bool is_candidate = false;
                #pragma unroll ${sample_count}
                for(int j=0; j<${sample_count} && !is_candidate; j++)
                {
                    is_candidate |= ref != pileup_maxlikelihood_genotypes[j * site_count + i];
                }
                candidate_sites[i] = is_candidate ? i : -1;
                """
            ).render(sample_count=len(self.query_samples))
        )

    def call(self):
        calls = []
        processed = 0
        called = 0
        for seq_view in self.index.get(self.query_samples):
            for index_slice in seq_view:
                logging.debug("calculating candidate sites")
                cl_candidate_sites, clcount = self.calc_candidate_sites(index_slice)

                logging.debug("loading slice")
                cl_slice = CLSlice(
                    pileup_allelefreq_likelihoods=self.to_device(
                        index_slice.pileup_allelefreq_likelihoods, async=True
                    ),
                    candidate_sites=cl_candidate_sites[:clcount.get().item()]
                )
                if not cl_slice.candidate_sites.size:
                    continue

                logging.debug("calling sites")
                reference_genotype_probabilities = self.calling_tree.apply(
                    cl_slice
                ).get()

                logging.debug("filtering calls")
                called_sites = np_index_true(
                    reference_genotype_probabilities
                    <= self.max_reference_genotype_probability
                )

                if called_sites.size:
                    # disabling indel filtering because BAQ should take care of that
                    #called_sites = self.filter_indel_sites(index_slice, called_sites)
                    logging.debug("done")
                    if called_sites.size:
                        quals = reference_genotype_probabilities[called_sites]

                        calls.append(
                            Calls(
                                self.cl_queue,
                                self.cl_mem_pool,
                                index_slice,
                                quals,
                                called_sites,
                                self.genotypes,
                                self.genotype_ids
                            )
                        )
                called += called_sites.size
                processed += len(index_slice)
                print_progress(processed, len(self.index))
                logging.debug("called {} sites".format(called))
        return calls

    def calc_candidate_sites(self, index_slice):
        cl_reference_genotypes = self.to_device(
            index_slice.reference_genotypes, async=True
        )
        cl_pileup_maxlikelihood_genotypes = self.to_device(
            index_slice.pileup_maxlikelihood_genotypes, async=True
        )
        site_count = cl_reference_genotypes.size
        cl_candidate_sites = self.empty(
            cl_reference_genotypes.shape, dtype=np.int32
        )
        self.cl_calc_candidate_sites(
            np.int32(site_count),
            cl_reference_genotypes,
            cl_pileup_maxlikelihood_genotypes,
            cl_candidate_sites
        )
        cl_candidate_sites, clcount, _ = clalg.copy_if(
            cl_candidate_sites, "ary[i] >= 0"
        )
        return cl_candidate_sites, clcount

    def filter_indel_sites(self, index_slice, called_sites):
        logging.debug("filtering indel sites")
        indel_depth = index_slice.pileup_allele_depth[:, called_sites, INDEL_ALLELE]
        indel_fraction = indel_depth / index_slice.pileup_read_depth[:, called_sites]
        non_indel_sites = np_index_true(np.any(indel_fraction <= self.max_indel_fraction, axis=0))
        return called_sites[non_indel_sites]

    def build_calling_tree(self, heterozygosity=0.001):
        sample_id = {sample: i for i, sample in enumerate(self.query_samples)}

        def _build_calling_tree(node):
            if isinstance(node, algebra.SampleUnion):
                sample_ids = np.array(
                    [sample_id[child] for child in node.children],
                    dtype=np.int32
                )
                sample_ids.sort()
                return SampleUnion(
                    self.cl_queue,
                    self.cl_mem_pool,
                    self.index,
                    sample_ids,
                    self.genotypes,
                    # use node specific het if defined
                    heterozygosity=node.heterozygosity or heterozygosity
                )

            if isinstance(node, algebra.Union):
                _node = Union(self.cl_queue, self.cl_mem_pool)
            if isinstance(node, algebra.RelaxedIntersection):
                children = sorted(
                    (_build_calling_tree(child) for child in node.children),
                    # each child of the intersection is a SampleUnion with one child
                    key=lambda child: child.sample_ids[0]
                )
                return RelaxedIntersection(self.cl_queue, self.cl_mem_pool, children, k=node.k)
            else:
                _node = Difference(self.cl_queue, self.cl_mem_pool)

            _node.left_child, _node.right_child = (_build_calling_tree(child) for child in node.children)
            return _node
        return _build_calling_tree(self.formula)


class Operator(CLAlgorithm):
    def __init__(self, cl_queue, cl_mem_pool):
        super().__init__(cl_queue, cl_mem_pool)
        self.left_child = None
        self.right_child = None

    def apply(self, cl_slice):
        raise NotImplementedError()


class BinaryOperator(Operator):
    def apply(self, cl_slice):
        return self.calc_cl_reference_genotype_probabilities(self.left_child.apply(cl_slice), self.right_child.apply(cl_slice), cl_slice.candidate_sites)


class Union(BinaryOperator):
    def __init__(self, cl_queue, cl_mem_pool):
        super().__init__(cl_queue, cl_mem_pool)
        self.cl_calc_reference_genotype_probabilities = ElementwiseKernel(cl_queue.context,
            "const int* candidate_sites, "
            "float* reference_genotype_probabilities_a, "
            "const float* reference_genotype_probabilities_b",
            """
            const int site = candidate_sites[i];
            reference_genotype_probabilities_a[site] = 
                reference_genotype_probabilities_a[site] +
                reference_genotype_probabilities_b[site];
            """,
            name="calc_reference_probabilities",
            preamble=cl_logsum())

    def calc_cl_reference_genotype_probabilities(self, cl_reference_genotype_probabilities_a, cl_reference_genotype_probabilities_b, cl_candidate_sites):
        self.cl_calc_reference_genotype_probabilities(cl_candidate_sites, cl_reference_genotype_probabilities_a, cl_reference_genotype_probabilities_b)
        return cl_reference_genotype_probabilities_a


class Difference(BinaryOperator):
    """Difference operator.

    .. math:

       \phi - \psi \Leftrightarrow 1 - ( P(X > 0 | \phi) P(X = 0 | \psi) )

    or

    .. math:

       1 - ( (1 - P(X = 0 | \phi)) P(X = 0 | \psi) )

    For numerical stability, we reformulate into:

    .. math:

       1 - P(X = 0 | \psi) + P(X = 0 | \phi) P(X = 0 | \psi)

    """
    def __init__(self, cl_queue, cl_mem_pool):
        super().__init__(cl_queue, cl_mem_pool)
        self.cl_calc_reference_genotype_probabilities = ElementwiseKernel(cl_queue.context,
            "const int* candidate_sites, "
            "float* reference_genotype_probabilities_a, "
            "const float* reference_genotype_probabilities_b",
            r"""
            const int site = candidate_sites[i];

            reference_genotype_probabilities_a[site] = logsum(
                log1p(-exp(reference_genotype_probabilities_b[site])),
                reference_genotype_probabilities_a[site] + reference_genotype_probabilities_b[site]
            );
            """,
            name="calc_reference_probabilities",
            preamble=cl_logsum())

    def calc_cl_reference_genotype_probabilities(self, cl_reference_genotype_probabilities_a, cl_reference_genotype_probabilities_b, cl_candidate_sites):
        self.cl_calc_reference_genotype_probabilities(cl_candidate_sites, cl_reference_genotype_probabilities_a, cl_reference_genotype_probabilities_b)
        return cl_reference_genotype_probabilities_a


class SampleUnion(Operator):

    def __init__(self, cl_queue, cl_mem_pool, index, sample_ids, genotypes, heterozygosity=0.001, ):
        super().__init__(cl_queue, cl_mem_pool)
        self.index = index
        self.ploidy = index.ploidy
        self.heterozygosity = heterozygosity
        self.sample_ids = np.array(sample_ids, dtype=np.int32)
        self.cl_sample_ids = self.to_device(self.sample_ids)
        self.sample_count = len(sample_ids)
        max_allele_freq = self.sample_count * self.ploidy

        self.cl_allelefreq_probabilities = self.calc_cl_allelefreq_probabilities(max_allele_freq)
        self.cl_genotypes = self.to_device(genotypes)
        self.genotypes_count = self.cl_genotypes.shape[0]

        self.work_group_size = min(128, cl_queue.device.max_work_group_size)

        preamble = Template("""
        #define WORK_GROUP_SIZE ${work_group_size}
        #define SAMPLE_COUNT ${sample_count}
        #define MIN_FLOAT ${min_float}
        #define PLOIDY ${ploidy}
        #define MAX_ALLELE_FREQ ${max_allele_freq}
        #define GENOTYPES ${genotypes}
        #define GENOTYPE(g, a)    genotypes[g * ${ploidy} + a]
        """).render(
            genotypes=self.genotypes_count,
            ploidy=self.ploidy,
            min_float=MIN_FLOAT,
            sample_count=self.sample_count,
            max_allele_freq=max_allele_freq,
            work_group_size=self.work_group_size
        )

        self.cl_calc_pileup_probabilities = cl.Program(cl_queue.context,
        preamble + cl_logsum() + cl_logsum_array(count=self.ploidy + 1) +
        r"""
        __kernel void calc_pileup_probabilities
        (
            const int site_count,
            const int candidate_site_count,
            __global const int* candidate_sites,
            __global const int* samples,
            __global const float* allelefreq_probabilities,
            __global const float* pileup_allelefreq_likelihoods,
            __global float* pileup_probabilities
        )
        {
            const int i = get_global_id(0);

            if(i >= candidate_site_count)
                return;

            const int site = candidate_sites[i];

            const int lid = get_local_id(0);

            __local float z[WORK_GROUP_SIZE][SAMPLE_COUNT + 1][PLOIDY + 1]; // log-space
            #pragma unroll
            for(int a=0; a<=PLOIDY; a++)
            {
                for(int j=0; j<=SAMPLE_COUNT; j++)
                    z[lid][j][a] = MIN_FLOAT;  // i.e. 0 in non log space
            }
            z[lid][0][0] = 0;  // i.e. 1 in non log space


            // TODO check code and comment comprehensively
            float pileup_probability = MIN_FLOAT;

            for(int allelefreq=0; allelefreq<=MAX_ALLELE_FREQ; allelefreq++)
            {
                // set z00 to 1 (i.e. 0 in log space) while it is possible to achive the allele freq with the first sample only.
                // afterwards, set it to -inf like the other z0x values
                z[lid][0][0] = MIN_FLOAT * (allelefreq > PLOIDY);

                const int targetcol = allelefreq % (PLOIDY + 1);
                for(int j=1; j<=SAMPLE_COUNT; j++)
                {
                    const int base = samples[j - 1] * site_count * (PLOIDY + 1) + site * (PLOIDY + 1);
                    float s[PLOIDY + 1];
                    #pragma unroll
                    for(int a=0; a<=PLOIDY; a++)
                    {
                        // select the column to work with
                        const int k = abs((allelefreq >= a) * allelefreq - a) % (PLOIDY + 1);
                        s[a] = z[lid][j - 1][k] + pileup_allelefreq_likelihoods[base + a];
                    }
                    z[lid][j][targetcol] = logsum_array(s);
                }
                // from de Pristo et al 2011 and Heng Li, 
                // "Mathematical Notes on Samtools Algorithms"
                // we can derive P(D|allelefreq=k) = z[lid][SAMPLE_COUNT][k]
                pileup_probability = logsum(z[lid][SAMPLE_COUNT][targetcol] + allelefreq_probabilities[allelefreq], pileup_probability);
            }
            pileup_probabilities[site] = pileup_probability;
        }
        """
        ).build().calc_pileup_probabilities

        # follows dePristo et al. Nature 2011
        self.cl_calc_reference_genotype_probabilities = ElementwiseKernel(self.cl_queue.context,
        "const int site_count, "
        "const int* candidate_sites, "
        "const int* samples, "
        "const float* pileup_probabilities, "  # log scaled
        "const float* pileup_allelefreq_likelihoods, "  # log scaled
        "const float* allelefreq_probabilities, "  # log scaled
        "float* reference_probabilities",
        r"""
        const int site = candidate_sites[i];
        float reference_genotype_probability = 0;
        for(int j=0; j<SAMPLE_COUNT; j++)
        {
            reference_genotype_probability += pileup_allelefreq_likelihoods[samples[j] * site_count * (PLOIDY + 1) + site * (PLOIDY + 1)];
        }
        
        reference_probabilities[site] = allelefreq_probabilities[0] + reference_genotype_probability - pileup_probabilities[site];
        """,
        preamble=preamble,
        name="calc_pileup_reference_probability")

    def calc_cl_pileup_probabilities(
        self, cl_pileup_allelefreq_likelihoods, cl_candidate_sites):
        r"""Calculate pileup probability.
        
        The calculations are derived from dePristo et al 2011 and Heng Li, Mathematical Notes on Samtools Algorithms.
        Let :math:`D=D_0, \dots, D_n` be a set of pileups from different samples at one position
        cl_pileup_probabilities is calculated as :math:`P(D) = \sum_{k=0,\dots,m} P(D | X = k) P(X = k)`
        with
        
        .. math:
        
           P(D | X = k) = \sum_{(g_1, \dots, g_n} \in G^n with \sum_{i=1,\dots,n} |gi| = k} \prod_{i=1,\dots,n} P(D_i | g_i)
       
        We calculate :math:`P(D | X = k) = z_{n,k}` by dynamic programming over the single-pileup likelihoods :math:`P(D_i | X = k)` with
        :math:`z_{i,l} = \sum_{k=0,\dots,m} z_{i-1,l-k} P(D_i | X = k)` and :math:`z_{i,l} = 0` for i or l less than zero.
        
        Args:
            cl_pileup_allelefreq_likelihoods (pyopencl.array.Array): the allelefreq likelihoods from the alpaca index
            cl_candidate_sites (pyopencl.array.Array): the candidate sites
        
        Returns:
            pyopencl.array.Array: the pileup probabilities
        """
        assert len(cl_pileup_allelefreq_likelihoods.shape) == 3
        site_count = cl_pileup_allelefreq_likelihoods.shape[1]

        cl_pileup_probabilities = self.empty(
            site_count,
            np.float32)

        candidate_site_count = len(cl_candidate_sites)

        logging.debug("calculating marginal pileup probability for {} sites".format(candidate_site_count))
        global_dim, wg_dim = self.get_dimensions(cl_candidate_sites.shape, self.work_group_size)
        self.cl_calc_pileup_probabilities(
            self.cl_queue,
            global_dim,
            wg_dim,
            np.int32(site_count),
            np.int32(candidate_site_count),
            cl_candidate_sites.data,
            self.cl_sample_ids.data,
            self.cl_allelefreq_probabilities.data,
            cl_pileup_allelefreq_likelihoods.data,
            cl_pileup_probabilities.data).wait()
        logging.debug("done")
        return cl_pileup_probabilities

    def calc_cl_reference_genotype_probabilities(self, cl_pileup_allelefreq_likelihoods, cl_candidate_sites):
        r"""Calculate reference genotype probabilities.
        
        reference_genotype_probabilities is calculated as :math:`P(X = 0 | D) = \frac{P(X = 0) P(D | X = 0)}{P(D)}` as defined in dePristo et al 2011.
        
        Args:
            cl_pileup_allelefreq_likelihoods (pyopencl.array.Array): alt allele frequency likelihoods
            cl_candidate_sites (pyopencl.array.Array): the candidate sites
        
        Returns:
            pyopencl.array.Array: the reference genotype probabilities
        """
        site_count = cl_pileup_allelefreq_likelihoods.shape[1]

        cl_reference_genotype_probabilities = self.zeros(
            site_count, np.float32
        )

        cl_pileup_probabilities = self.calc_cl_pileup_probabilities(
            cl_pileup_allelefreq_likelihoods,
            cl_candidate_sites
        )

        self.cl_calc_reference_genotype_probabilities(
            np.int32(site_count),
            cl_candidate_sites,
            self.cl_sample_ids,
            cl_pileup_probabilities,
            cl_pileup_allelefreq_likelihoods,
            self.cl_allelefreq_probabilities,
            cl_reference_genotype_probabilities
        )
        return cl_reference_genotype_probabilities

    def calc_cl_allelefreq_probabilities(self, max_allele_freq):
        """Calculate prior allelefreq probabilities.
        
        Follows directly dePristo et al. 2011.
        
        Args:
            max_allele_freq (int): maximum possible alternate allele frequency over all samples
        
        Returns:
            pyopencl.array.Array: the allele frequency priors
        """
        heterozygosity = np.log(self.heterozygosity)
        allelefreq_probabilities = np.arange(max_allele_freq + 1, dtype=np.float32)
        allelefreq_probabilities[1:] = heterozygosity - np.log(allelefreq_probabilities[1:])
        allelefreq_probabilities[0] = np.log(1 - self.heterozygosity * sum(1 / i for i in range(1, self.ploidy * self.sample_count + 1)))
        return self.to_device(allelefreq_probabilities)

    def apply(self, cl_slice):
        return self.calc_cl_reference_genotype_probabilities(*cl_slice)


class RelaxedIntersection(Operator):
    def __init__(self, cl_queue, cl_mem_pool, children, k=None):
        super().__init__(cl_queue, cl_mem_pool)
        self.k = len(children) if k is None else k
        assert k >= 0 and k <= len(children)
        self.children = children

        self.cl_calc_zjk = ElementwiseKernel(cl_queue.context,
            "const float* sample_reference_prob, "
            "const float* sample_variant_prob, "
            "float* zjk",
            """
            zjk[i] = logsum(sample_variant_prob[i], sample_reference_prob[i]);
            """,
            preamble=cl_logsum()
        )

        self.cl_update_posteriors = ElementwiseKernel(cl_queue.context,
            "const float* z, "
            "float* posterior_probabilities",
            """
            posterior_probabilities[i] = logsum(posterior_probabilities[i], z[i]);
            """,
            preamble=cl_logsum()
        )

    def calc_cl_relaxed_reference_genotype_probabilities(
        self, sample_cl_reference_genotype_probabilities
    ):
        sample_count = len(sample_cl_reference_genotype_probabilities)
        site_count = len(sample_cl_reference_genotype_probabilities[0])
        cl_z = self.empty((sample_count + 1, 2, site_count), np.float32)
        cl_z.fill(-np.inf)
        cl_z[0,0, :] = 0

        cl_posterior_probabilities = self.empty((site_count,), np.float32)
        cl_posterior_probabilities.fill(-np.inf)

        # k is the number of variant samples
        # j indicates the subset 1,...,j of samples investigated
        for k in range(self.k):
            for j in range(1, sample_count + 1):
                cl_reference_genotype_probabilities = sample_cl_reference_genotype_probabilities[j - 1]

                cl_sample_reference_prob = cl_z[j - 1, k % 2] + cl_reference_genotype_probabilities
                cl_sample_variant_prob = cl_z[j - 1, (k - 1) % 2] + clmath.log1p(
                    -clmath.exp(cl_reference_genotype_probabilities)
                )

                self.cl_calc_zjk(cl_sample_reference_prob, cl_sample_variant_prob, cl_z[j, k])
            # the probability for less than self.k non-ref samples is 
            # the sum over 0 <= k < self.k
            self.cl_update_posteriors(cl_z[sample_count, k], cl_posterior_probabilities)
        return cl_posterior_probabilities

    def apply(self, cl_slice):
        return self.calc_cl_relaxed_reference_genotype_probabilities(
            [child.apply(cl_slice) for child in self.children]
        )
