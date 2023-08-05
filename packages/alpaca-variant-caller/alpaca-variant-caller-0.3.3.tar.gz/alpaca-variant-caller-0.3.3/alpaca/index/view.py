import logging, time
from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple

import h5py
import numpy as np

from alpaca.index.utils import check_index, calc_genotype_ids, ALLELE_COUNT


__author__ = "Johannes Köster"


class IndexView:
    def __init__(self, hdf5path, buffersize=10000):
        check_index(hdf5path, "alpaca_index")
        self.hdf5 = h5py.File(hdf5path)
        self.hdf5_index = self.hdf5["alpaca_index"]
        self.buffersize = buffersize
        self.ploidy = self.hdf5_index.attrs["ploidy"]
        self.samples = self.hdf5_index["samples"].value

        self._len = sum(seq["reference_positions"].size for seq in self.hdf5_index["sequences"].values())

    def get(self, samples):
        for reference_name in self.hdf5_index["sequences"]:
            yield IndexSeqView(self, reference_name, samples)

    def __len__(self):
        return self._len


class IndexLocusView(IndexView):
    def __init__(self, hdf5path, locus, buffersize=10000):
        super().__init__(hdf5path, buffersize=buffersize)
        try:
            self.reference_name, pos = locus.split(":")
            self.pos = int(pos) - 1
        except ValueError:
            raise AlpacaError("Locus must be of the form chrom:pos.")
        self._len = 1

    def get(self, samples):
        yield IndexSeqLocusView(
            self, self.reference_name, self.pos, samples
        )


class IndexSeqView:
    def __init__(self, index_view, reference_name, samples):
        self.buffersize = index_view.buffersize
        self.ploidy = index_view.ploidy
        self.hdf5_seq = index_view.hdf5_index["sequences"][reference_name]
        self.samples = samples
        self.reference_name = reference_name
        self._len = self.hdf5_seq["reference_positions"].size

    def __iter__(self):
        for i in range(0, len(self), self.buffersize):
            yield self[i:i + self.buffersize]

    def __getitem__(self, slice):
        try:
            start = slice.start
            stop = slice.stop
        except AttributeError:
            start = slice
            stop = start + 1
        return IndexSeqSlice(self.hdf5_seq, start, stop, self.ploidy, self.samples, self.reference_name)

    def __len__(self):
        return self._len


class IndexSeqLocusView(IndexSeqView):
    def __init__(self, index_view, reference_name, pos, samples):
        super().__init__(index_view, reference_name, samples)
        self.pos = pos

    def __iter__(self):
        for seq_slice in super().__iter__():
            refpos = seq_slice.reference_positions
            i = np.searchsorted(refpos, self.pos)
            if refpos[i] == self.pos:
                yield self[i]


class IndexSeqSlice:
    def __init__(self, hdf5_seq, start, stop, ploidy, samples, reference_name):
        self.hdf5_seq = hdf5_seq
        self.ploidy = ploidy
        self.start = start
        self.stop = min(stop, self.hdf5_seq["reference_positions"].size)
        self.samples = samples
        self.reference_name = reference_name
        self.sample_count = len(samples)

    @property
    def reference_positions(self):
        return self.hdf5_seq["reference_positions"][self.start:self.stop]

    @property
    def reference_genotypes(self):
        return self.hdf5_seq["reference_genotypes"][self.start:self.stop]

    @property
    def pileup_allelefreq_likelihoods(self):
        return self.read_pileup_data(
            self.hdf5_seq["pileup_allelefreq_likelihoods"],
            dtype=np.float32  # ensure that floats are casted to float32
        )

    @property
    def pileup_maxlikelihood_genotypes(self):
        return self.read_pileup_data(
            self.hdf5_seq["pileup_maxlikelihood_genotypes"]
        )

    @property
    def pileup_allele_depth(self):
        return self.read_pileup_data(self.hdf5_seq["pileup_allele_depth"])

    @property
    def pileup_allele_rev_depth(self):
        return self.read_pileup_data(self.hdf5_seq["pileup_allele_rev_depth"])

    @property
    def pileup_read_depth(self):
        return np.sum(self.pileup_allele_depth, axis=2)

    @property
    def candidate_sites(self):
        return np.arange(len(self), dtype=np.int32)

    def read_pileup_data(self, hdf5_group, dtype=None):
        sample_data = hdf5_group[self.samples[0]]

        shape = [len(self.samples)]
        shape.extend(sample_data.shape)
        shape[1] = len(self)

        data = np.empty(shape, dtype=sample_data.dtype if dtype is None else dtype)

        for i, sample in enumerate(self.samples):
            hdf5_group[sample].read_direct(
                data,
                source_sel=np.s_[self.start:self.stop],
                dest_sel=np.s_[i]
            )
        return data

    def __len__(self):
        return self.stop - self.start


