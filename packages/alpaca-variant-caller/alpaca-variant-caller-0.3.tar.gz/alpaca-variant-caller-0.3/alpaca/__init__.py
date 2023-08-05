
"""Alpaca is an ALgebraic PArallel single nucleotide variant CAller.
Alpaca has two major distinguishing features compared to other variant callers like GATK or MuTect:

* for each given sample, the genotype likelihoods are preprocessed and stored in an extendible HDF5 index
* given the preprocessed index and an algebraic query posterior probabilities for a variant given the query can be calculated very fast

The separation into indexing and calling allows to add samples later without having to redo all the computations.
The algebraic query allows to model calling scenarios in a very flexible way, e.g.

* calling all somatic mutations of a tumor: "tumor_sample - normal_sample"
* calling loss of heterozygosity: "normal_sample - tumor_sample"
"""


__author__ = "Johannes Köster"
__license__ = "MIT"


# I would like to thank my wife Christine for allowing me to work on this during my vacation ;-).


import os
import sys
import argparse
import logging
import traceback
import math
import csv

import numpy as np
import pyopencl as cl
import h5py
import vcf as pyvcf

import alpaca.algebra as algebra
from alpaca.index.sample_index import SampleIndex
from alpaca.index.global_index import GlobalIndex
from alpaca.index.view import SampleIndexView, IndexView, IndexLocusView
from alpaca.caller import Caller
from alpaca.utils import init_opencl, AlpacaError, LOG_TO_PHRED_FACTOR
import alpaca.vcf as vcf
from alpaca.show import show_html, show_json
from alpaca.version import __version__
from alpaca.caller.annotate import FDR
from alpaca.peek import Peek
from alpaca import ensembl


def get_sample_name(samfilepath):
    """Obtain sample name from SAM or BAM file.
    
    Args:
        samfilepath (str): the path to the SAM file
    """
    return "".join(os.path.splitext(os.path.basename(samfilepath))[:-1])


def index_sample(
    hdf5path,
    fastapath,
    samfilepaths,
    sample_name,
    ploidy=2,
    buffersize=1000000,
    threads=1,
    mapq_downgrade=50,
    min_mapq=17,
    min_baseq=13,
    baq=True,
    cl_device="cpu",
    compression_type=None,
    compression_shuffle=False,
    compression_half=False,
    chunksize=1000000
):
    """Index a sample.
    
    Args:
        fastapath (str): path to FASTA file
        samfilepaths (list): paths to SAM files
        sample_name (str): sample name
        ploidy (int): assumed ploidy
        buffersize (int): the buffersize
        threads (int): threads to use
        cl_device (str): type of opencl device (cpu, gpu, accelerator, any)
    """

    cl_queue, cl_mem_pool = init_opencl(device_type=cl_device, threads=threads)

    sample_index = SampleIndex(
        cl_queue,
        cl_mem_pool,
        hdf5path,
        buffersize=buffersize,
        ploidy=ploidy
    )
    sample_index.build(
        fastapath,
        samfilepaths,
        sample_name,
        threads=threads,
        mapq_downgrade=mapq_downgrade,
        min_mapq=min_mapq,
        min_baseq=min_baseq,
        baq=baq,
        compression_type=compression_type,
        compression_shuffle=compression_shuffle,
        compression_half=compression_half,
        chunksize=chunksize
    )


def merge(
    fastapath,
    hdf5path,
    *sample_index_paths,
    buffersize=1000000,
    threads=1,
    cl_device="cpu"
):
    """Merge sample indexes.
    
    Args:
        fastapath (str): path to FASTA file
        hdf5path (str): path to merged index
        sample_index_paths (list) paths to sample indexes
        buffersize (int): the buffersize
        threads (int): threads to use
        cl_device (str): type of opencl device (cpu, gpu, accelerator, any)
    """
    cl_queue, cl_mem_pool = init_opencl(device_type=cl_device, threads=threads)

    ploidies = [
        SampleIndexView(hdf5path, buffersize=buffersize).ploidy
        for hdf5path in sample_index_paths
    ]
    ploidy = ploidies[0]
    if not all(p == ploidy for p in ploidies):
        raise AlpacaError("All samples must have the same expected ploidy.")

    global_index = GlobalIndex(
        cl_queue,
        cl_mem_pool,
        hdf5path,
        ploidy=ploidy
    )
    global_index.build(fastapath, *sample_index_paths, buffersize=buffersize)


