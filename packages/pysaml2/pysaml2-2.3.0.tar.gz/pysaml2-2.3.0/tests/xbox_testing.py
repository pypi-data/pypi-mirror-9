from saml2.sigver import make_temp, pre_encryption_part
from saml2.saml import EncryptedAssertion
from saml2 import sigver, class_name, extension_elements_to_elements
from saml2 import samlp
from saml2 import saml
from saml2 import config
from saml2.mdstore import MetadataStore
from saml2.s_utils import factory
from saml2.s_utils import do_attribute_statement

__author__ = 'roland'


# load SP configuration
conf = config.SPConfig()
conf.load_file("server_conf")
# load metadata
md = MetadataStore([saml, samlp], None, conf)
md.load("local", "idp_example.xml")
conf.metadata = md

# setup the security context
sec = sigver.security_context(conf)

# Create a dummy assertion
assertion = factory(
    saml.Assertion, version="2.0", id="11111",
    issue_instant="2009-10-30T13:20:28Z",
    signature=sigver.pre_signature_part("11111", sec.my_cert, 1),
    attribute_statement=do_attribute_statement(
        {("", "", "surName"): ("Foo", ""),
         ("", "", "givenName"): ("Bar", ""), })
)

# Sign the assertion using the IdPs private key
sigass = sec.sign_statement(assertion, class_name(assertion),
                            key_file="pki/mykey.pem", node_id=assertion.id)

# Create an Assertion instance from the signed assertion
_ass = saml.assertion_from_string(sigass)
# Put the signed assertion in an EncryptedAssertion instance
encrypted_assertion = EncryptedAssertion()
# Have to be added as an extension element since that is what the
# EncryptedAssertion can hold
encrypted_assertion.add_extension_element(_ass)

# create the encrypt data template
_, pre = make_temp("%s" % pre_encryption_part(), decode=False)
# Encrypt the Assertion
enctext = sec.crypto.encrypt(
    "%s" % encrypted_assertion, conf.cert_file, pre, "des-192",
    '/*[local-name()="EncryptedAssertion"]/*[local-name()="Assertion"]')

# So this is where it turns around and the following lines should
# eventually produce a readable assertion
# Decrypt the encrypted assertion
decr_text = sec.decrypt(enctext)

# Create an EncryptedAssertion class instance
_seass = saml.encrypted_assertion_from_string(decr_text)
assertions = []

# convert the extension elements in to Assertion instances
assers = extension_elements_to_elements(_seass.extension_elements,
                                        [saml, samlp])

# The signers (the IDPs) cert == public key
sign_cert_file = "pki/mycert.pem"

for ass in assers:
    _ass = "%s" % ass
    # verify the signature
    _flag = sec.verify_signature(_ass, sign_cert_file,
                                 node_name=class_name(assertion))
    if _flag:  # The signature was correct
        assertions.append(ass)

for a in assertions:
    print a
