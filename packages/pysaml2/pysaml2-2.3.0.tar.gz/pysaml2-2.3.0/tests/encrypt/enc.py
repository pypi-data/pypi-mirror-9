__author__ = 'roland'

com_list = [xmlpath, "encrypt", "--pubkey-cert-pem", enc_key,
            "--session-key", key_type, "--xml-data", fil,
            "--node-xpath", ASSERT_XPATH]

(_stdout, _stderr, output) = self._run_xmlsec(com_list, [tmpl],
                                              exception=EncryptError,
                                              validate_output=False)