class SampleIndexView:
    def __init__(self, hdf5path, buffersize=10000):
        check_index(hdf5path, "alpaca_sample_index")
        self.hdf5 = h5py.File(hdf5path)
        self.hdf5_index = self.hdf5["alpaca_sample_index"]
        self.buffersize = buffersize
        self.ploidy = self.hdf5_index.attrs["ploidy"]
        self.sample = self.hdf5_index.attrs["sample"]

    @property
    def sequence_names(self):
        return list(self.hdf5_index["sequences"])

    def __getitem__(self, reference_name):
        return SampleIndexSeqView(self.hdf5_index, reference_name, self.buffersize, self.ploidy)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.hdf5.close()


class SampleIndexSeqView:
    def __init__(self, hdf5_index, reference_name, buffersize, ploidy):
        self.buffersize = buffersize
        self.hdf5_seq = hdf5_index["sequences"][reference_name]
        self.ploidy = ploidy

    def __getitem__(self, slice):
        if isinstance(slice, list) or isinstance(slice, np.ndarray):
            sites = slice
            return SampleIndexSeqItems(self.hdf5_seq, sites, self.ploidy)
        start, stop = slice
        return SampleIndexSeqSlice(self.hdf5_seq, start, stop, self.ploidy)

    def __iter__(self):
        for i in range(0, len(self), self.buffersize):
            yield self[i, i + self.buffersize]

    def __len__(self):
        return self.hdf5_seq["reference_positions_incr"].size


class SampleIndexSeqSlice:
    def __init__(self, hdf5_seq, start, stop, ploidy):
        self.hdf5_seq = hdf5_seq
        self.ploidy = ploidy
        self.start = start
        size = self.hdf5_seq["reference_positions_incr"].size
        self.stop = min(stop, size)
        self._len = self.stop - start

    @property
    def reference_positions_incr(self):
        return self.hdf5_seq["reference_positions_incr"][self.start:self.stop]

    @property
    def pileup_allelefreq_likelihoods(self):
        # convert to float32
        return np.asanyarray(
            self.hdf5_seq["pileup_allelefreq_likelihoods"][self.start:self.stop, :],
            dtype=np.float32
        )

    @property
    def pileup_maxlikelihood_genotypes_diff(self):
        return self.hdf5_seq["pileup_maxlikelihood_genotypes_diff"][self.start:self.stop]

    @property
    def pileup_allele_depth(self):
        return self.hdf5_seq["pileup_allele_depth"][self.start:self.stop, :]

    @property
    def pileup_allele_rev_depth(self):
        return self.hdf5_seq["pileup_allele_rev_depth"][self.start:self.stop, :]

    @property
    def peek(self):
        peek_data = np.empty((len(self), 3 + ALLELE_COUNT * 2), dtype=np.int32)
        self.hdf5_seq["reference_positions_incr"].read_direct(peek_data, source_sel=np.s_[self.start:self.stop], dest_sel=np.s_[:,0])
        self.hdf5_seq["pileup_allele_depth"].read_direct(peek_data, source_sel=np.s_[self.start:self.stop, :], dest_sel=np.s_[:, 2:2 + ALLELE_COUNT])
        self.hdf5_seq["pileup_allele_rev_depth"].read_direct(peek_data, source_sel=np.s_[self.start:self.stop, :], dest_sel=np.s_[:, 2 + ALLELE_COUNT:2 + ALLELE_COUNT * 2])

        # calculate allele depths
        pileup_allele_depth = peek_data[:, 2:8]
        pileup_allele_rev_depth = peek_data[:, 8:14]
        peek_data[:, 1] = np.sum(pileup_allele_depth, axis=1)
        pileup_allele_depth -= pileup_allele_rev_depth

        # calculate reference_positions
        reference_positions = peek_data[:, 0]
        np.cumsum(reference_positions, out=reference_positions)

        return peek_data

#    @property
#    def peek(self):
#        pileup_allele_depth = self.pileup_allele_depth
#        pileup_allele_rev_depth = self.pileup_allele_rev_depth
#        depth = np.sum(pileup_allele_depth, axis=1)

#        pileup_allele_depth -= pileup_allele_rev_depth
#        return np.hstack((
#            self.reference_positions,
#            depth,
#            pileup_allele_depth,
#            pileup_allele_rev_depth
#        ))

    def __len__(self):
        return self._len


def double_buffer(seq_view, *attributes):
    SeqSliceBuffer = namedtuple("SeqSliceBuffer", attributes)

    def read_data(seq_slice):
        seq_slice.buffer = SeqSliceBuffer(
            **{attr: getattr(seq_slice, attr) for attr in attributes}
        )
        return seq_slice

    with ThreadPoolExecutor(max_workers=1) as pool:
        # once the first buffer is yielded, the second is loaded concurrently
        yield from pool.map(read_data, seq_view)
