import multiprocessing
import re
import io
import logging
import subprocess
from itertools import islice
from functools import partial
from collections import namedtuple
from operator import itemgetter

import numpy as np
from mako.template import Template

from alpaca.utils import AlpacaError
from alpaca.index.utils import ALPHABET, ALPHABET_N, ALPHABET_IUPAC


Pileup = namedtuple("Pileup", "pos ref_alleles address seqs quals")


def parse_pileup(
    pileup,
    indel_re_sub=re.compile(b"[\+-]([0-9]+)([ACGTNacgtn]+)").sub,
    indel_sub=lambda match: match.group(2)[int(match.group(1)):],
    sep=b"\t",
    merge=b"".join,
    int=int,
    frombuffer=partial(np.frombuffer, dtype=np.int8),
    arange=np.arange,
    sample_size=250
):
    """Parse samtools pileup output.
    
    Args:
        pileup: one samtools pileup output line
        sample_size: bases to downsample pileup to
    Returns:
        a pileup tuple consisting of pos, ref, seqs, quals and n (depth)
    """

    pileup = pileup.split(sep)

    pos = int(pileup[1])
    ref = pileup[2]
    seqs = merge(pileup[4::3])
    quals = merge(pileup[5::3])

    # cleanup sequence
    seqs = indel_re_sub(indel_sub, seqs)
    seqs = frombuffer(seqs)
    quals = frombuffer(quals)

    if seqs.size > sample_size:
        # taking the first bases from pileup should be sufficiently random
        offset = (seqs.size - sample_size) / 2
        seqs = seqs[offset:offset + sample_size]
        quals = quals[offset:offset + sample_size]

    return pos, ref, seqs.size, seqs, quals


def calc_pileup(
    fastapath,
    samfilepaths,
    reference,
    buffersize,
    offset,
    max_pileup_depth=254,
    mapq_downgrade=50,
    min_mapq=17,
    min_baseq=13,
    baq=True,
    parse_pileup=parse_pileup,
):
    """Calculate pileups for a given region.
    
    Args:
        fastapath: path to fasta reference
        samfilepaths: paths to SAM files
        reference: reference sequence name
        buffersize: buffer size
        offset: offset
        max_pileup_depth: maximum pileup depth (for downsampling)
    Returns:
        a pileup tuple consisting of pos,
        ref_alleles, address (address of the i-th pileup), seqs and quals
    """

    # TODO find a way to replace indels in awk, use mawk with below code to replace large parts of the parse_pileup function
    awk = r"""
    BEGIN {
        OFS = "\t"
    }
    {
        n = 0
        for(i=4; i<=imax; i+=3) {
            n += $i
        }
        if(n > 0 && ($3 ~ /[ACGTacgt]/)) {
            for(j=5; j<=jmax; j+=3) {
                gsub(/\./, $3, $j)
                gsub(/\,/, tolower($3), $j)
                gsub(/(\$|\^.)/, "", $j)
            }
            print
        }
    }
    """

    # region parameter works inclusive
    region = "{}:{}-{}".format(reference, offset + 1, offset + buffersize)
    with subprocess.Popen(
        [
            "samtools", "mpileup",
            "-d", str(max_pileup_depth * 2),
            "-q", str(min_mapq),
            "-Q", str(min_baseq),
            "-C", str(mapq_downgrade),
            "-f", fastapath,
            "-r", region
        ] + (
            [] if baq else ["-B"]
        ) + samfilepaths,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as mpileup:
        with subprocess.Popen(
            [
                "mawk",
                "-v", "imax={}".format(4 + (len(samfilepaths) - 1) * 3),
                "-v", "jmax={}".format(5 + (len(samfilepaths) - 1) * 3),
                awk
            ],
            stdin=mpileup.stdout,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        ) as awk:
            out, err = awk.communicate()
            if awk.returncode != 0:
                raise AlpacaError(
                    "AWK terminated with exit code {}:\n{}".format(
                        awk.returncode, err.decode()
                    )
                )
            _, err = mpileup.communicate()
            if mpileup.returncode != 0:
                raise AlpacaError(
                    "Samtools terminated with exit code {}:\n{}".format(
                        mpileup.returncode, err.decode()
                    )
                )
    try:
        logging.debug("parsing pileups")
        pileups = [parse_pileup(pileup) for pileup in out.split(b"\n")[:-1]]

        if not pileups:
            return

        logging.debug("calculating pileup pos")
        pos = np.fromiter(map(itemgetter(0), pileups), dtype=np.int32)
        pos -= 1

        logging.debug("calculating pileup address")
        address = np.cumsum(
            [0] + [pileup[2] for pileup in pileups],
            dtype=np.int32
        )

        logging.debug("calculating ref alleles")
        ref_alleles = np.fromiter(
            [ord(pileup[1]) for pileup in pileups],
            dtype=np.uint8
        )

        logging.debug("calculating seqs")
        seqs = np.concatenate([pileup[3] for pileup in pileups])
        logging.debug("calculating quals")
        quals = np.concatenate([pileup[4] for pileup in pileups])
    except Exception as e:
        print(e)
        raise e

    return Pileup(pos, ref_alleles, address, seqs, quals)
