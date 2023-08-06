# -*- coding: utf-8 -*-

from cherrypy.process.plugins import SimplePlugin


class ExceptionsCounter (SimplePlugin):

    def __init__ (self, bus):
        super (ExceptionsCounter, self).__init__ (bus)
        bus.exceptions_counter = self
        self.data = {}

    def start (self):
        self.bus.log ('ExceptionsCounter started')

    def stop (self):
        self.bus.log ('ExceptionsCounter stopped')

    def register (self, source, exception):
        key = type (exception)
        message = repr (exception)
        self.data [source] = self.data.get (source, {})
        self.data [source][key] = self.data [source].get (key, {})
        self.data [source][key][message] = self.data [source][key].get (message, 0)
        self.data [source][key][message] += 1
