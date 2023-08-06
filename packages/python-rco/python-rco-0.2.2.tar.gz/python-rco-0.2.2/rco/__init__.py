# -*- coding: utf-8 -*-

__version__ = '0.2.2'


from cherrypy.lib import xmlrpcutil
_xmlrpclib = xmlrpcutil.get_xmlrpclib ()


from . import base, client, tickets, security, tools, naming, plugins
from base import Service
from interfaces import CryptoInterface, MetaInterface, Namespace


import cherrypy
toolbox = cherrypy.tools
toolbox.encrypted_xmlrpc = tools.EncryptedXmlrpcTool ()


cherrypy.config.update ({
    'engine.starter_stopper.on': True,
    'engine.task_manager.on': True
})
