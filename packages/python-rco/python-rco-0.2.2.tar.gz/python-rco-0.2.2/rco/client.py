# -*- coding: utf-8 -*-

import cherrypy
import pgpxmlrpc
from . import base


def lookup (code, version):
    request = cherrypy.serving.request
    if not request.app:
        raise LookupError ('Cannot execute simple lookup outside the request process', -4001)
    result = request.app.service.naming.lookup (code, version)
    return result [0:2]


def Service (uri, service_key, gpg_homedir = None, gpg_key = None, gpg_password = None, ticket = None, headers = {}):
    if ticket:
        headers.update ({'RCO-Ticket': ticket})
    return pgpxmlrpc.Service (
        uri = uri,
        service_key = service_key,
        gpg_homedir = gpg_homedir or base.config ('security.homedir', strict = True),
        gpg_key = gpg_key or base.config ('security.key', strict = True),
        gpg_password = gpg_password or base.config ('security.password', strict = True),
        headers = headers
    )


def get_service (service_code, version = None, ticket = None, headers = {}):
    url, key = lookup (service_code, version)
    return Service (url, key, ticket = ticket, headers = headers)

