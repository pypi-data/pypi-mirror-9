# -*- coding: utf-8 -*-

import sqlalchemy.schema as sas
import sqlalchemy.types as sat
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.sql as sql
import regnupg
from cherrybase import orm
import cherrypy
import logging
from . import errors


BaseMdl = declarative_base ()


class _RightsMdl (BaseMdl):

    __tablename__ = 'rights'

    fingerprint = sas.Column (sat.String (50), primary_key = True, nullable = False)
    method = sas.Column (sat.Text, primary_key = True, nullable = False)

    def __init__ (self, fingerprint, method):
        self.fingerprint = fingerprint
        self.method = method


class Manager (object):

    pool_name_format = '__{}__security_manager__'

    def __init__ (self, service, gpg_homedir, gpg_key, gpg_password):

        cherrypy.log.error ('Starting security manager for %s' % service.code, context = 'RCO', severity = logging.INFO)

        self.service = service
        self.gpg = regnupg.GnuPG (homedir = gpg_homedir)
        self.homedir = gpg_homedir
        self.key = gpg_key
        self.password = gpg_password
        self.ifaces = {}
        self._update_keys ()

        # Готовим хранилище
        self.pool_name = self.pool_name_format.format (service.code)

        from cherrybase import db
        import cherrybase.orm.drivers.alchemy as alchemy

        # Создаем пул подключений к специальной БД
        db.auto_config (service.service_conf, self.pool_name, 'security_manager.db_')
        # Обертываем подключения в ORM
        alchemy.wrap (self.pool_name)
        # Достаем сессию алхимии из пула и создаем структуру БД
        session = orm.catalog.get (self.pool_name)
        cherrypy.log.error ('SM DB %s' % service.code, context = 'RCO', severity = logging.INFO)
        BaseMdl.metadata.create_all (session.bind)
        # Синхронизируем БД и содержимое ключницы (удаляем из БД упоминания о несуществующих ключах)
        session.query (_RightsMdl).filter (~_RightsMdl.fingerprint.in_ (self.keys.keys ())).delete (synchronize_session = False)
        session.commit ()
        orm.catalog.put (self.pool_name, session)

    def _update_keys (self):
        self.keys = {key: dict (data) for key, data in self.gpg.list_keys ().keys.iteritems ()}

    def _prepare_keys (self, keys):
        if isinstance (keys, basestring):
            keys = [keys]
        for k in keys:
            if len (k) < 8:
                raise errors.SecurityError ('Key id too short: %s' % k)
        return keys

    def _prepare_methods (self, methods):
        return [methods] if isinstance (methods, basestring) else methods

    def _validate_keys (self, keys):
        '''Проверка переданных ключей на предмет нахождения в ключнице'''
        self._update_keys ()
        keys = self._prepare_keys (keys)
        for key in keys:
            if not self.public_key_exists (key):
                raise ValueError ('Unknown gpg key: %s' % key)
        return keys

    def _get_fingerprints (self, keys):
        '''Получение отпечатков ключей по их идентификаторам.
        На входе ожидаются проверенные методом _validate_keys() ключи.'''
        long_keys = []
        for key in keys:
            for item in self.keys.keys ():
                if item.endswith (key):
                    long_keys.append (item)
                    break
        # итоговая длина набора ключей должна совпадать с начальной
        if len (keys) != len (long_keys):
            raise ValueError ('Cannot locate fingerprints for given key-ids')
        return long_keys

    def _validate_methods (self, methods):
        ''' Проверка переданных методов (контроллеров) на предмет подключения к интерфейсу'''
        methods = self._prepare_methods (methods)
        # Список всех присоединенных к интерфейсу контроллеров
        controllers = []
        for key in self.ifaces.keys ():
            controllers += self.ifaces [key]
        # Непосредственно проверка существования контроллера для переданного метода
        for method in methods:
            found = False
            for controller in controllers:
                if method.endswith ('.'):
                    if controller.startswith (method):
                        found = True
                        break
                else:
                    if method == controller:
                        found = True
                        break

            if not found:
                raise ValueError ('Unknown method or namespace: %s' % method)

        return methods

    def connect_interface (self, iface):
        from interfaces import CryptoInterface
        if not isinstance (iface, CryptoInterface):
            raise ValueError ('Interface is not instance of rco.CryptoInterface')
        self.ifaces [iface._mount_point] = iface.system.methods.keys ()

    def grant (self, methods, keys):
        """ Добавление прав производится в рамках транзакции. В случае какой-либо ошибки (например,
        не найден метод или ключ) никаких прав выдано не будет - будет возвращено сообщение об ошибке.
        """
        session = orm.catalog.get (self.pool_name)
        keys = self._validate_keys (keys)
        # т.к. отпечатки будем заносить в БД безопасности, то получаем их
        # в то время, как от клиента может прийти идентификатор ключа
        keys = self._get_fingerprints (keys)
        methods = self._validate_methods (methods)
        for method in methods:
            for key in keys:
                if session.query (_RightsMdl).filter (
                    sql.and_ (
                        _RightsMdl.fingerprint == key,
                        sql.or_ (
                            sql.and_ (~_RightsMdl.method.endswith ('.'), _RightsMdl.method == method),
                            sql.and_ (_RightsMdl.method.endswith ('.'), sql.expression.literal (method).startswith (_RightsMdl.method))
                        )
                    )
                ).count () == 0:
                    session.add (_RightsMdl (key, method))
        session.commit ()
        orm.catalog.put (self.pool_name, session)

    def revoke (self, methods, keys):
        session = orm.catalog.get (self.pool_name)
        keys = self._validate_keys (keys)
        methods = self._prepare_methods (methods)
        for method in methods:
            for key in keys:
                session.query (_RightsMdl).filter (
                    sql.and_ (
                        _RightsMdl.fingerprint.endswith (key),
                        sql.or_ (
                            sql.and_ (~sql.expression.literal (method).endswith ('.'), _RightsMdl.method == method),
                            sql.and_ (sql.expression.literal (method).endswith ('.'), _RightsMdl.method.startswith (method))
                        )
                    )
                ).delete (synchronize_session = 'fetch')
        session.commit ()
        orm.catalog.put (self.pool_name, session)

    def rights (self, methods = None, keys = None):
        if not (methods or keys):
            return {}

        session = orm.catalog.get (self.pool_name)
        result = {}

        if keys:
            keys = self._validate_keys (keys)
            for key in keys:
                result [key] = []
                for row in session.query (_RightsMdl.method.label ('method')).filter (_RightsMdl.fingerprint.endswith (key)).all ():
                    result [key].append (row.method)

        if methods:
            methods = self._validate_methods (methods)
            for method in methods:
                result [method] = []
                for row in session.query (_RightsMdl.fingerprint.label ('key')).filter (
                    sql.or_ (
                        sql.and_ (~_RightsMdl.method.endswith ('.'), _RightsMdl.method == method),
                        sql.and_ (_RightsMdl.method.endswith ('.'), sql.expression.literal (method).startswith (_RightsMdl.method))
                    )
                ).all ():
                    result [method].append (row.key)

        session.rollback ()
        orm.catalog.put (self.pool_name, session)
        return result

    def delete_keys (self, keys):
        # т.к. из БД безопасности будем удалять отпечатки, то получаем их
        # в то время, как от клиента может прийти идентификатор ключа
        keys = self._validate_keys (keys)
        keys = self._get_fingerprints (keys)
        own_key = self.key if len (self.key) != 8 else self._get_fingerprints ([self.key, ]) [0]
        if own_key in keys:
            raise errors.SecurityError ('Cannot manipulate with my own gpg key: %s' % self.key, -2000)
        self.gpg.delete_keys (keys)
        session = orm.catalog.get (self.pool_name)
        session.query (_RightsMdl).filter (_RightsMdl.fingerprint.in_ (keys)).delete (synchronize_session = False)
        session.commit ()
        orm.catalog.put (self.pool_name, session)
        self._update_keys ()

    def import_keys (self, armored):
        result = self.gpg.import_keys (armored)
        self._update_keys ()
        return {res.fingerprint: (res.imported, res.result_text if res.imported else res.problem_text) for res in result.results}

    def export_keys (self, keys):
        ''' Экспортирует открытые ключи (в .т.ч. свой собственный) в armored-формате'''
        return self.gpg.export_keys (self._prepare_keys (keys)).data

    def can_execute (self, iface, method):
        request = cherrypy.request

        # Своему собственному ключу даем права на все
        if self.key.endswith (request.rco_client):
            return True

        session = orm.catalog.get (self.pool_name)

        cnt = session.query (_RightsMdl).filter (
            sql.and_ (
                _RightsMdl.fingerprint.endswith (request.rco_client),
                sql.or_ (
                    sql.and_ (~_RightsMdl.method.endswith ('.'), _RightsMdl.method == method),
                    sql.and_ (_RightsMdl.method.endswith ('.'), sql.expression.literal (method).startswith (_RightsMdl.method))
                )
            )
        ).count ()

        session.rollback ()
        orm.catalog.put (self.pool_name, session)

        return cnt != 0

    def public_key_exists (self, key):
        return self.gpg.key_exists (key)

    def encrypt (self, data, recipient_key):
        result = self.gpg.encrypt (data, recipient_key, self.key, self.password, always_trust = True)
        return result.data

    def decrypt (self, encrypted, correspondent_key):
        result = self.gpg.decrypt (encrypted, self.password, correspondent_key, always_trust = True)
        return result.data

