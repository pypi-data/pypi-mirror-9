# coding=utf-8
from saml2.authn_context import INTERNETPROTOCOLPASSWORD
from saml2 import saml
from saml2 import samlp
from saml2.server import Server

__author__ = 'roland'

AUTHN = {
    "class_ref": INTERNETPROTOCOLPASSWORD,
    "authn_auth": "http://www.example.com/login"
}


def test():
    server = Server("eduid")

    ava = {u'displayName': u'Stefan Liström',
           u'eduPersonPrincipalName': u'ginon-sukuh@eduid.se',
           u'givenName': u'Stefan',
           u'mail': u'stefan@listrom.se',
           "sn": u'Liström',
           'eduPersonScopedAffiliation': "staff@example.com",
    #       'eduPersonAffiliation': "staff"
    }

    npolicy = samlp.NameIDPolicy(format=saml.NAMEID_FORMAT_TRANSIENT,
                                 allow_create="true")

    resp = server.create_authn_response(
        ava, "_f49f31e0951e6ad3665b07499ad1f962",
        "https://connect.sunet.se/Shibboleth.sso/SAML2/POST" ,
        'https://connect.sunet.se/shibboleth',
        npolicy, '532d7e9d1fb33aeefd88a33e', authn=AUTHN)

    print resp

if __name__ == "__main__":
    test()