def call(
    hdf5path,
    query,
    heterozygosity=0.001,
    min_qual=50,
    max_fdr=None,
    min_total_depth=None,
    max_strand_bias=None,
    locus=None,
    buffersize=1000000,
    threads=1,
    cl_device="cpu"
):
    """Perform calling.
    
    Args:
        hdf5path (str): path to index
        query (str): algebraic query formula
        heterozygosity (float): expected heterozygosity
        min_qual (int): minimum quality
        max_fdr (float): maximum expected FDR
        min_total_depth (int): minimum total depth over all samples
        max_strand_bias (int): maximum strand bias
        buffersize (int): the buffersize
        threads (int): threads to use
        cl_device (str): type of opencl device (cpu, gpu, accelerator, any)
    """

    cl_queue, cl_mem_pool = init_opencl(device_type=cl_device, threads=threads)

    if locus is None:
        index = IndexView(hdf5path, buffersize=buffersize)
    else:
        index = IndexLocusView(hdf5path, locus, buffersize=buffersize)
    formula = algebra.parse(query, index.samples)
    called_samples = algebra.get_samples(formula)

    if max_fdr is not None:
        min_qual = LOG_TO_PHRED_FACTOR * math.log(max_fdr)

    caller = Caller(
        cl_queue,
        cl_mem_pool,
        formula,
        index,
        heterozygosity=heterozygosity,
        min_qual=min_qual,
        buffersize=buffersize
    )

    calls = caller.call()

    fdr_max_prob, expected_fdr = None, None
    if max_fdr is not None:
        fdr = FDR(cl_queue, cl_mem_pool)
        if calls:
            fdr_max_prob, expected_fdr = fdr.calc_max_prob(calls, max_fdr)

    logging.debug("printing calls")
    vcf.print_header(called_samples, query, expected_fdr)
    for _calls in calls:
        _calls.filter(
            max_prob=fdr_max_prob,
            min_total_depth=min_total_depth,
            max_strand_bias=max_strand_bias
        )
        vcf.print_records(_calls)


def annotate(species="human"):
    """Parse vcf from STDIN and print annotated records to STDOUT
    Annotation is performed via the Ensembl VEP REST API and needs an internet
    conntection.
    
    Args:
        species: Ensembl species name for annotation
    """
    reader = pyvcf.Reader(sys.stdin)
    writer = pyvcf.Writer(sys.stdout, template=reader)
    for record in ensembl.annotate(reader, species=species):
        writer.write_record(record)
    writer.close()


def show(type="html", species="human"):
    """Output vcf from STDIN to STDOUT in given format.
    
    Args:
        type: output format (html or json)
    """
    reader = pyvcf.Reader(sys.stdin)
    if type == "html":
        show_html.show(reader, species=species)
    elif type == "json":
        show_json.show(reader)
    else:
        raise ValueError("Argument type must be either json or html")


def peek(
    sample_hdf5path,
    likelihoods=False,
    buffersize=1000000,
    threads=1,
    cl_device="cpu"
):
    cl_queue, cl_mem_pool = init_opencl(device_type=cl_device, threads=threads)

    peek = Peek(cl_queue, cl_mem_pool, sample_hdf5path)

    loci = (
        (l[0], int(l[1]))
        for l in csv.reader(sys.stdin, delimiter="\t")
        if not l[0][0] == "#"
    )
    peek.peek(loci, likelihoods=likelihoods, buffersize=buffersize)


