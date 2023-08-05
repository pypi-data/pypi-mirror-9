
import logging
from collections import namedtuple, OrderedDict
from functools import partial
from itertools import combinations_with_replacement, starmap

import numpy as np
from scipy.stats import fisher_exact
import fisher
import pyopencl.clmath as clmath

from alpaca.index.utils import restore_alphabet
from alpaca.utils import LOG_TO_PHRED_FACTOR, PHRED_TO_LOG_FACTOR, np_round_to_int, MAX_INT, CLAlgorithm


Call = namedtuple("Call", "chrom pos alleles qual sample_info ensembl")
SampleInfo = namedtuple("SampleInfo", "genotype read_depth allele_depths strand_bias detailed_allele_depth")


class Calls(CLAlgorithm):

    def __init__(self, cl_queue, cl_mem_pool, index_slice, quals, called_sites, genotypes, genotype_ids):
        super().__init__(cl_queue, cl_mem_pool)
        self.quals = quals
        self.called_sites = called_sites
        self.index_slice = index_slice
        self.max_strand_bias = MAX_INT
        self.genotypes = genotypes
        self.genotype_ids = genotype_ids

    def filter(self, max_prob=None, min_total_depth=None, max_strand_bias=None):
        if max_strand_bias is not None:
            self.max_strand_bias = max_strand_bias
        if min_total_depth is None and max_prob is None:
            return
        passed = np.ones(self.quals.size, dtype=np.bool)
        if max_prob is not None:
            passed &= self.quals <= max_prob
        if min_total_depth is not None:
            passed &= np.sum(self.read_depth, axis=1) >= min_total_depth

        self.called_sites = self.called_sites[passed]
        self.quals = self.quals[passed]

    @property
    def read_depth(self):
        return self.index_slice.pileup_read_depth[:, self.called_sites].T

    @property
    def allele_depth(self):
        return np.transpose(self.index_slice.pileup_allele_depth[:, self.called_sites, :], axes=(1, 0, 2))

    @property
    def allele_rev_depth(self):
        return np.transpose(self.index_slice.pileup_allele_rev_depth[:, self.called_sites, :], axes=(1, 0, 2))

    def __iter__(self):
        if not self.quals.size:
            # return empty iterator
            return iter([])

        logging.debug("handle qualities")
        qual = np_round_to_int(self.quals * LOG_TO_PHRED_FACTOR)

        logging.debug("determine pos on chromosome {}".format(self.index_slice.reference_name))
        chrom = [self.index_slice.reference_name] * len(self.called_sites)
        pos = self.index_slice.reference_positions[self.called_sites]

        logging.debug("transpose such that site is first dimension")
        maxlikelihood_genotypes = self.index_slice.pileup_maxlikelihood_genotypes[:, self.called_sites].T
        allele_depth = self.allele_depth
        allele_rev_depth = self.allele_rev_depth
        read_depth = self.read_depth

        logging.debug("determine ref and alt")
        ref = self.index_slice.reference_genotypes[self.called_sites]
        alleles = list(self.calc_alleles(maxlikelihood_genotypes, ref))

        logging.debug("calc strand bias")
        strand_bias = self.calc_strand_bias(alleles, allele_depth, allele_rev_depth)

        logging.debug("compose detailed allele depth")
        detailed_allele_depth = np.concatenate((allele_depth - allele_rev_depth, allele_rev_depth), axis=2)

        logging.debug("calculate sample info")
        sample_info = list(self.calc_sample_info(maxlikelihood_genotypes, alleles, read_depth, allele_depth, allele_rev_depth, strand_bias, detailed_allele_depth))
        ensembl = [list()] * len(ref)

        logging.debug("decode ref and alt")
        alleles = [restore_alphabet(a) for a in alleles]
        logging.debug("done")
        return filter(
            self.valid_strand_bias,
            starmap(Call, zip(chrom, pos, alleles, qual, sample_info, ensembl))
        )

    def calc_strand_bias(self, alleles, allele_depth, allele_rev_depth):
        ref = [pos_alleles[0] for pos_alleles in alleles]
        alt = [pos_alleles[1] for pos_alleles in alleles]
        allele_fwd_depth = allele_depth - allele_rev_depth

        logging.debug("collecting allele counts")
        allele_fwd_depth = allele_fwd_depth.transpose((0,2,1))
        allele_rev_depth = allele_rev_depth.transpose((0,2,1))
        positions = np.arange(allele_fwd_depth.shape[0])

        a = allele_fwd_depth[positions, ref].flatten()
        b = allele_rev_depth[positions, ref].flatten()
        c = allele_fwd_depth[positions, alt].flatten()
        d = allele_rev_depth[positions, alt].flatten()

        pvals = [
            #fisher.pvalue(v_a, v_b, v_c, v_d).two_tail
            fisher_exact(np.array([[v_a, v_b], [v_c, v_d]], dtype=np.int32))[1]
            for v_a, v_b, v_c, v_d in zip(a, b, c, d)
        ]

        logging.debug("finding multiallelic sites")
        multiallele = np.nonzero(
            np.array(
                [pos_alleles.size for pos_alleles in alleles],
                dtype=np.int8
            ) > 2
        )

        logging.debug("transforming to PHRED scale")
        pvals = np.log(pvals)
        pvals *= LOG_TO_PHRED_FACTOR
        pvals = np_round_to_int(pvals).reshape(len(ref), -1)

        logging.debug("masking invalid values")
        pvals[multiallele, :] = -1
        return pvals

    def calc_sample_info(self, maxlikelihood_genotypes, alleles, read_depth, allele_depth, allele_rev_depth, strand_bias, detailed_allele_depth, log_to_phred_factor=LOG_TO_PHRED_FACTOR):

        for pos_alleles, pos_read_depth, pos_allele_depth, pos_allele_rev_depth, pos_strand_bias, pos_maxlikelihood_genotypes, pos_detailed_allele_depth in zip(alleles, read_depth, allele_depth, allele_rev_depth, strand_bias, maxlikelihood_genotypes, detailed_allele_depth):

            genotypes = OrderedDict()
            for gt, gt_allele_index in zip(
                combinations_with_replacement(pos_alleles, self.index_slice.ploidy),
                combinations_with_replacement(range(len(pos_alleles)), self.index_slice.ploidy)
            ):
                gt_id = self.genotype_ids[gt]
                genotypes[gt_id] = gt_allele_index

            # collect genotypes
            samples_genotypes = [genotypes[gt] for gt in pos_maxlikelihood_genotypes]
            samples_allele_depths = pos_allele_depth[:, pos_alleles]

            yield list(starmap(SampleInfo, zip(samples_genotypes, pos_read_depth, samples_allele_depths, pos_strand_bias, pos_detailed_allele_depth)))

    def calc_alleles(self, maxlikelihood_genotypes, ref):
        genotypes = self.genotypes
        for ref, gts in zip(ref, maxlikelihood_genotypes):
            alleles = np.concatenate(
                (
                    [ref],
                    np.unique([a for gt in genotypes[gts] for a in gt if a != ref])
                )
            )
            yield alleles

    def valid_strand_bias(self, call):
        return all([sample.strand_bias <= self.max_strand_bias for sample in call.sample_info])

    def __len__(self):
        return self.quals.size
