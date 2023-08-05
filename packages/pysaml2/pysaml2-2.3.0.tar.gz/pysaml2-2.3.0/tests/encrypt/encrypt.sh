#!/bin/sh
/opt/local/bin/xmlsec1 encrypt --pubkey-cert-pem ../../example/idp2/pki/mycert.pem \
    --session-key des-192 --xml-data pre_saml2_response.xml \
    --node-xpath '/*[local-name()="Response"]/*[local-name()="Assertion"]/*[local-name()="Subject"]/*[local-name()="EncryptedID"]/text()' \
    enc-element-3des-kt-rsa1_5.tmpl > enc_3des_rsa.out