
"""
Common utilities.
"""

__author__ = "Johannes Köster"
__license__ = "MIT"


import math
import os
import logging
from itertools import combinations_with_replacement, permutations

import numpy as np
import h5py

from alpaca.utils import is_higher_version, comb_with_repl
from alpaca.index.version import __version__
from alpaca.utils import AlpacaError


H5PY_STR_DTYPE = h5py.special_dtype(vlen=str)


ALPHABET = b"ACGT"
ALPHABET_N = b"N"
ALPHABET_INDEL_SHADOW = b"*"
N_BITENCODED = b"\x04"
INDEL_SHADOW_BITENCODED = b"\x05"
ALPHABET_BITENCODED = b"\x00\x01\x02\x03"
ALPHABET_MIN_REVCOMP = ord("a")
ALPHABET_IUPAC = b"RYSWKMBDHV"  # translate this to N in bitencoding


BITENCODE_TRANSLATION_TABLE = bytes.maketrans(
    (
        ALPHABET + ALPHABET_N + (ALPHABET + ALPHABET_N).lower() +
        ALPHABET_INDEL_SHADOW + ALPHABET_IUPAC + ALPHABET_IUPAC.lower()
    ), 
    (
        (ALPHABET_BITENCODED + N_BITENCODED) * 2 +
        INDEL_SHADOW_BITENCODED + N_BITENCODED * len(ALPHABET_IUPAC) * 2
    )
)


BITENCODE = np.fromstring(
    BITENCODE_TRANSLATION_TABLE,
    dtype=np.uint8
)


BITDECODE = np.fromstring(
    bytes.maketrans(ALPHABET_BITENCODED + N_BITENCODED, ALPHABET + b"N"),
    dtype=np.uint8
)


ALLELE_COUNT = 6 # ACGT, N and indel
INDEL_ALLELE = 5


def restore_alphabet(bitencoded, get_bytes=np.vectorize(chr)):
    """Restore original alphabet from bit-encoded sequence.
    
    Args:
        bitencoded: bit-encoded sequence
    Returns:
        sequence in plain text
    """
    return get_bytes(BITDECODE[bitencoded])


# Technology specific confusion matrix (row: true allele, column: called base)
TECHNOLOGY_MISCALL_PROB = dict(
    illumina=np.log(
        np.array(
            [
                [1, 0.58, 0.17, 0.25],
                [0.35, 1, 0.11, 0.54],
                [0.32, 0.05, 1, 0.63],
                [0.46, 0.22, 0.32, 1]
            ],
            dtype=np.float32
        )
    )
)


def check_index(hdf5path, prefix):
    """Check if the given index is of the expected format.
    
    Args:
        hdf5path (h5py.File): an HDF5 file
        prefix: prefix to check
    """
    with h5py.File(hdf5path) as hdf5:
        if not prefix in hdf5 or not "version" in hdf5[prefix].attrs:
            raise IOError(
                "Given hdf5 file {} is not a valid alpaca index.".format(
                    hdf5path
                )
            )
        hdf5_version = hdf5[prefix].attrs["version"]
        if is_higher_version(__version__, hdf5_version):
            raise IOError(
                "The alpaca index {} is outdated (version {}, need {}). "
                "Please create a new one for this version of alpaca.".format(
                    hdf5path,
                    hdf5_version, __version__
                )
            )
        elif is_higher_version(hdf5_version, __version__):
            raise IOError(
                "The alpaca index {} is too new (version {}, need {}). "
                "Please create a new one for this version of alpaca.".format(
                    hdf5path,
                    hdf5_version, __version__
                )
            )


def calc_min_bits(min_value, max_value):
    """Calculates the needed bits for values in the given range."""
    return math.ceil(math.log(max_value - min_value + 1, 2))


def is_homozygous(genotype):
    """ Return True if genotype is homozygous """
    return genotype == genotype[0:1] * len(genotype)


def calc_genotypes(ploidy):
    """ Calculate all possible genotypes given a ploidy. """
    return np.array(
        sorted(
            combinations_with_replacement(ALPHABET_BITENCODED, ploidy),
            key=is_homozygous,
            reverse=True
        ),
        dtype=np.uint8
    )


def calc_genotype_ids(genotypes, ploidy):
    """Calculate a matrix to look up genotype ids.

    The matrix has as many dimensions as ploidy and contains an entry for each
    combination of alleles.
    """
    genotype_ids = np.empty([4] * ploidy, dtype=np.int8)
    for i, gt in enumerate(genotypes):
        for alleles in permutations(gt):
            genotype_ids[alleles] = i
    return genotype_ids


def calc_genotype_allelefreq_probability(ploidy):
    r""" Calculate probability of genotype given an alt allele frequency.
    
    Assuming a uniform distribution of genotypes, the probability of observing 
    genotype g given alt allele frequency a is
    P(g | X = k) = \binom{3 + k - 1}{k}^{-1} 
    if k is the alt allele frequency of g. Else, the probability is 0,
    but we omit this case here.
    I.e. 1 / (the number of possible genotypes with alt allele frequences a).
    The nominator is the number of combinations with replacement when choosing a 
    alternative alleles from 3 possible alternative allele.
    
    Args:
        ploidy (int): the ploidy

    Returns:
        np.ndarray: the log probabilities for each alt allele frequency
    """
    # probability to sample genotype g given alt_allelefreq is
    # 1 / comb_with_repl(3, alt_allelefreq) (assuming uniform distribution)
    # one base is reference, hence there are 3 to choose from
    n = 3
    probs = np.array(
        [comb_with_repl(n, a) for a in range(ploidy + 1)],
        dtype=np.float32
    )
    # calculate log(1 / probs) = log(1) - log(probs) = -log(probs)
    return -np.log(probs)


def read_fasta(fastapath, prefix=b">"):
    if fastapath.endswith(".gz"):
        openfasta = io.BufferedReader(gzip.open(fastapath, "rb"))
    else:
        openfasta = open(fastapath, "rb")

    with openfasta as fasta:
        name = None
        seq = bytearray()
        for l in fasta:
            if l.startswith(prefix):
                if name is not None:
                    yield name, np.asarray(seq, dtype=np.uint8)
                    seq = bytearray()
                name = l[1:-1].split(b" ", 1)[0].decode()
            else:
                seq.extend(l[:-1])
        if seq and name:
            yield name, np.asarray(seq, dtype=np.uint8)


def read_fai(fastapath):
    faipath = fastapath + ".fai"
    if not os.path.exists(faipath):
        raise AlpacaError(
            "The fasta reference must be indexed with samtools faidx."
        )
    with open(faipath) as fai:
        for l in fai:
            name, length, _ = l.split("\t", 2)
            yield name, int(length)