def argument_parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--version", "-v", action="version", version=__version__
    )
    p.add_argument(
        "--threads", "-t", type=int, default=1,
        help="How many parallel threads to use."
    )
    p.add_argument(
        "--compute-device", "--dev", choices="gpu cpu accelerator any".split(),
        default="cpu",
        help="Compute device to use. CPU per default. Any lets the system decide."
    )
    p.add_argument(
        "--buffersize", "-b", type=int, default=1000000,
        help="How many bases shall be investigated at the same time."
    )
    p.add_argument(
        "--debug", "-d", action="store_true", help="Show debug output"
    )
    p.add_argument("--profile", help="Profile alpaca")
    subparsers = p.add_subparsers(dest="subcommand", help='')

    index = subparsers.add_parser(
        "index", help="Calculate the alpaca index for given bam files."
    )
    index.add_argument(
        "reference",
        help=(
            "Path to the reference fasta file. "
            "Has to be indexed with samtools faidx."
        )
    )
    index.add_argument(
        "bamfiles", metavar="BAM", nargs="+",
        help=(
            "Bam files of a single sample that shall be indexed. "
            "If more than one bam file is given, --sample-name has "
            "to be specified."
        )
    )
    index.add_argument("index", help="Path to the index HDF5 file.")
    index.add_argument(
        "--sample-name", "-n",
        help=(
            "Sample name. Per default, sample name is inferred from bam "
            "file name as path/to/<samplename>.bam."
        )
    )
    index.add_argument(
        "--ploidy", "-p", type=int, default=2, metavar="INT",
        help="Assumed ploidy of samples in index."
    )
    index.add_argument(
        "--mapq-downgrade", "-C", type=int, default=50, metavar="INT",
        help=(
            "Downgrade mapping quality in case of excessive mismatches (default 50)."
            "See samtools manual for details."
        )
    )
    index.add_argument(
        "--min-mapq", "-q", type=int, default=17, metavar="INT",
        help="Minimum mapping quality for a read to be considered."
    )
    index.add_argument(
        "--min-baseq", "-Q", type=int, default=13, metavar="INT",
        help="Minimum base quality for a base to be considered."
    )
    index.add_argument(
        "--no-baq", "-B", action="store_true",
        help=(
            "Do not calculate base alignment quality (BAQ; see samtools "
            "manual) to correct base qualities."
        )
    )
    index.add_argument(
        "--compression", "-c", choices="n h g gs gh gsh l ls lh lsh".split(),
        default="gh",
        help=(
            "Compression to use for sample index (default none). "
            "n: no compression, "
            "h: store half-precision floats (lossy), "
            "g: gzip compression, "
            "gs: gzip with shuffle filter, "
            "gh: gzip with half-precision floats (lossy), "
            "gsh: gzip with half-precision floats and shuffle filter (lossy), "
            "l: lzf compression (default), "
            "ls: lzf with shuffle filter, "
            "lh: lzf with half-precision floats (lossy), "
            "lsh: lzf with half-precision floats and shuffle filter (lossy), "
        )
    )
    index.add_argument(
        "--chunksize", default=1000000, type=int,
        help=(
            "HDF5 chunk size. Should be a divider of buffer size. "
            "Ignored if neither gzip nor bzip2 compression is used (default)."
        )
    )

    merge = subparsers.add_parser(
        "merge", help="Merge sample indexes for calling."
    )
    merge.add_argument(
        "reference",
        help=(
            "Path to the reference fasta file. Has to be indexed with "
            "samtools faidx."
        )
    )
    merge.add_argument(
        "sample_indexes", nargs="+", metavar="FILE",
        help="Path to the sample index HDF5 files."
    )
    merge.add_argument(
        "merged_index", help="Path to the resulting index HDF5 file."
    )

    call = subparsers.add_parser(
        "call", help="Call SNVs given an algebraic formula."
    )
    call.add_argument("index", help="Path to the index HDF5 file.")
    call.add_argument("query", help="Algebraic calling expression.")

    min_qual = call.add_mutually_exclusive_group(required=True)
    min_qual.add_argument(
        "--fdr", "-f", type=float, const=0.05, nargs="?",
        help=(
            "Maximum allowed expected false discovery rate (FDR). "
            "The expected FDR is calculated from the posterior probabilities "
            "for observing the reference genotype given the query. "
            "If no value is given, an FDR of 0.05 is ensured."
        )
    )
    min_qual.add_argument(
        "--min-qual", "-q", type=int, const=50, nargs="?",
        help=(
            "Minimum quality for a call to be printed. "
            "The quality is the PHRED scaled posterior probability for "
            "observing the reference genotype given the query. "
            "If no value is given, a minimum quality of 50 is ensured."
        )
    )

    call.add_argument(
        "--max-strand-bias", "-sb", type=int,
        help=(
            "Maximum PHRED-scaled strand bias p-value. "
            "A variant is not called, if the strand bias "
            "for any sample violates the threshold."
        )
    )
    call.add_argument(
        "--min-total-depth", "-d", type=int,
        help=(
            "Minimum total read depth at a site. "
            "Calls with less will be marked as LOW_DEPTH. "
            "Not used per default."
        )
    )
    call.add_argument(
        "--heterozygosity", "-het", type=float, default=0.001, 
        help="Expected heterozygosity (default 0.001 for human)."
    )
    call.add_argument(
        "--locus", "-l",
        help="Restrict calling to a certain locus (e.g. chr1:60038)"
    )

    annotate = subparsers.add_parser(
        "annotate", help=(
            "Annotate calls with variant effects obtained online from "
            "Ensembl VEP. Needs internet connection. Default species is human. "
            "This uses always the latest assembly. Hence the annotations are "
            "only correct if alpaca was run on the latest assembly."
            "Calls are streamed in vcf format from STDIN. "
            "Output is streamed in vcf format to STDOUT."
        )
    )
    annotate.add_argument(
        "--species", "-s", default="human",
        help="Ensembl species name or alias for annotation (default human)."
    )

    show = subparsers.add_parser(
        "show", help=(
            "Show calls as HTML (human readable) or JSON (machine readable). "
            "Calls are streamed in vcf format from STDIN. "
            "Output is streamed to STDOUT."
        )
    )
    show.add_argument(
        "--format", "-f", default="html", choices="html json".split(),
        help="Output format (default html)."
    )
    show.add_argument(
        "--species", "-s", default="human",
        help="Ensembl species name or alias for annotation (default human)."
    )

    peek = subparsers.add_parser(
        "peek", help="Peek into the given sample index at loci given by stdin. These can be either tab separated CHROM POS pairs or a vcf file."
    )
    peek.add_argument("index", help="Path to the sample index HDF5 file.")
    peek.add_argument(
        "--likelihoods", "-l",
        action="store_true",
        help="Print likelihoods instead of allele depths."
    )

    return p

