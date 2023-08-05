
import os
import urllib.request
from mako.template import Template

from alpaca.show import show_json
from alpaca.vcf import READCOUNT_ALLELES


def show(vcfreader, species="human"):
    query = vcfreader.metadata["ALPACA_QUERY"][0]
    args = vcfreader.metadata["ALPACA_ARGS"][0]
    samples = vcfreader.samples

    css = [
        "https://cdnjs.cloudflare.com/ajax/libs/foundation/5.5.0/css/foundation.css",
        "https://raw.githubusercontent.com/DataTables/Plugins/master/integration/foundation/dataTables.foundation.css",
        "https://raw.githubusercontent.com/vedmack/yadcf/master/jquery.dataTables.yadcf.css",
        "https://cdnjs.cloudflare.com/ajax/libs/select2/3.5.2/select2.css"
    ]

    js = [
        "https://cdnjs.cloudflare.com/ajax/libs/foundation/5.5.0/js/vendor/modernizr.js",
        "https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/jquery.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/foundation/5.5.0/js/foundation.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/select2/3.5.2/select2.min.js",
        "https://raw.githubusercontent.com/DataTables/DataTables/master/media/js/jquery.dataTables.min.js",
        "https://raw.githubusercontent.com/DataTables/Plugins/master/integration/foundation/dataTables.foundation.min.js",
        "https://raw.githubusercontent.com/vedmack/yadcf/master/jquery.dataTables.yadcf.js"
    ]

    # header
    print(
        Template(
            filename=os.path.join(os.path.dirname(__file__), "header.html")
        ).render(
            query=query,
            samples=samples,
            alleles=READCOUNT_ALLELES,
            css=map(get_content, css),
            js=map(get_content, js)
        )
    )

    # content
    show_json.show(vcfreader)

    # footer
    print(
        Template(
            filename=os.path.join(os.path.dirname(__file__), "footer.html")
        ).render(samples=samples, alleles=READCOUNT_ALLELES, species=species)
    )


def get_content(url):
    return urllib.request.urlopen(url).read().decode()
