"""
Print calls in vcf to stdout.
"""

__author__ = "Johannes Köster"
__license__ = "MIT"

import sys
from functools import partial
from collections import OrderedDict
import logging

import numpy as np

from alpaca.version import __version__


READCOUNT_ALLELES = "A C G T N INDEL".split()


VCF_HEADER = "##fileformat=VCFv4.1"

def print_header(samples, query, expected_fdr):
    """Print vcf header including field definitions used by ALPACA."""

    def print_info(**kwargs):
        print(
            '##INFO=<ID={id},Number={number},'
            'Type={type},Description="{desc}">'.format(**kwargs)
        )

    def print_format(**kwargs):
        print(
            '##FORMAT=<ID={id},Number={number},'
            'Type={type},Description="{desc}">'.format(**kwargs)
        )

    print(VCF_HEADER)
    print("##source=alpaca-{}".format(__version__))
    print_info(
        id="WORST_CONSEQUENCES", number=".", type="String",
        desc="Most severe consequences for called alternative alleles in the order listed"
    )
    print_info(
        id="GENES", number=".", type="String",
        desc="Overlapping gene symbols."
    )
    print_info(
        id="TRANSCRIPT_CONSEQUENCES", number=".", type="String",
        desc=(
            "Transcript consequences. Each entry consists of "
            "allele:gene-symbol:ensembl-id:consequence"
        )
    )
    print_info(
        id="PROTEIN_CONSEQUENCES", number=".", type="String",
        desc=(
            "Protein consequences. Each entry consists of "
            "allele:gene-symbol:hgvs-notation:polyphen-prediction:polyphen-score:sift-prediction:sift-score"
        )
    )
    print_info(
        id="REGULATORY_FEATURES", number=".", type="String",
        desc="Ensembl IDs of overlapping regulatory features"
    )
    print_info(
        id="COLOCATED_VARIANTS", number=".", type="String",
        desc="IDs of colocated variants"
    )

    # the following format specifications are taken from GATK
    print_format(id="GT", number=1, type="String", desc="Genotype")
    print_format(
        id="AD", number=".", type="Integer",
        desc="Allelic depths for the ref and alt alleles in the order listed"
    )
    print_format(
        id="DP", number=1, type="Integer",
        desc="Approximate read depth (reads with MQ=0 or with bad mates are filtered)"
    )
    print_format(
        id="SB", number=1, type="Integer",
        desc="PHRED-scaled p-value for strand bias (fishers exact test)"
    )
    print_format(
        id="RC", number=".", type="Integer",
        desc=(
            "Read counts for A,C,G,T,N,INDEL,a,c,g,t,n,indel. "
            "Lowercase represents reverse complement counts."
        )
    )
    print('##ALPACA_ARGS={}'.format(" ".join(sys.argv)))
    print('##ALPACA_QUERY={}'.format(query))
    if expected_fdr is not None:
        print('##EXPECTED_FDR={:.2e}'.format(expected_fdr))
    print(
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{}".format(
            "\t".join(samples)
        )
    )


def fmt_sb(value):
    """Format the strand bias."""
    return "." if value < 0 else value


def fmt_info(**entries):
    """Format the info field."""
    if all(value is None for name, value in entries.items()):
        return "."
    return ";".join(
        "{}={}".format(name, value) for name, value in entries.items()
    )


def print_records(
    calls,
    sample_fmt="GT:AD:DP:SB:RC",
    tostr=partial(map, str),
    fmt_sb=fmt_sb
):
    """Print a call record in vcf format."""
    for call in calls:

        print(
            call.chrom,
            call.pos + 1,
            ".",
            call.alleles[0],
            ",".join(call.alleles[1:]),
            call.qual,
            ".",
            ".",
            sample_fmt,
            sep="\t",
            end="\t"
        )

        print(
            *[
                "{gt}:{ad}:{dp}:{sb}:{rc}".format(
                    gt="/".join(tostr(sample.genotype)),
                    dp=sample.read_depth,
                    ad=",".join(tostr(sample.allele_depths)),
                    sb=fmt_sb(sample.strand_bias),
                    rc=",".join(tostr(sample.detailed_allele_depth))
                )
                for sample in call.sample_info
            ],
            sep="\t"
        )
