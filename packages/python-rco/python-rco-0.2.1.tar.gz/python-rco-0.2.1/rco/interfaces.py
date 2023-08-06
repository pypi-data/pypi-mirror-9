# -*- coding: utf-8 -*-

import logging
import cherrypy
from cherrybase import rpc
from . import stdlib
from . import errors
from . import _xmlrpclib


class Namespace (object):
    '''
    Пространство имен XML-RPC интерфейса
    '''
    pass


class CryptoInterface (rpc.Controller):
    '''
    Базовый класс для всех шифрованных RPC-интерфейсов
    '''
    _cp_config = {
        'tools.encrypted_xmlrpc.on': True
    }

    def __init__ (self, security_manager, mount_point = '/'):
        '''
        Инициализатор интерфейса.
        
        :param security_manager: Менеджер безопасности, экземпляр класса :py:class:`rco.security.SecurityManager`.
            Интерфейс регистриует себя в менеджере безопасности и в дальнейшем использует его для проверки
            прав доступа к методам интерфейса и шифрования ответа.
            В случае нестандартной системы безопасности, можно использовать собственный объект
            с переопределенным поведением. 
        :param mount_point: Точка монтирования интерфейса.
        '''
        self._mount_point = mount_point
        self._security = security_manager
        self.control = Namespace ()
        self.control.keyring = stdlib.Keyring (self._security)
        self.control.access = stdlib.Access (self._security)
        self.callbacks = Namespace ()
        super (CryptoInterface, self).__init__ ()
        self._security.connect_interface (self)

    def _call_method (self, method, name, args, vpath, parameters):
        '''
        Непосредственно вызов RPC-метода интерфейса.
        Реализация по умолчанию проверяет права доступа клиента сервиса к RPC-методу
        путем вызова ``can_execute()`` менеджера безопасности интерфейса и, в случае 
        наличия прав, передает вызов в родительский метод ``cherrybase.rpc.Controller``.
        
        :param method: Callabale RPC-метода
        :param name: Полное имя вызываемого RPC-метода
        :param args: tuple аргументов вызываемого RPC-метода
        :param vpath: list, содержащий элементы пути метода (URI)
        :param parameters: GET-параметры из URL
        :return: Результат callable RPC-метода.
        '''
        app = cherrypy.request.app
        try:
            if not self._security.can_execute (self, name):
                raise errors.SecurityError ('Access denied', -1000)
            return super (CryptoInterface, self)._call_method (method, name, args, vpath, parameters)
        except Exception as e:
            engine = cherrypy.engine
            if hasattr (engine, 'exceptions_counter'):
                engine.exceptions_counter.register (app.service.code, e)
            raise

    def default (self, *vpath, **params):
        '''
        Обработчик клиентского запроса по умолчанию.
        В момент его отработки тело POST-запроса уже расшифровано и находится
        в ``cherrypy.request.rco_decrypted``.
        Обработчик разбирает XML-RPC запрос, расположенный в теле POST,
        отыскивает подходящий обработчик, вызывает его (см. :py:meth:`_call_method`).
        Результат выполнения обработчика транслируется в XML-RPC method response,
        шифруется менеджером безопасности и помещается в ``cherrypy.response``.
        '''
        request = cherrypy.request
        response = cherrypy.response

        try:
            rpc_params, rpc_method = _xmlrpclib.loads (request.rco_decrypted, use_datetime = 1)
        except:
            request.app.log.error ('Invalid request', 'RPC', logging.WARNING, True)
            raise errors.RequestError ('Invalid request', -32700)

        request.app.log.error ('Call {} {}'.format (rpc_method, rpc_params), 'RPC', logging.INFO, True)

        method = self._find_method (rpc_method)
        if method is not None:
            result = self._call_method (method, rpc_method, rpc_params, vpath, params)
        else:
            raise errors.MethodError ('Method "%s" not found' % rpc_method)

        body = self._security.encrypt (
            _xmlrpclib.dumps (
                (result,),
                methodresponse = 1,
                encoding = 'utf-8',
                allow_none = 1
            ),
            request.rco_client
        )

        response.status = '200 OK'
        response.headers ['Content-Type'] = 'application/pgp-encrypted'
        response.headers ['Content-Length'] = len (body)
        response.body = body
        return body

    default.exposed = True


class MetaInterface (rpc.Controller):
    '''
    Стандартный нешифрованный интерфейс meta
    '''
    _cp_config = {
        'tools.encrypted_xmlrpc.on': False,
        'tools.xmlrpc.on': True,
        'tools.xmlrpc.allow_none': True,
    }

    def __init__ (self, security_manager, code = None, version = None, title = None):
        '''
        :param security_manager: Менеджер безопасности
        :param code: Мнемокод сервиса
        :param version: Версия сервиса
        :param title: Название сервиса
        '''
        self.meta = stdlib.Meta (security_manager, code, version, title)
        super (MetaInterface, self).__init__ ()


