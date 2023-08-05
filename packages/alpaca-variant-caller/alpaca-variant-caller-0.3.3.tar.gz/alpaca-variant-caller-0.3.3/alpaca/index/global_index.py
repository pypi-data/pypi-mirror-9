
"""
Merge per sample indexes into one global index.
"""

__author__ = "Johannes Köster"
__license__ = "MIT"

import logging
import os

import numpy as np
import h5py
import pyopencl.array as clarray
import pyopencl.algorithm as clalg
from pyopencl.elementwise import ElementwiseKernel
from pyopencl.scan import ExclusiveScanKernel
from pyopencl.tools import dtype_to_ctype
from mako.template import Template

from alpaca.utils import CLAlgorithm
from alpaca.index.utils import (
    calc_genotypes, BITENCODE, H5PY_STR_DTYPE, read_fai,
    read_fasta, ALLELE_COUNT
)
from alpaca.index.view import SampleIndexView, double_buffer
from alpaca.index.version import __version__


class GlobalIndex(CLAlgorithm):

    def __init__(
        self,
        cl_queue,
        cl_mem_pool,
        hdf5path,
        ploidy=2
    ):
        """Constructor initializes kernels and other stuff.
        
        Args:
            cl_queue: an OpenCL queue
            cl_mem_pool: an OpenCL memory pool
            hdf5path: path to HDF5 file for storing the index
            ploidy: expected ploidy
        """
        super().__init__(cl_queue, cl_mem_pool)

        self.hdf5path = hdf5path

        self.ploidy = ploidy
        self.cl_bitencode = self.to_device(BITENCODE)
        self.cl_genotypes = self.to_device(calc_genotypes(ploidy))

        self.preamble = Template(
            """
            #define PLOIDY ${ploidy}
            #define GENOTYPE(g, a)    genotypes[g * ${ploidy} + a]
            """
        ).render(ploidy=ploidy)

        self.cl_calc_candidate_sites = ElementwiseKernel(
            self.cl_queue.context,
            "const int* reference_positions, "
            "const char* pileup_maxlikelihood_genotypes_diff, "
            "char* is_candidate",
            """
            const int site = reference_positions[i];
            is_candidate[site] |= pileup_maxlikelihood_genotypes_diff[i] != 0;
            """,
            preamble=self.preamble,
            name="calc_candidate_sites"
        )

        self.cl_calc_candidate_positions = ElementwiseKernel(
            self.cl_queue.context,
            "const char* is_candidate, "
            "const int* candidate_addr, "
            "int* candidate_positions",
            """
            if(is_candidate[i])
            {
                candidate_positions[candidate_addr[i]] = i;
            }
            """,
            name="calc_candidate_positions"
        )

        self.cl_calc_reference_genotypes = ElementwiseKernel(
            self.cl_queue.context,
            "const int* candidate_positions, "
            "const char* reference_alleles, "
            "const char* genotypes, "
            "const char* bitencode, "
            "char* reference_genotypes",
            """
            const int site = candidate_positions[i];
            const char ref_allele = bitencode[reference_alleles[site]];
            reference_genotypes[i] = ref_allele;
            """,
            preamble=self.preamble,
            name="calc_reference_genotypes"
        )

        self.cl_calc_candidate_addr = ExclusiveScanKernel(
            self.cl_queue.context,
            np.int32, "a+b", "0"
        )

    def get_store_sample_kernel(self, dtype, shape, assign="="):
        assert len(shape) <= 2
        return ElementwiseKernel(
            self.cl_queue.context,
            "const int offset, "
            "const int* reference_positions, "
            "const char* is_candidate, "
            "const int* candidate_addr, "
            "const {ctype}* src, "
            "{ctype}* dest".format(ctype=dtype_to_ctype(dtype)),
            Template(
                """
                const int site = reference_positions[i];
                if(!is_candidate[site])
                    PYOPENCL_ELWISE_CONTINUE;
                const int target = candidate_addr[site] - offset;
                % if len(shape) == 2:
                    % for k in range(shape[1]):
                        dest[target * ${shape[1]} + ${k}] ${assign} src[i * ${shape[1]} + ${k}];
                    % endfor
                % else:
                    dest[target] ${assign} src[i];
                % endif
                """
            ).render(shape=shape, assign=assign)
        )

    def build(self, fastapath, *sample_index_paths, buffersize=10000000):
        """Build the merged index.
        
        Args:
            fastapath: path to reference fasta file
            sample_index_paths: paths to per-sample indexes that shall be merged
            buffersize: the buffer size
        """

        if os.path.exists(self.hdf5path):
            os.remove(self.hdf5path)

        # determine reference sequence names and lengths
        reference_sequences = read_fai(fastapath)
        sample_count = len(sample_index_paths)

        def get_sample_names():
            for f in sample_index_paths:
                with SampleIndexView(f) as sample_index:
                    yield sample_index.sample
        sample_names = np.array(
            list(get_sample_names()),
            dtype=object
        )

        # sort samples lexicographically
        idx = np.argsort(sample_names)
        sample_names = sample_names[idx]
        sample_index_paths = [sample_index_paths[i] for i in idx]

        with h5py.File(self.hdf5path) as hdf5:
            # store metadata
            hdf5_index = hdf5.create_group("alpaca_index")
            hdf5_index.attrs["ploidy"] = self.ploidy
            hdf5_index.attrs["version"] = __version__
            hdf5_index.create_dataset(
                "samples",
                dtype=H5PY_STR_DTYPE,
                data=sample_names
            )
            hdf5_index.create_group("sequences")

        for seq_name, seq in read_fasta(fastapath):
            logging.info("processing sequence {}".format(seq_name))
            with h5py.File(self.hdf5path) as hdf5:
                hdf5_index = hdf5["alpaca_index"]

                hdf5_seq = hdf5_index["sequences"].create_group(seq_name)
                self.cl_mem_pool.free_held()

                # determine candidate positions
                cl_is_candidate = self.zeros(len(seq), dtype=np.uint8)
                for f in sample_index_paths:
                    with SampleIndexView(f, buffersize=buffersize) as sample_index:
                        offset = 0
                        for sample_slice in double_buffer(
                            sample_index[seq_name],
                            "reference_positions_incr",
                            "pileup_maxlikelihood_genotypes_diff"
                        ):
                            cl_reference_positions = self.get_sample_reference_positions(
                                sample_slice.buffer, offset=offset
                            )
                            self.calc_candidate_sites(
                                sample_slice.buffer,
                                cl_reference_positions,
                                cl_is_candidate
                            )
                            offset = cl_reference_positions[-1].get().item()

                # count candidates
                candidate_count = clarray.sum(
                    cl_is_candidate, dtype=np.int32
                ).get().item()

                # the target position of each candidate determined by a prescan
                cl_candidate_addr = self.calc_candidate_addr(cl_is_candidate)

                # store reference information
                cl_reference_positions = self.calc_reference_positions(
                    candidate_count, cl_is_candidate, cl_candidate_addr
                )
                cl_reference_genotypes = self.calc_reference_genotypes(
                    candidate_count, cl_reference_positions, seq
                )
                hdf5_seq.create_dataset(
                    "reference_positions",
                    data=cl_reference_positions.get()
                )
                hdf5_seq.create_dataset(
                    "reference_genotypes",
                    data=cl_reference_genotypes.get()
                )

                # init other merged data structures
                for group in [
                    "pileup_allelefreq_likelihoods",
                    "pileup_maxlikelihood_genotypes",
                    "pileup_allele_depth",
                    "pileup_allele_rev_depth"
                ]:
                    hdf5_seq.create_group(group)
                for sample_name in sample_names:
                    hdf5_seq["pileup_allelefreq_likelihoods"].create_dataset(
                        sample_name,
                        [candidate_count, self.ploidy + 1],
                        dtype=np.float32
                    )
                    hdf5_seq["pileup_maxlikelihood_genotypes"].create_dataset(
                        sample_name,
                        [candidate_count],
                        dtype=np.int8
                    )
                    hdf5_seq["pileup_allele_depth"].create_dataset(
                        sample_name,
                        [candidate_count, ALLELE_COUNT],
                        dtype=np.uint8
                    )
                    hdf5_seq["pileup_allele_rev_depth"].create_dataset(
                        sample_name,
                        [candidate_count, ALLELE_COUNT],
                        dtype=np.uint8
                    )

                # store candidates in global index
                for sample_name, f in zip(sample_names, sample_index_paths):
                    with SampleIndexView(f, buffersize=buffersize) as sample_index:
                        logging.info("storing sample {}".format(sample_index.sample))
                        start = 0
                        sample_ref_stop = 0
                        for sample_slice in double_buffer(
                            sample_index[seq_name],
                            "pileup_allelefreq_likelihoods",
                            "pileup_maxlikelihood_genotypes_diff",
                            "pileup_allele_depth",
                            "pileup_allele_rev_depth",
                            "reference_positions_incr"
                        ):
                            cl_reference_positions = self.get_sample_reference_positions(sample_slice.buffer, offset=sample_ref_stop)

                            sample_ref_start = cl_reference_positions[0].get().item()
                            sample_ref_stop = cl_reference_positions[-1].get().item()
                            stop = cl_candidate_addr[sample_ref_stop].get().item()
                            # increase stop limit by one if last position was a candidate
                            stop += cl_is_candidate[sample_ref_stop].get().item()

                            if stop == start:
                                # no candidate found
                                continue

                            def store_sample_data(src, cl_init=None, assign="="):
                                cl_src = self.to_device(src, async=True)
                                if cl_init is None:
                                    cl_dest = self.zeros(
                                        [stop - start] + list(src.shape[1:]),
                                        dtype=src.dtype
                                    )
                                else:
                                    cl_dest = cl_init.copy()
                                knl = self.get_store_sample_kernel(
                                    src.dtype, src.shape, assign=assign
                                )
                                knl(
                                    np.int32(start),
                                    cl_reference_positions,
                                    cl_is_candidate,
                                    cl_candidate_addr,
                                    cl_src,
                                    cl_dest
                                )
                                return cl_dest

                            logging.debug("storing likelihoods")
                            cl_pileup_allelefreq_likelihoods = store_sample_data(
                                np.asanyarray(
                                    sample_slice.buffer.pileup_allelefreq_likelihoods,
                                    dtype=np.float32
                                )
                            )
                            logging.debug("storing genotypes")
                            #import pdb; pdb.set_trace()
                            #logging.debug(cl_reference_positions.get()[499310:499315])
                            #logging.debug(cl_is_candidate.get()[8000000-10:8000010])
                            #logging.debug(cl_candidate_addr.get()[8000000-10:8000010])
                            #logging.debug(cl_reference_genotypes[start:stop].get().max())
                            cl_pileup_maxlikelihood_genotypes = store_sample_data(
                                sample_slice.buffer.pileup_maxlikelihood_genotypes_diff,
                                cl_init=cl_reference_genotypes[start:stop],
                                assign="+="
                            )
                            logging.debug("storing allele depths")
                            cl_pileup_allele_depth = store_sample_data(
                                sample_slice.buffer.pileup_allele_depth
                            )
                            cl_pileup_allele_rev_depth = store_sample_data(
                                sample_slice.buffer.pileup_allele_rev_depth
                            )

                            if False and not np.all(cl_pileup_maxlikelihood_genotypes.get() < 10):
                                k = np.argmax(cl_pileup_maxlikelihood_genotypes.get())
                                #i = np.searchsorted(cl_candidate_addr.get(), k + start)
                                #v = sample_slice.buffer.pileup_allelefreq_likelihoods[[i for i, v in enumerate(cl_candidate_addr.get()) if v - start == k][0] - start]
                                logging.debug((cl_reference_genotypes.get()[k], cl_pileup_maxlikelihood_genotypes.get()[k], k, self.cl_genotypes.size))
                                exit(1)

                            hdf5_seq[
                                "pileup_allelefreq_likelihoods"
                            ][sample_name][start:stop] = cl_pileup_allelefreq_likelihoods.get()
                            hdf5_seq[
                                "pileup_maxlikelihood_genotypes"
                            ][sample_name][start:stop] = cl_pileup_maxlikelihood_genotypes.get()
                            hdf5_seq[
                                "pileup_allele_depth"
                            ][sample_name][start:stop] = cl_pileup_allele_depth.get()
                            hdf5_seq[
                                "pileup_allele_rev_depth"
                            ][sample_name][start:stop] = cl_pileup_allele_rev_depth.get()

                            start = stop

    def get_sample_reference_positions(self, sample_slice, offset=None):
        cl_reference_positions = self.to_device(
            sample_slice.reference_positions_incr, async=True
        )
        cl_reference_positions[0] += np.int32(offset)
        cl_reference_positions = clarray.cumsum(cl_reference_positions)
        return cl_reference_positions

    def calc_reference_positions(
        self,
        candidate_count,
        cl_is_candidate,
        cl_candidate_addr,
    ):
        """Calculate the reference positions for given candidates.
        
        Args:
            candidate_count: number of candidates
            cl_is_candidate: whether a site is a candidate
            cl_candidate_addr: address of the candidate
        Returns:
            reference positions
        """
        cl_reference_positions = self.empty(
            [candidate_count],
            dtype=np.int32
        )
        self.cl_calc_candidate_positions(
            cl_is_candidate, cl_candidate_addr, cl_reference_positions
        )
        return cl_reference_positions

    def calc_reference_genotypes(
        self,
        candidate_count,
        cl_reference_positions,
        seq,
    ):
        """Calculate the reference genotypes for given candidates.
        
        Args:
            cl_reference_positions: candidate reference positions
            seq: reference sequence
        Returns:
            reference genotypes
        """
        cl_reference_seq = self.to_device(seq, async=True)
        cl_reference_genotypes = self.empty([candidate_count], dtype=np.int8)
        self.cl_calc_reference_genotypes(
            cl_reference_positions,
            cl_reference_seq,
            self.cl_genotypes,
            self.cl_bitencode,
            cl_reference_genotypes
        )
        return cl_reference_genotypes

    def calc_candidate_sites(self, sample_slice, cl_reference_positions, cl_is_candidate):
        """Calculate candidate sites.
        
        Args:
            sample_slices: sample slices
        """

        cl_pileup_maxlikelihood_genotypes_diff = self.to_device(
            sample_slice.pileup_maxlikelihood_genotypes_diff, async=True
        )

        self.cl_calc_candidate_sites(
            cl_reference_positions,
            cl_pileup_maxlikelihood_genotypes_diff,
            cl_is_candidate
        )

    def calc_candidate_addr(self, cl_is_candidate):
        """Calculate candidate site addresses.
        
        Args:
            cl_is_candidate: array telling whether a site is a candidate
        Returns:
            the address of each candidate
        """
        cl_candidate_addr = cl_is_candidate.astype(np.int32)
        self.cl_calc_candidate_addr(cl_candidate_addr)
        return cl_candidate_addr
