from saml2 import BINDING_SOAP
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_HTTP_POST
from saml2.saml import NAME_FORMAT_URI

from pathutils import full_path
from pathutils import xmlsec_path

BASE = "http://localhost:8088"

CONFIG = {
    "entityid": "urn:mace:example.com:saml:roland:idp",
    "name": "Rolands IdP",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service": [
                    ("%s/sso" % BASE, BINDING_HTTP_REDIRECT)],
                "single_logout_service": [
                    ("%s/slo" % BASE, BINDING_SOAP),
                    ("%s/slop" % BASE, BINDING_HTTP_POST)]
            },
            "policy": {
                "default": {
                    "lifetime": {"minutes": 15},
                    "attribute_restrictions": None,  # means all I have
                    "name_form": NAME_FORMAT_URI,
                },
            },
            "subject_data": full_path("subject_data.db"),
            #"domain": "umu.se",
            #"name_qualifier": ""
        },
    },
    "debug": 1,
    "key_file": full_path("test.key"),
    "cert_file": full_path("test.pem"),
    "xmlsec_binary": xmlsec_path,
    "metadata": {
        "mdfile": [full_path("swamid2.md")],
    },
}
