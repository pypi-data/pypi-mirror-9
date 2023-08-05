
import json
from itertools import islice
from urllib.request import Request, urlopen
import logging


TRANSCRIPT_CONSEQUENCE_FIELDS = "alt gene transcript_id consequence".split()
PROTEIN_CONSEQUENCE_FIELDS = (
    "alt gene transcript_id consequence hgvsp polyphen_prediction "
    "polyphen_score sift_prediction sift_score".split()
)


def annotate(records, species="human"):
    def transcript_effects(alt, transcript_annotation):
        transcript_id = transcript_annotation["transcript_id"]
        gene = transcript_annotation["gene_symbol"]
        for consequence in transcript_annotation["consequence_terms"]:
            yield "{alt}:{gene}:{transcript_id}:{consequence}".format(
                alt=alt,
                gene=gene,
                transcript_id=transcript_id,
                consequence=consequence
            )

    def protein_effects(alt, transcript_annotation):
        transcript_id = transcript_annotation["transcript_id"]
        gene = transcript_annotation["gene_symbol"]
        get = lambda key: transcript_annotation.get(key, ".")
        hgvsp = transcript_annotation["hgvsp"]
        if ":" in hgvsp:
            hgvsp = hgvsp.split(":")[1]
        for consequence in transcript_annotation["consequence_terms"]:
            yield (
                    "{alt}:{gene}:{transcript_id}:{consequence}:{hgvsp}:"
                    "{polyphen_prediction}:{polyphen_score}:{sift_prediction}:"
                    "{sift_score}"
                ).format(
                alt=alt,
                gene=gene,
                transcript_id=transcript_id,
                consequence=consequence,
                hgvsp=hgvsp,
                polyphen_prediction=get("polyphen_prediction"),
                polyphen_score=get("polyphen_score"),
                sift_prediction=get("sift_prediction"),
                sift_score=get("sift_score")
            )

    while True:
        record_buffer = list(islice(records, 1000))
        variants = [
            (record.CHROM, record.POS, record.REF, alt)
            for record in record_buffer
            for alt in record.ALT
        ]
        if not variants:
            break
        annotation = iter(get_variant_annotation(variants, species=species))
        for record in record_buffer:
            def store(key, info):
                if info:
                    record.INFO[key] = info

            record_annotation = list(islice(annotation, len(record.ALT)))
            store(
                "WORST_CONSEQUENCES",
                [a["most_severe_consequence"] for a in record_annotation]
            )
            transcripts = [
                a.get("transcript_consequences", []) for a in record_annotation
            ]
            if transcripts[0]:
                store("GENES", sorted(set(t["gene_symbol"] for t in transcripts[0])))

                store(
                    "TRANSCRIPT_CONSEQUENCES",
                    [
                        effect
                        for alt, alt_annotation in zip(record.ALT, transcripts)
                        for transcript in alt_annotation
                        if "hgvsp" not in transcript
                        for effect in transcript_effects(alt, transcript)
                    ]
                )

                store(
                    "PROTEIN_CONSEQUENCES",
                    [
                        effect
                        for alt, alt_annotation in zip(record.ALT, transcripts)
                        for transcript in alt_annotation
                        if "hgvsp" in transcript
                        for effect in protein_effects(alt, transcript)
                    ]
                )

            store(
                "REGULATORY_FEATURES",
                [
                    f["regulatory_feature_id"] for f in
                    record_annotation[0].get(
                       "regulatory_feature_consequences", []
                    )
                ]
            )
            store(
                "COLOCATED_VARIANTS",
                [
                    v["id"] for v in
                    record_annotation[0].get("colocated_variants", [])
                ]
            )
        yield from record_buffer


def get_variant_annotation(variants, species="human"):
    """Use the Ensembl REST API to obtain varaint annotation.
    
    Args:
        variants: a list (len <= 1000) of tuples of the form (chrom, pos (1-based), ref, alt)
        species:  Ensembl species name
    Yields:
        the JSON annotation as provided by VEP, see
        http://www.ensembl.org/info/docs/tools/vep/vep_formats.html#json
    """
    # batch requests of size 1000 are expected
    assert len(variants) <= 1000
    data = json.dumps(
        {
            "variants": [
                "{} {} - {} {} . . .".format(chrom, pos, ref, alt)
                for chrom, pos, ref, alt in variants
            ],
            "hgvs": 1,
            "canonical": 1
        }
    ).encode()

    req = Request(
        "http://rest.ensembl.org/vep/{}/region".format(species),
        data=data,
        headers={
            "Content-Type": "application/json",
            "accept": "application/json"
        }
    )
    response = json.loads(urlopen(req).read().decode())
    return response
