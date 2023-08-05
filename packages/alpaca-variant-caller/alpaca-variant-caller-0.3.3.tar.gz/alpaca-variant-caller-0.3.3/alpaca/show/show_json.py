import json
import sys


from alpaca.ensembl import PROTEIN_CONSEQUENCE_FIELDS, TRANSCRIPT_CONSEQUENCE_FIELDS


def show(vcfreader):
    print("[")
    for i, record in enumerate(vcfreader):
        data = {
            "id": i,
            "chrom": record.CHROM,
            "pos": record.POS,
            "ref": record.REF,
            "alt": list(map(str, record.ALT)),
            "qual": record.QUAL,
            "genes": record.INFO.get("GENES", []),
            "transcript_consequences": [
                dict(zip(TRANSCRIPT_CONSEQUENCE_FIELDS, consequence.split(":")))
                for consequence in record.INFO.get("TRANSCRIPT_CONSEQUENCES", [])
            ],
            "protein_consequences": [
                dict(zip(PROTEIN_CONSEQUENCE_FIELDS, consequence.split(":")))
                for consequence in record.INFO.get("PROTEIN_CONSEQUENCES", [])
            ],
            "regulatory_features": record.INFO.get("REGULATORY_FEATURES", []),
            "colocated_variants": record.INFO.get("COLOCATED_VARIANTS", []),
            "worst_consequence": record.INFO.get("WORST_CONSEQUENCES", []),
            "sample_info": [
                {
                    "sample": call.sample,
                    "genotype": call.data.GT,
                    "ref_depth": call.data.AD[0],
                    "alt_depths": call.data.AD[1:],
                    "depth": call.data.DP,
                    "strand_bias": call.data.SB,
                    "read_counts": call.data.RC
                }
                for call in record.samples
            ]
        }
        json.dump(data, sys.stdout)
        print(",")
    print("]")
