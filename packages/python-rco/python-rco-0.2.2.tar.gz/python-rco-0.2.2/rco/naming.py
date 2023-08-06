# -*- coding: utf-8 -*-

import cherrypy
from cherrypy.lib import xmlrpcutil
_xmlrpclib = xmlrpcutil.get_xmlrpclib ()

import time
from pkg_resources import parse_version
from . import errors
from . import client


class LookupError (errors.BaseError):
    pass


class NamingEntry (object):

    def __init__ (self, code, security_manager, raw_entry):
        self.code = code
        self.security_manager = security_manager
        self.url, self.fingerprint, self.version = raw_entry
        self.timestamp = time.time ()
        self.parsed_version = parse_version (self.version or '0.0.0')

    def valid (self, cache_time):
        return time.time () - self.timestamp < cache_time

    def suitable (self, code, parsed_version):
        return self.code == code \
            and self.parsed_version >= parsed_version \
            and self.security_manager.public_key_exists (self.fingerprint)

    def dump (self):
        return (self.url, self.fingerprint, self.version)

    def __repr__ (self):
        return '<NamingEntry code={}, url={}, version={}, fingerprint={}, timestamp={}>'.format (
            self.code,
            self.url,
            self.version,
            self.fingerprint,
            self.timestamp
        )


class NamingProxy (object):

    def __init__ (self, service):
        self.own_url = service.service_config ('naming.own_url', strict = True)
        self.cache = []
        self.cache_time = service.service_config ('naming.cache_time', 600)
        self.security_manager = service.security_manager
        self.routing_entry = NamingEntry (
            'routing',
            self.security_manager,
            [
                service.service_config ('naming.routing_url', strict = True),
                service.service_config ('naming.routing_fingerprint', strict = True),
                None,
            ]
        )
        self.router = client.Service (
            uri = self.routing_entry.url,
            service_key = self.routing_entry.fingerprint,
            gpg_homedir = self.security_manager.homedir,
            gpg_key = self.security_manager.key,
            gpg_password = self.security_manager.password
        )
        if service.service_config ('naming.autoregister', False):
            engine = cherrypy.engine
            engine.starter_stopper.on_start.append (self.register)
            engine.starter_stopper.on_stop.append (self.unregister)

            interval = service.service_config ('naming.autoregister_interval', 0)
            if interval > 0:
                engine.task_manager.add (
                    '__{}_naming_autoregister__'.format (service.code),
                    self.register,
                    interval
                )

    def cleanup (self):
        self.cache = [entry for entry in self.cache if entry.valid (self.cache_time)]

    def find (self, code, version):
        return [entry for entry in self.cache if entry.suitable (code, version)]

    def lookup (self, code, version = None):
        if code == 'routing':
            return self.routing_entry.dump ()

        parsed_version = parse_version (version or '0.0.0')

        self.cleanup ()

        result = self.find (code, parsed_version)
        if not result:
            self.cache.extend (
                [NamingEntry (code, self.security_manager, raw) for raw in self.router.routing.naming.lookup (code, version)]
            )
        try:
            result = self.find (code, parsed_version)
            return result [0].dump ()
        except _xmlrpclib.Fault as e:
            if e.faultCode == -5005:
                raise LookupError (e.faultString, e.faultCode)
            raise

    def register (self):
        self.router.routing.naming.register (self.own_url)

    def unregister (self):
        self.router.routing.naming.unregister (self.own_url)
