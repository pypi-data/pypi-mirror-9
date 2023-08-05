#!/usr/bin/env python
# -*- coding: utf-8 -*-

from saml2 import BINDING_SOAP, BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.saml import NAMEID_FORMAT_PERSISTENT
from saml2.saml import NAME_FORMAT_URI

try:
    from saml2.sigver import get_xmlsec_binary
    xmlsec_path = get_xmlsec_binary(["/opt/local/bin"])
except ImportError:
    xmlsec_path = '/usr/bin/xmlsec1'

BASE = "http://localhost:8088"

CONFIG = {
    "entityid" : "%s/idp.xml" % BASE,
    "name" : "Rålands IdP",
    "service": {
        "idp": {
            "endpoints" : {
                "single_sign_on_service" : [
                    ("%s/sso" % BASE, BINDING_HTTP_REDIRECT)],
                "single_logout_service": [
                    ("%s/slo" % BASE, BINDING_SOAP),
                    ("%s/slop" % BASE,BINDING_HTTP_POST)]
            },
            "policy": {
                "default": {
                    "lifetime": {"minutes":15},
                    "attribute_restrictions": None, # means all I have
                    "name_form": NAME_FORMAT_URI,
                    },
                "urn:mace:example.com:saml:roland:sp": {
                    "lifetime": {"minutes": 5},
                    "nameid_format": NAMEID_FORMAT_PERSISTENT,
                    # "attribute_restrictions":{
                    #     "givenName": None,
                    #     "surName": None,
                    # }
                }
            },
            "subject_data": "subject_data.db",
            #"domain": "umu.se",
            #"name_qualifier": ""
        },
        },
    "debug" : 1,
    "key_file" : "test.key",
    "cert_file" : "test.pem",
    "xmlsec_binary" : xmlsec_path,
    "metadata": {
        "local": ["metadata_sp_1.xml", "vo_metadata.xml"],
        },
    "attribute_map_dir" : "attributemaps",
    "organization": {
        "name": "Exempel AB",
        "display_name": [("Ögonblick AB","se"),("Momemt Inc.","en")],
        "url":"http://www.example.com/roland",
        },
    "contact_person": [{
                           "given_name":"Åke",
                           "sur_name": "Österlund",
                           "email_address": ["john.smith@example.com"],
                           "contact_type": "technical",
                           },
                       ],
    }
