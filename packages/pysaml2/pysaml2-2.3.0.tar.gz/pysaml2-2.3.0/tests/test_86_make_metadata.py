from saml2.saml import NAME_FORMAT_URI
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2.entity_category.edugain import COC

__author__ = 'roland'

BASE = "http://localhost"

CONFIG = {
    "entityid": "%s/%ssp.xml" % (BASE, ""),
    'entity_category': [COC],
    "description": "Example SP",
    "service": {
        "sp": {
            "required_attributes": ["surname", "givenname",
"edupersonaffiliation"],
            "optional_attributes": ["title"],
            "endpoints": {
                "assertion_consumer_service": [
                    ("%s/acs/redirect" % BASE, BINDING_HTTP_REDIRECT),
                    ("%s/acs/post" % BASE, BINDING_HTTP_POST)
                ],
            },
        },
    },
    "key_file": "pki/mykey.pem",
    "cert_file": "pki/mycert.pem",
    "metadata": {"local": ["idp.xml"]},
    #"attribute_map_dir": "pysaml2/example/attributemaps",
    "name_form": NAME_FORMAT_URI,
}

