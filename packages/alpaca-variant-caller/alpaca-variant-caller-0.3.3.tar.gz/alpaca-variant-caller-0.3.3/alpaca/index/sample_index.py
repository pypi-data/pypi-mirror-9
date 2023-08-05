

import os
import sys
import math
import logging
from functools import partial
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from queue import Empty as EmptyQueue

import numpy as np
import pyopencl as cl
import h5py
from pyopencl.elementwise import ElementwiseKernel
from mako.template import Template

from alpaca.utils import (
    CLAlgorithm, MIN_FLOAT, LOG_TO_PHRED_FACTOR, PHRED_TO_LOG_FACTOR,
    cl_logsum, cl_logsum_array, AlpacaError, flocked, np_slice,
    print_progress, np_index_true
)
from alpaca.index.pileup import calc_pileup
from alpaca.index.utils import (
    check_index, calc_min_bits, calc_genotype_allelefreq_probability,
    calc_genotypes, BITENCODE, N_BITENCODED, TECHNOLOGY_MISCALL_PROB,
    ALLELE_COUNT, INDEL_SHADOW_BITENCODED, ALPHABET_MIN_REVCOMP,
    ALPHABET_INDEL_SHADOW, read_fai
)
from alpaca.index.version import __version__


class SampleIndex(CLAlgorithm):
    def __init__(
        self,
        cl_queue,
        cl_mem_pool,
        hdf5path,
        buffersize=1000000,
        ploidy=2,
        max_pileup_depth=250,
        qual_offset=33,
        technology="illumina"
    ):
        """Constructor.
        
        Args:
            cl_queue (pyopencl.CommandQueue): the OpenCL queue
            cl_mem_pool (pyopencl.tools.MemoryPool): the OpenCL memory pool
            hdf5path (str): path to index
            buffersize (int): buffer size
            ploidy (int): ploidy
            max_pileup_depth (int): maximum pileup depth
            qual_offset (int): offset for PHRED scaled quality values in bam file
            technology (int): technology that was used for sequencing
        """
        super().__init__(cl_queue, cl_mem_pool)

        # we assume a ploidy of at most 9 such that we can store various 
        # values in a single char
        assert 0 < ploidy <= 9

        self.hdf5path = hdf5path

        self.buffersize = buffersize
        self.ploidy = ploidy
        self.max_pileup_depth = max_pileup_depth
        self.cl_bitencode = self.to_device(BITENCODE)
        self.cl_genotypes = self.to_device(calc_genotypes(ploidy))
        self.genotypes_count = len(self.cl_genotypes)
        # probability to sample genotype given an allelefreq
        self.cl_genotype_allelefreq_probability = self.to_device(
            calc_genotype_allelefreq_probability(ploidy)
        )
        self.qual_offset = qual_offset
        self.cl_technology_miscall_prob = self.to_device(
            TECHNOLOGY_MISCALL_PROB[technology]
        )

        self.preamble = Template(
            """
            #define GENOTYPES_COUNT ${genotypes_count}
            #define PLOIDY ${ploidy}
            #define LOG_PLOIDY ${log_ploidy}
            #define NBASE ${nbase}
            #define GENOTYPE(g, a)    genotypes[g * ${ploidy} + a]
            #define LOG_TO_PHRED_FACTOR ${log_to_phred_factor}
            #define PHRED_TO_LOG_FACTOR ${phred_to_log_factor}
            #define MIN_FLOAT ${min_float}
            #define ALLELE_COUNT ${allele_count}
            #define INDEL_SHADOW ${indel_shadow}
            #define MIN_REVCOMP ${min_revcomp}
            ${cl_logsum}
            """
        ).render(
            min_float=MIN_FLOAT,
            genotypes_count=self.genotypes_count,
            ploidy=ploidy,
            nbase=ord(N_BITENCODED),
            log_to_phred_factor=LOG_TO_PHRED_FACTOR,
            phred_to_log_factor=PHRED_TO_LOG_FACTOR,
            log_ploidy=np.float32(math.log(ploidy)),
            allele_count=ALLELE_COUNT,
            indel_shadow=ord(INDEL_SHADOW_BITENCODED),
            min_revcomp=ALPHABET_MIN_REVCOMP,
            cl_logsum=cl_logsum()
        )

        # base likelihood given genotype as defined in de Pristo et al 2011
        self.cl_calc_base_likelihoods = ElementwiseKernel(
            self.cl_queue.context,
            "const char genotype, "
            "const int* candidate_bases, "
            "const char* seqs, "
            "const char* quals, "
            "const char* bitencode, "
            "const char* genotypes, "
            "const float* technology_miscall_prob, "
            "float* base_likelihoods",
            r"""
            const int j = candidate_bases[i];
            const char allele = bitencode[seqs[j]];
            const char rev_allele = REVCOMP(allele);
            const char is_revcomp = seqs[j] >= MIN_REVCOMP;
            const float prob_miscall = PHRED_TO_LOG_FACTOR * quals[j];
            const float prob_call = log1p(-exp(prob_miscall));

            float allele_likelihoods[PLOIDY];
            # pragma unroll
            for(int a=0; a<PLOIDY; a++)
            {
                const char genotype_allele = genotypes[genotype * PLOIDY + a];
                
                if(allele == genotype_allele || allele == NBASE)
                {
                    allele_likelihoods[a] = prob_call;
                }
                else
                {
                    const int idx = (is_revcomp) ? 
                        REVCOMP(genotype_allele) * 4 + rev_allele :
                        genotype_allele * 4 + allele;
                    const float a_priori_miscall = technology_miscall_prob[idx];
                    allele_likelihoods[a] = prob_miscall + a_priori_miscall;
                }
            }
            base_likelihoods[j] = logsum_array(allele_likelihoods) - LOG_PLOIDY;
            """,
            preamble=self.preamble + cl_logsum_array(count=self.ploidy) + """
            #define REVCOMP(a) (3 - a)
            """,
            name="calc_base_likelihoods"
        )

        # genotype likelihood as defined in de Pristo et al 2011
        self.cl_calc_pileup_genotype_likelihoods = ElementwiseKernel(
            self.cl_queue.context,
            "const char genotype, "
            "const int* pileup_address, "
            "const float* base_likelihoods, "
            "float* pileup_genotype_likelihoods",
            r"""
            const int jmin = pileup_address[i];
            const int jmax = pileup_address[i + 1];

            // calculate genotype likelihood
            float genotype_likelihood = 0;
            for(int j=jmin; j<jmax; j++)
            {
                genotype_likelihood += base_likelihoods[j];
            }
            pileup_genotype_likelihoods[i * GENOTYPES_COUNT + genotype] = genotype_likelihood;
            """,
            preamble=self.preamble,
            name="calc_pileup_genotype_likelihoods"
        )

        self.cl_bitencode_ref_alleles = ElementwiseKernel(
            cl_queue.context,
            "char* reference_alleles, "
            "const char* bitencode",
            """
            reference_alleles[i] = bitencode[reference_alleles[i]]
            """,
            name="bitencode_reference_alleles"
        )

        self.cl_calc_genotype_alt_allelefreqs = ElementwiseKernel(
            cl_queue.context,
            "const char* reference_alleles, "
            "const char* genotypes, "
            "char* genotype_alt_allelefreqs",
            r"""
            const char ref_allele = reference_alleles[i];
            int alt_allelefreq_base = i * GENOTYPES_COUNT;
            // the homozygous genotypes are the first 4
            #pragma unroll
            for(int g=0; g<4; g++)
            {
                const char alt_allelefreq = (GENOTYPE(g, 0) != ref_allele) * PLOIDY;
                genotype_alt_allelefreqs[alt_allelefreq_base + g] = alt_allelefreq;
            }
            for(int g=4; g<GENOTYPES_COUNT; g++)
            {
                char alt_allelefreq = 0;
                #pragma unroll
                for(int a=0; a<PLOIDY; a++)
                {
                    alt_allelefreq += GENOTYPE(g, a) != ref_allele;
                }
                genotype_alt_allelefreqs[alt_allelefreq_base + g] = alt_allelefreq;
            }
            """,
            preamble=self.preamble,
            name="calc_genotype_alt_allelefreqs"
        )

        self.cl_calc_pileup_allelefreq_likelihoods = ElementwiseKernel(
            self.cl_queue.context,
            "const char* genotype_alt_allelefreqs, "
            "const float* genotype_allelefreq_probability, "
            "const float* pileup_genotype_likelihoods, "
            "float* pileup_allelefreq_likelihoods",
            r"""
            const int base = i * (PLOIDY + 1);

            for(int g=0; g<GENOTYPES_COUNT; g++)
            {
                const float genotype_likelihood = pileup_genotype_likelihoods[i * GENOTYPES_COUNT + g];
                const char alt_allelefreq = genotype_alt_allelefreqs[i * GENOTYPES_COUNT + g];

                const int addr = base + alt_allelefreq;
                pileup_allelefreq_likelihoods[addr] = logsum(pileup_allelefreq_likelihoods[addr], genotype_likelihood + genotype_allelefreq_probability[alt_allelefreq]);
            }
            """,
            preamble=self.preamble,
            name="calc_pileup_allelefreq_likelihoods"
        )

        def get_cl_calc_pileup_depths(name, filter):
            return ElementwiseKernel(
                self.cl_queue.context,
                "const int* pileup_address, "
                "const char* seqs, "
                "const unsigned char* bitencode, "
                "unsigned char* pileup_allele_depth",
                Template(r"""
                const int base_addr = i * ALLELE_COUNT;
                for(int j=pileup_address[i]; j<pileup_address[i + 1]; j++)
                {
                    if(${filter})
                    {
                        const unsigned char allele = bitencode[seqs[j]];
                        const int addr = base_addr + allele;
                        // count the observed base
                        pileup_allele_depth[addr]++;
                    }
                }
                """).render(filter=filter),
                preamble=self.preamble,
                name=name
            )

        self.cl_calc_pileup_allele_depths = get_cl_calc_pileup_depths(
            "calc_pileup_allele_depths",
            "true"
        )
        self.cl_calc_pileup_allele_rev_depths = get_cl_calc_pileup_depths(
            "calc_pileup_allele_rev_depths",
            "seqs[j] >= {}".format(ALPHABET_MIN_REVCOMP)
        )

    def init(self, hdf5, sample_name):
        """Initialize the alpaca index.
        
        Args:
            hdf5 (h5py.File): an opened HDF5 alpaca index
            sample_name (str): the sample name
        """

        hdf5_index = hdf5.create_group("alpaca_sample_index")
        hdf5_index.attrs["sample"] = sample_name
        hdf5_index.attrs["version"] = __version__
        hdf5_index.attrs["ploidy"] = self.ploidy
        hdf5_index.create_group("sequences")

    def store_seq(
        self,
        hdf5_index,
        seq,
        pileup_allelefreq_likelihoods,
        pileup_maxlikelihood_genotypes_diff,
        pileup_allele_depth,
        pileup_allele_rev_depth,
        reference_positions_incr,
        compression_type=None,
        compression_shuffle=False,
        compression_half=False,
        chunksize=1000000
    ):
        """Store sequence index data in HDF5.
        
        Args:
            hdf5_index: the hdf5 index object
            seq (str): the name of the sequence to store
            pileup_allelefreq_likelihoods (np.ndarray): allelefreq likelihoods
            pileup_maxlikelihood_genotypes (np.ndarray): maximum likelihood genotypes
            pileup_allele_depth (np.ndarray): allele frequencies
            pileup_allele_rev_depth (np.ndarray): reverse complement allele frequencies
            reference_positions (np.ndarray): reference positions
        """
        # compression (optionally) strategies:
        # try to get as many equal values subsequently as possible
        # - shuffle filter
        # - maxlikelihood_genotypes: save as difference to ref genotype 
        # - allelefreq_likelihoods:
        #   - quantize loci with ref genotype? not for now.
        # - values in the same column will be similar -> chunksize to single column

        hdf5_seq = hdf5_index["sequences"].create_group(seq)
        pileup_size = reference_positions_incr.size

        def create_dataset(name, data=None, shuffle=False, chunks=None):
            if compression_type is None:
                chunks = None
                shuffle = False
            else:
                chunks = list(chunks)
                if pileup_size:
                    chunks[0] = min(chunksize, pileup_size)
                chunks = tuple(chunks)
            hdf5_seq.create_dataset(
                name,
                data=data,
                chunks=chunks,
                shuffle=shuffle and compression_shuffle,
                compression=compression_type
            )

        create_dataset(
            "pileup_maxlikelihood_genotypes_diff",
            data=pileup_maxlikelihood_genotypes_diff,
            chunks=(chunksize,)
        )
        create_dataset(
            "pileup_allele_depth",
            data=pileup_allele_depth,
            chunks=(chunksize, 1)
        )
        create_dataset(
            "pileup_allele_rev_depth",
            data=pileup_allele_rev_depth,
            chunks=(chunksize, 1)
        )

        create_dataset(
            "reference_positions_incr",
            data=reference_positions_incr,
            chunks=(chunksize,)
        )

        _pileup_allelefreq_likelihoods = pileup_allelefreq_likelihoods
        if compression_half:
            _pileup_allelefreq_likelihoods = np.asarray(
                pileup_allelefreq_likelihoods,
                dtype=np.float16
            )
        create_dataset(
            "pileup_allelefreq_likelihoods",
            data=_pileup_allelefreq_likelihoods,
            shuffle=True,
            chunks=(chunksize, 1)
        )

    def build(
        self,
        fastapath,
        samfilepaths,
        sample_name,
        threads=1,
        mapq_downgrade=50,
        min_mapq=17,
        min_baseq=13,
        baq=True,
        compression_type=None,
        compression_shuffle=False,
        compression_half=False,
        chunksize=1000000
    ):
        """Build the index for the given SAM files.
        
        Args:
            fastapath (str): path to reference fasta
            samfilepaths (list): paths to SAM files that shall be indexed
            sample_name (str): the name of the sample (for referencing it in queries)
            threads (int): number of samtools threads
        """
        sub_buffersize = max(self.buffersize // threads, 1000)

        reference_sequences = read_fai(fastapath)

        if os.path.exists(self.hdf5path):
            os.remove(self.hdf5path)

        with h5py.File(self.hdf5path) as hdf5:
            self.init(hdf5, sample_name)
            hdf5_index = hdf5["alpaca_sample_index"]

            logging.info("importing {} as {}".format(", ".join(samfilepaths), sample_name))

            with ProcessPoolExecutor(max_workers=threads) as pool:
                # process pileups
                processed = 0

                for seq, length in reference_sequences:
                    logging.info("processing sequence {}".format(seq))
                    offsets = [
                        offset for offset in range(0, length, sub_buffersize)
                    ]

                    pileup_allelefreq_likelihoods = np.empty(
                        [length, self.ploidy + 1], dtype=np.float32
                    )
                    pileup_maxlikelihood_genotypes_diff = np.empty(
                        [length], dtype=np.int8
                    )
                    pileup_allele_depth = np.empty(
                        [length, ALLELE_COUNT], dtype=np.uint8
                    )
                    pileup_allele_rev_depth = np.empty_like(pileup_allele_depth)
                    reference_positions = np.empty(
                        [length], dtype=np.int32
                    )
                    effective_offset = 0

                    while offsets:
                        # use list in order to wait on all processes to be finished
                        for offset, pileup in list(zip(
                            offsets,
                            pool.map(
                                partial(
                                    calc_pileup,
                                    fastapath,
                                    samfilepaths,
                                    seq,
                                    sub_buffersize,
                                    mapq_downgrade=mapq_downgrade,
                                    min_mapq=min_mapq,
                                    min_baseq=min_baseq,
                                    baq=baq
                                ),
                                offsets[:threads]  # process as many offsets as threads
                            )
                        )):
                            if pileup is None:
                                continue
                            logging.debug("calculating likelihoods")
                            effective_offset = self.process_pileup(
                                pileup.pos,
                                pileup.address,
                                pileup.ref_alleles,
                                pileup.seqs,
                                pileup.quals,
                                pileup_allelefreq_likelihoods,
                                pileup_maxlikelihood_genotypes_diff,
                                pileup_allele_depth,
                                pileup_allele_rev_depth,
                                reference_positions,
                                effective_offset
                            )
                        # as many offsets as threads are processed
                        offsets = offsets[threads:]

                    # shrink buffers to effective length
                    pileup_allelefreq_likelihoods = pileup_allelefreq_likelihoods[:effective_offset]
                    pileup_maxlikelihood_genotypes_diff = pileup_maxlikelihood_genotypes_diff[:effective_offset]
                    pileup_allele_depth = pileup_allele_depth[:effective_offset]
                    pileup_allele_rev_depth = pileup_allele_rev_depth[:effective_offset]
                    reference_positions = reference_positions[:effective_offset]

                    reference_positions_incr = reference_positions.copy()
                    reference_positions_incr[1:] -= reference_positions[:-1]

                    # store data in HDF5
                    logging.debug("store sequence data")
                    self.store_seq(
                        hdf5_index,
                        seq,
                        pileup_allelefreq_likelihoods,
                        pileup_maxlikelihood_genotypes_diff,
                        pileup_allele_depth,
                        pileup_allele_rev_depth,
                        reference_positions_incr,
                        compression_type=compression_type,
                        compression_shuffle=compression_shuffle,
                        compression_half=compression_half,
                        chunksize=chunksize
                    )

    def process_pileup(
        self,
        pileup_pos,
        pileup_address,
        ref_alleles,
        seqs,
        quals,
        pileup_allelefreq_likelihoods,
        pileup_maxlikelihood_genotypes_diff,
        pileup_allele_depth,
        pileup_allele_rev_depth,
        reference_positions,
        effective_offset
    ):
        r"""Process buffered pileups.
        
        Let D_i be a single sample pileup at one position.
        pileup_genotype_likelihoods is calculated as :math:`P(D_i | g) = \sum_{c \in D_i} P(c | g)`.
        pileup_allelefreq_likelihoods is calculated as :math:`P(D_i | X = k) = \sum_{g \in G} P(D_i | g) P(g | X = k)`.
        
        Args:
            pos (np.ndarray): pileup positions
            seqs (np.ndarray): pileup bases
            quals (np.ndarray): pileup quals
            pileup_allelefreq_likelihoods (np.ndarray): array to store allele frequency likelihoods
            pileup_maxlikelihood_genotypes (np.ndarray): array to store maximum likelihood genotypes
            pileup_allele_depth (np.ndarray): array to store allele depths
            pileup_allele_rev_depth (np.ndarray): array to store reverse complement allele depths
            reference_positions (np.ndarray): array to store reference position for each site
            effective_offset (int): offset for storage in above arrays
        """
        quals -= self.qual_offset

        size = pileup_pos.size
        cl_pileup_address = self.to_device(pileup_address)
        cl_seqs = self.to_device(seqs)
        cl_quals = self.to_device(quals)
        cl_ref_alleles = self.to_device(ref_alleles)
        self.cl_bitencode_ref_alleles(cl_ref_alleles, self.cl_bitencode)

        # calculate genotype likelihoods
        cl_pileup_genotype_likelihoods = self.calc_pileup_genotype_likelihoods(
            cl_pileup_address,
            cl_seqs,
            cl_quals,
            seqs,
            quals,
            size
        )
        _pileup_maxlikelihood_genotypes_diff = self.calc_maxlikelihood_genotypes_diff(
            cl_pileup_genotype_likelihoods,
            cl_ref_alleles,
        )

        # calculate allele frequency likelihoods
        logging.debug("calculating allele frequency likelihoods")
        cl_genotype_alt_allelefreqs = self.calc_genotype_alt_allelefreqs(cl_ref_alleles)
        cl_pileup_allelefreq_likelihoods = self.calc_pileup_allelefreq_likelihoods(
            cl_pileup_address,
            cl_pileup_genotype_likelihoods,
            cl_genotype_alt_allelefreqs,
            size
        )

        # calculate pileup depths
        logging.debug("calculating pileup depths")
        cl_pileup_allele_depth, cl_pileup_allele_rev_depth = self.calc_pileup_allele_depths(
            cl_pileup_address,
            cl_seqs,
            size
        )

        start = effective_offset
        stop = start + pileup_pos.size

        cl_pileup_allelefreq_likelihoods.get(
            ary=pileup_allelefreq_likelihoods[start:stop, :]
        )
        pileup_maxlikelihood_genotypes_diff[start:stop] = _pileup_maxlikelihood_genotypes_diff
        cl_pileup_allele_depth.get(ary=pileup_allele_depth[start:stop, :])
        cl_pileup_allele_rev_depth.get(ary=pileup_allele_rev_depth[start:stop, :])
        reference_positions[start:stop] = pileup_pos
        logging.debug("pileups processed")
        return stop


    def calc_pileup_genotype_likelihoods(
        self,
        cl_pileup_address,
        cl_seqs,
        cl_quals,
        seqs,
        quals,
        size
    ):
        """Calculate genotype likelihoods.
        
        Args:
            cl_pileup_address (pyopencl.array.Array): array of pileup addresses
            cl_seqs (pyopencl.array.Array): array of piled up read bases
            cl_quals (pyopencl.array.Array): array of piled up qualities
            seqs (np.ndarray): array of piled up read bases
            quals (np.ndarray): array of piled up qualities
            size (int): how many pileups
        Returns:
            pyopencl array of genotype likelihoods
        """
        # select candidate bases
        #is_candidate = np.logical_and(seqs != ord(ALPHABET_INDEL_SHADOW), quals >= 17)
        is_candidate = seqs != ord(ALPHABET_INDEL_SHADOW)
        candidate_bases = np_index_true(is_candidate)
        cl_candidate_bases = self.to_device(candidate_bases)

        cl_pileup_genotype_likelihoods = self.empty(
            (size, self.genotypes_count),
            np.float32
        )

        cl_base_likelihoods = self.empty(cl_seqs.shape, dtype=np.float32)
        for genotype in np.arange(self.genotypes_count, dtype=np.int8):
            cl_base_likelihoods.fill(0)
            logging.debug("calculating base likelihoods")
            self.cl_calc_base_likelihoods(
                genotype,
                cl_candidate_bases,
                cl_seqs,
                cl_quals,
                self.cl_bitencode,
                self.cl_genotypes,
                self.cl_technology_miscall_prob,
                cl_base_likelihoods
            )
            logging.debug("calculating genotype likelihoods")
            self.cl_calc_pileup_genotype_likelihoods(
                genotype,
                cl_pileup_address,
                cl_base_likelihoods,
                cl_pileup_genotype_likelihoods,
                slice=np_slice[0:size]
            )
        return cl_pileup_genotype_likelihoods

    def calc_maxlikelihood_genotypes_diff(self, cl_pileup_genotype_likelihoods, cl_ref_alleles):
        """Calculate maximum likelihood genotypes.
        
        Args:
            cl_pileup_genotype_likelihoods (pyopencl.array.Array): array of genotype likelihoods
        Returns:
            numpy array of maximum likelihood genotypes
        """
        # TODO implement argmax in pyopencl
        maxlikelihood_genotypes = np.argmax(cl_pileup_genotype_likelihoods.get(), axis=1)
        maxlikelihood_genotypes -= cl_ref_alleles.get()
        return maxlikelihood_genotypes

    def calc_genotype_alt_allelefreqs(self, cl_ref_alleles):
        """Calculate genotype alternative allele frequencies.
        
        Args:
            cl_ref_alleles: reference alleles
        Returns:
            pyopencl array of genotype alternative allele frequencies
        """
        cl_genotype_alt_allelefreqs = self.empty(
            (cl_ref_alleles.size, self.genotypes_count),
            dtype=np.uint8
        )
        self.cl_calc_genotype_alt_allelefreqs(
            cl_ref_alleles,
            self.cl_genotypes,
            cl_genotype_alt_allelefreqs
        )
        return cl_genotype_alt_allelefreqs

    def calc_pileup_allelefreq_likelihoods(
        self,
        cl_pileup_address,
        cl_pileup_genotype_likelihoods,
        cl_genotype_alt_allelefreqs,
        size
    ):
        """Calculate allele frequency likelihoods.
        
        Args:
            cl_pileup_address: array of pileup addresses
            cl_pileup_genotype_likelihoods: the genotype likelihoods
            cl_genotype_alt_allelefreqs: the alternative allele frequencies
            size: how many pileups
        """
        cl_pileup_allelefreq_likelihoods = self.empty(
            (size, self.ploidy + 1), np.float32
        )
        cl_pileup_allelefreq_likelihoods.fill(MIN_FLOAT)

        self.cl_calc_pileup_allelefreq_likelihoods(
            cl_genotype_alt_allelefreqs,
            self.cl_genotype_allelefreq_probability,
            cl_pileup_genotype_likelihoods,
            cl_pileup_allelefreq_likelihoods,
            slice=np_slice[0:size]
        )
        return cl_pileup_allelefreq_likelihoods

    def calc_pileup_allele_depths(self, cl_pileup_address, cl_seqs, size):
        """Calculate allele depths.
        
        Args:
            cl_pileup_address: array of pileup addresses
            cl_seqs: array of piled up read bases
            size: how many pileups
        Returns:
            pyopencl array of allele depths and reverse complement depths
        """
        cl_pileup_allele_depth = self.zeros((size, ALLELE_COUNT), np.uint8)
        cl_pileup_allele_rev_depth = self.zeros_like(cl_pileup_allele_depth)

        self.cl_calc_pileup_allele_depths(
            cl_pileup_address,
            cl_seqs,
            self.cl_bitencode,
            cl_pileup_allele_depth,
            slice=np_slice[0:size]
        )
        self.cl_calc_pileup_allele_rev_depths(
            cl_pileup_address,
            cl_seqs,
            self.cl_bitencode,
            cl_pileup_allele_rev_depth,
            slice=np_slice[0:size]
        )
        return cl_pileup_allele_depth, cl_pileup_allele_rev_depth
