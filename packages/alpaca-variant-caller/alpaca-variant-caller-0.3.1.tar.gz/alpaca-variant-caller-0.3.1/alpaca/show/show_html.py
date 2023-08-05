
import os
from mako.template import Template

from alpaca.show import show_json
from alpaca.vcf import READCOUNT_ALLELES


def show(vcfreader, species="human"):
    query = vcfreader.metadata["ALPACA_QUERY"][0]
    args = vcfreader.metadata["ALPACA_ARGS"][0]
    samples = vcfreader.samples
    # header
    print(
        Template(
            filename=os.path.join(os.path.dirname(__file__), "header.html")
        ).render(query=query, samples=samples, alleles=READCOUNT_ALLELES)
    )

    # content
    show_json.show(vcfreader)

    # footer
    print(
        Template(
            filename=os.path.join(os.path.dirname(__file__), "footer.html")
        ).render(samples=samples, alleles=READCOUNT_ALLELES, species=species)
    )