def main():
    p = argument_parser()
    args = p.parse_args()

    logging.basicConfig(
        format=" %(asctime)s: %(message)s",
        level=logging.DEBUG if args.debug else logging.INFO,
        stream=sys.stderr)

    if args.profile:
        import yappi
        yappi.start()

    def check_reference():
        if not any(
            args.reference.endswith(ext)
            for ext in ".fa .fa.gz .fasta .fasta.gz".split()
        ):
            print(
                "Invalid reference. Has to be .fa, .fa.gz, .fasta or .fasta.gz",
                file=sys.stderr
            )
            p.print_help()
            exit(1)

    def check_index(index):
        if not index.endswith(".hdf5"):
            print(
                "Invalid alpaca index given. Has to be an HDF5 file with "
                "suffix hdf5.",
                file=sys.stderr
            )
            p.print_help()
            exit(1)

    def parse_compression(args_compression):
        compression = {
            "compression_type": None,
        }
        if "g" in args_compression:
            compression["compression_type"] = "gzip"
        if "l" in args_compression:
            compression["compression_type"] = "lzf"
        compression["compression_shuffle"] = "s" in args.compression
        compression["compression_half"] = "h" in args.compression
        return compression

    try:
        if args.subcommand == "index":
            check_reference()
            check_index(args.index)

            sample_name = args.sample_name
            if sample_name is None:
                if len(args.bamfiles) > 1:
                    p.print_help()
                sample_name = get_sample_name(args.bamfiles[0])

            # parse compression
            compression = parse_compression(args.compression)

            index_sample(
                args.index,
                args.reference,
                args.bamfiles,
                sample_name,
                ploidy=args.ploidy,
                mapq_downgrade=args.mapq_downgrade,
                min_mapq=args.min_mapq,
                min_baseq=args.min_baseq,
                baq=not args.no_baq,
                buffersize=args.buffersize,
                threads=args.threads,
                cl_device=args.compute_device,
                chunksize=args.chunksize,
                **compression
            )

        elif args.subcommand == "merge":
            check_reference()
            check_index(args.merged_index)
            for sample_index in args.sample_indexes:
                check_index(sample_index)
            merge(
                args.reference,
                args.merged_index,
                *args.sample_indexes,
                buffersize=args.buffersize,
                threads=args.threads,
                cl_device=args.compute_device
            )

        elif args.subcommand == "call":
            check_index(args.index)
            call(
                args.index,
                args.query,
                min_qual=args.min_qual,
                max_fdr=args.fdr,
                min_total_depth=args.min_total_depth,
                max_strand_bias=args.max_strand_bias,
                heterozygosity=args.heterozygosity,
                locus=args.locus,
                buffersize=args.buffersize,
                threads=args.threads,
                cl_device=args.compute_device
            )

        elif args.subcommand == "annotate":
            annotate(species=args.species)

        elif args.subcommand == "show":
            show(species=args.species, type=args.format)

        elif args.subcommand == "peek":
            peek(
                args.index,
                likelihoods=args.likelihoods,
                buffersize=args.buffersize,
                threads=args.threads,
                cl_device=args.compute_device
            )

        else:
            print("Invalid subcommand.", file=sys.stderr)
            p.print_help()
            exit(1)
    except cl.MemoryError as e:
        logging.error(
            "Not enough memory on device. "
            "Consider switching to another device "
            "(e.g. a better GPU, or to the CPU), or reduce the buffersize."
        )
        logging.debug(traceback.format_exc(e))
        exit(1)
    except AlpacaError as e:
        logging.error(e)
        exit(1)
    except KeyboardInterrupt as e:
        logging.error("Cancelled on user request.")
        exit(1)
    except BrokenPipeError:
        # exit silently (e.g. in case of using head)
        exit(0)

    if args.profile:
        with open(args.profile, "w") as out:
            profile = yappi.get_func_stats()
            profile.sort("totaltime")
            profile.print_all(out=out)
