from saml2 import BINDING_HTTP_POST
from saml2.metadata import entity_descriptor
from saml2.config import SPConfig
from saml2.client import Saml2Client

__author__ = 'roland'

fil = "sp_multi_index_endp_conf"

conf = SPConfig()
conf.load_file(fil)

client = Saml2Client(conf)

endp = client.config.endpoint("assertion_consumer_service")

assert len(endp) == 3
assert endp[0] == "http://lingon.catalogix.se:8087/A"


cnf = SPConfig().load_file(fil, metadata_construction=True)
edesc = entity_descriptor(cnf)

acs = edesc.spsso_descriptor.assertion_consumer_service
assert len(acs) == 3

assert acs[0].binding == BINDING_HTTP_POST
assert acs[0].index == '1'
assert acs[0].location == "http://lingon.catalogix.se:8087/A"

assert acs[1].binding == BINDING_HTTP_POST
assert acs[1].index == '2'
assert acs[1].location == "http://lingon.catalogix.se:8087/B"

assert acs[2].binding == BINDING_HTTP_POST
assert acs[2].index == '3'
assert acs[2].location == "http://lingon.catalogix.se:8087/C"

cnf = SPConfig().load_file("sp_3_tup_conf", metadata_construction=True)
edesc = entity_descriptor(cnf)
acs = edesc.spsso_descriptor.assertion_consumer_service

print edesc