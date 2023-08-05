from saml2.client import Saml2Client
from saml2 import config
from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.entity_category.edugain import COC
from saml2.saml import NAME_FORMAT_URI
from pathutils import xmlsec_path, full_path

__author__ = 'roland'

BASE = "http://localhost:8087"


CONFIG = {
    "entityid": "%s/%ssp.xml" % (BASE, ""),
    'entity_category': [COC],
    "description": "Python SP",
    "service": {
        "sp": {
            "authn_requests_signed": "true",
            "want_assertions_signed": "true",
            "endpoints": {
                "assertion_consumer_service": [
                    ("%s/acs/redirect" % BASE, BINDING_HTTP_REDIRECT),
                    ("%s/acs/post" % BASE, BINDING_HTTP_POST)
                ],
            },
        },
    },
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    "xmlsec_binary": xmlsec_path,
    "metadata": {"local": ["./idp.xml"]},
    "name_form": NAME_FORMAT_URI,
    "debug": 1,
}

conf = config.SPConfig()
conf.load(CONFIG)
client = Saml2Client(conf)

req = client.create_authn_request("urn:mace:example.com:saml:roland:idp")
print req