import logging
import os
import re
import argparse

from urlparse import parse_qs
from saml2 import server

from saml2.authn_context import AuthnBroker, PASSWORD, UNSPECIFIED
from saml2.authn_context import authn_context_class_ref
from saml2.metadata import create_metadata_string
from service import not_found
from service import Cache
from service import do_verify_pwd
from service import info_from_cookie
from service import AUTHN_URLS
from service import NON_AUTHN_URLS

from idp_user import USERS
from idp_user import EXTRA

logger = logging.getLogger("saml2.idp")

__author__ = 'roland'


NON_AUTHN_URLS.extend([
    (r'verify_cas?(.*)$', do_verify_cas),
    (r'verify_cas?(.*)$', do_verify_pwd),
])


def metadata(environ, start_response):
    try:
        path = args.path
        if path is None or len(path) == 0:
            path = os.path.dirname(os.path.abspath( __file__ ))
        if path[-1] != "/":
            path += "/"
        metadata = create_metadata_string(path+args.config, IDP.config,
                                          args.valid, args.cert, args.keyfile,
                                          args.id, args.name, args.sign)
        start_response('200 OK', [('Content-Type', "text/xml")])
        return metadata
    except Exception as ex:
        logger.error("An error occured while creating metadata:" + ex.message)
        return not_found(environ, start_response)


def application(environ, start_response):
    """
    The main WSGI application. Dispatch the current request to
    the functions from above and store the regular expression
    captures in the WSGI environment as  `myapp.url_args` so that
    the functions from above can access the url placeholders.

    If nothing matches call the `not_found` function.

    :param environ: The HTTP application environment
    :param start_response: The application to run when the handling of the
        request is done
    :return: The response as a list of lines
    """

    path = environ.get('PATH_INFO', '').lstrip('/')

    environ["pysaml2.idp"] = IDP
    environ["pysaml2.userinfo"] = USERS
    environ["pysaml2.userinfo.extra"] = EXTRA
    environ["pysaml2.authn_broker"] = AUTHN_BROKER
    environ["pysaml2.mako.lookup"] = LOOKUP

    if path == "metadata":
        return metadata(environ, start_response)

    kaka = environ.get("HTTP_COOKIE", None)
    logger.info("<application> PATH: %s" % path)

    if kaka:
        logger.info("= KAKA =")
        user, authn_ref = info_from_cookie(kaka, IDP)
        environ["idp.authn_ref"] = authn_ref
    else:
        try:
            query = parse_qs(environ["QUERY_STRING"])
            logger.debug("QUERY: %s" % query)
            user = IDP.cache.uid2user[query["id"][0]]
        except KeyError:
            user = None

    url_patterns = AUTHN_URLS
    if not user:
        logger.info("-- No USER --")
        # insert NON_AUTHN_URLS first in case there is no user
        url_patterns = NON_AUTHN_URLS + url_patterns

    for regex, callback in url_patterns:
        match = re.search(regex, path)
        if match is not None:
            try:
                environ['myapp.url_args'] = match.groups()[0]
            except IndexError:
                environ['myapp.url_args'] = path

            logger.debug("Callback: %s" % (callback,))
            if isinstance(callback, tuple):
                cls = callback[0](environ, start_response, user)
                func = getattr(cls, callback[1])
                return func()
            return callback(environ, start_response, user)

    return not_found(environ, start_response)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    import socket
    from wsgiref.simple_server import make_server
    from mako.lookup import TemplateLookup

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', dest='path', help='Path to configuration file.')
    parser.add_argument('-v', dest='valid',
                        help="How long, in days, the metadata is valid from the time of creation")
    parser.add_argument('-c', dest='cert', help='certificate')
    parser.add_argument('-i', dest='id',
                        help="The ID of the entities descriptor")
    parser.add_argument('-k', dest='keyfile',
                        help="A file with a key to sign the metadata with")
    parser.add_argument('-n', dest='name')
    parser.add_argument('-s', dest='sign', action='store_true',
                        help="sign the metadata")
    parser.add_argument('-m', dest='mako_root', default="./")
    parser.add_argument(dest="config")
    args = parser.parse_args()

    _rot = args.mako_root
    LOOKUP = TemplateLookup(directories=[_rot + 'templates', _rot + 'htdocs'],
                            module_directory=_rot + 'modules',
                            input_encoding='utf-8', output_encoding='utf-8')

    PORT = 8088

    AUTHN_BROKER = AuthnBroker()
    AUTHN_BROKER.add(authn_context_class_ref(PASSWORD),
                     cas, 10,
                     "http://%s" % socket.gethostname())
    AUTHN_BROKER.add(authn_context_class_ref(UNSPECIFIED),
                     "", 0, "http://%s" % socket.gethostname())

    IDP = server.Server(args.config, cache=Cache())
    IDP.ticket = {}

    SRV = make_server('', PORT, application)
    print "IdP listening on port: %s" % PORT
    SRV.serve_forever()
