
import csv
import sys
import logging
import time
from itertools import groupby
from operator import itemgetter

import numpy as np
import pyopencl as cl
from pyopencl.elementwise import ElementwiseKernel
import pyopencl.algorithm as clalg
import pyopencl.array as clarray

from alpaca.utils import CLAlgorithm, mergesorted
from alpaca.index.view import SampleIndexView, double_buffer
from alpaca.index.utils import ALLELE_COUNT


class Peek(CLAlgorithm):

    def __init__(self, cl_queue, cl_mem_pool, hdf5path):
        super().__init__(cl_queue, cl_mem_pool)
        self.hdf5path = hdf5path

        self.cl_calc_is_candidate = ElementwiseKernel(
            self.cl_queue.context,
            "const int min_pos, "
            "const int* pos, "
            "char* is_candidate",
            """
            is_candidate[pos[i] - min_pos] = true;
            """
        )

        self.cl_calc_candidate_sites = ElementwiseKernel(
            self.cl_queue.context,
            "const int min_pos, "
            "const int max_pos, "
            "const int* reference_positions, "
            "char* is_candidate, "
            "int* candidate_sites",
            r"""
            const int pos = reference_positions[i];

            int site = -1;
            if(pos >= min_pos && pos <= max_pos) {
                if(is_candidate[pos - min_pos]) {
                    is_candidate[pos - min_pos] = false;  // remove candidate
                    site = i;
                }
            }
            candidate_sites[i] = site;
            """
        )

    def peek(self, loci, likelihoods=False, buffersize=1000000):
        fmt_depth = lambda depth: "\t".join(map("{}".format, depth))

        sample_index = SampleIndexView(self.hdf5path, buffersize=buffersize)

        if likelihoods:
            header = ["M={}".format(m).encode() for m in range(sample_index.ploidy + 1)]
        else:
            header = b"chrom pos depth A C G T N INDEL a c g t n indel".split()
        sys.stdout.buffer.write(b"\t".join(header) + b"\n")

        for seq_name, loci in groupby(loci, key=itemgetter(0)):
            logging.info("processing sequence {}".format(seq_name))
            self.cl_mem_pool.free_held()

            if likelihoods:
                fmt = ["%f"] * len(header)
            else:
                fmt = ["{}\t%i".format(seq_name)] + ["%i"] * (len(header) - 1)

            positions = np.array(
                [locus[1] - 1 for locus in loci],
                dtype=np.int32
            )
            min_pos = np.int32(positions[0])
            max_pos = np.int32(positions[-1])
            cl_positions = self.to_device(positions, async=True)

            logging.debug("calculating candidate index")
            cl_is_candidate = self.zeros(max_pos + 1 - min_pos, dtype=np.int8)
            self.cl_calc_is_candidate(
                min_pos,
                cl_positions,
                cl_is_candidate
            )

            seq_index = sample_index[seq_name]
            slice_max_pos = 0
            for seq_slice in double_buffer(
                seq_index,
                "reference_positions_incr",
                "pileup_allelefreq_likelihoods" if likelihoods else "peek"
            ):
                # obtain reference positions from increments
                cl_reference_positions = self.to_device(
                    seq_slice.buffer.reference_positions_incr,
                    async=True
                )
                refpos_offset = slice_max_pos

                # add last position
                cl_reference_positions[0] += refpos_offset
                # restore absolute reference positions
                cl_reference_positions = clarray.cumsum(cl_reference_positions)

                slice_min_pos = cl_reference_positions[0].get().item()
                slice_max_pos = cl_reference_positions[-1].get().item()
                logging.debug("processing slice {} - {}".format(slice_min_pos, slice_max_pos))
                if slice_max_pos < min_pos:
                    continue
                if slice_min_pos > max_pos:
                    break

                # find candidate sites from reference positions and the is_candidate array
                cl_candidate_sites = self.empty_like(cl_reference_positions)
                self.cl_calc_candidate_sites(
                    min_pos,
                    max_pos,
                    cl_reference_positions,
                    cl_is_candidate,
                    cl_candidate_sites
                )
                cl_candidate_sites, clcount, _ = clalg.copy_if(
                    cl_candidate_sites, "ary[i] >= 0"
                )
                candidate_sites = cl_candidate_sites[:clcount.get().item()].get()

                # get data for candidate sites
                if likelihoods:
                    peek_data = seq_slice.buffer.pileup_allelefreq_likelihoods[candidate_sites]
                else:
                    peek_data = seq_slice.buffer.peek[candidate_sites]
                    # calc reference positions from increment
                    peek_data[:, 0] += refpos_offset
                    peek_data[:, 0] = np.cumsum(peek_data[:, 0])

                # get not covered sites
                min_candidate_addr = max(slice_min_pos - min_pos, 0)
                not_covered = cl_is_candidate[
                    min_candidate_addr:slice_max_pos + 1 - min_pos
                ].get()
                not_covered_positions = np.nonzero(not_covered)[0] + min_candidate_addr + min_pos

                # merge positions of both
                peek_data_dest, not_covered_dest = mergesorted(peek_data[:, 0], not_covered_positions)
                merged_data = np.zeros(
                    (peek_data.shape[0] + not_covered_positions.size, peek_data.shape[1]),
                    dtype=np.float32 if likelihoods else np.int32
                )

                if merged_data.size:
                    merged_data[peek_data_dest] = peek_data
                    merged_data[not_covered_dest, 0] = not_covered_positions

                    # increase position to output 1-based
                    merged_data[:, 0] += 1
                    logging.debug("printing candidate sites")
                    np.savetxt(
                        sys.stdout.buffer,
                        merged_data,
                        fmt=fmt,
                        delimiter="\t"
                    )
