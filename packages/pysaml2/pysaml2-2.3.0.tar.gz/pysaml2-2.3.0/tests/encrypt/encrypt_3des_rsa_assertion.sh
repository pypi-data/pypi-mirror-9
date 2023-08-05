#!/bin/bash
/opt/local/bin/xmlsec1 encrypt --pubkey-cert-pem ../../example/idp2/pki/mycert.pem \
    --session-key des-192 --xml-data pre_assertion_enc.xml \
    --node-xpath '/*[local-name()="Response"]/*[local-name()="EncryptedAssertion"]/*[local-name()="Assertion"]' \
    enc-element-3des-kt-rsa1_5.tmpl > enc_3des_rsa_assertion.xml