from saml2 import config, BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.saml import NAMEID_FORMAT_TRANSIENT

__author__ = 'roland'

conf = config.SPConfig()
conf.load_file("servera_conf")
client = Saml2Client(conf)

selected_idp = "urn:mace:example.com:saml:roland:idp"
came_from = "/"

foo = client.prepare_for_authenticate(
    entityid=selected_idp, relay_state=came_from, sign=True,
    binding=BINDING_HTTP_POST, nameid_format=NAMEID_FORMAT_TRANSIENT)

print foo