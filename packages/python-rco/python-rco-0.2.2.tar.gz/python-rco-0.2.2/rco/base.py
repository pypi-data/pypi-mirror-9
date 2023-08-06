# -*- coding: utf-8 -*-

import cherrypy
import cherrybase
import pkg_resources
from cherrypy import _cpconfig
from . import security
from . import interfaces


def config (name, default = None, strict = False):
    '''
    Получить значение настройки приложения.
    Может быть использован только в рамках обработчика запроса.
    
    :param name: Имя настройки
    :param default: Значение по умолчанию
    :param strict: Если True, то выбросить исключение при отсутствии параметра
    :returns: Значение параметра
    '''
    app = cherrypy.request.app
    return app.service.service_config (name, default, strict)


def prepare_config (conf, package):
    '''
    Метод подготовки конфигурации сервиса.
    Ищет и заменяет в значениях конфигурации {PKG_PATH} на путь к пакету.
    
    :param conf: dict конфигурации
    :param package: имя пакета приложения (сервиса)
    '''
    def replace (str):
        return str.replace ('{PKG_PATH}', pkg_path).replace ('{PKG_NAME}', package)

    pkg_path = pkg_resources.resource_filename (package, '')
    if isinstance (conf, list):
        for item in conf:
            if isinstance (item, basestring):
                item = replace (item)
            elif isinstance (item, (dict, list)):
                prepare_config (item, package)
    elif isinstance (conf, dict):
        for key in conf:
            if isinstance (conf [key], basestring):
                conf [key] = replace (conf [key])
            elif isinstance (conf [key], (dict, list)):
                prepare_config (conf [key], package)


class Service (cherrybase.Application):
    '''
    Базовый класс сервиса.
    Все приложения, выполненные в рамках облачной концепции RCO,
    должны базироваться на этом классе вместо cherrybase.Application 
    '''
    def __init__ (self, package, basename, mode, root = None, config = None):
        '''
        Инициализатор сервиса.
        
        :param package: Имя пакета сервиса.
        :param basename: Базовое имя виртуального хоста сервиса. 
            Будет добавлено к тем виртуальным хостам, которые заканчиваются точкой (``.``)
        :param mode: Режим работы сервиса (``'debug'`` или ``'production'``).
        :param root: Класс/фабрика корневого интерфейса сервиса, обычно наследник :py:class:`.CryptoInterface`.
            Инициализатору этого класса будет передан экземпляр менеджера безопасности :py:class:`security.SecurityManager`.
        :param config: Конфигурация сервиса как приложения cherrypy. Может быть dict, именем файла конфигурации
            или файловым объектом. Если None, то сервис будет искать файл конфигурации с именем
            'production.conf' или 'debug.conf' в подкаталоге '__config__' пакета сервиса, в зависимости
            от указанного режима работы сервиса.
            В переданной конфигурации производится поиск подстроки ``{PKG_PATH}`` во всех значениях и
            ее замена на полный путь к пакету сервиса. Сервис ожидает наличие раздела ``[service]`` в конфигурации
            и читает оттуда следующие параметры:
                
                :code: Мнемокод сервиса.
                :version: Версия сервиса.
                :title: Название сервиса.
                :vhosts: Строка или список строк виртуальных хостов сервиса.
                    Ко всем виртуальным хостам, заканчивающимся точкой, будет добавлено значение, переданное в параметре
                    ``basename``.
                :security.homedir: Каталог ключницы менеджера безопасности.
                :security.key: Отпечаток ключа сервиса.
                :security.password: Пароль приватного ключа сервиса.
            
            :naming...: Параметры клиента роутинга
        '''
        self.package = package

        # Готовим конфигурацию
        raw_config = {
            '/' : {
                'tools.encode.on': True,
                'tools.gzip.on': True,
                'tools.gzip.mime_types': ['text/*', 'application/pgp-encrypted']
            }
        }
        _cpconfig.merge (
            raw_config,
            config or pkg_resources.resource_filename (package, '__config__/{}.conf'.format (mode))
        )
        prepare_config (raw_config, package)

        self.service_conf = raw_config.get ('service', {})

        self.code = self.service_config ('code', package)
        self.vhosts = self.service_config ('vhosts', [self.code + '.'])
        if isinstance (self.vhosts, basestring):
            self.vhosts = [self.vhosts]

        sec_homedir = self.service_config ('security.homedir', strict = True)
        sec_key = self.service_config ('security.key', strict = True)
        sec_password = self.service_config ('security.password', strict = True)

        # Создаем менеджер безопасности
        self.security_manager = security.Manager (self, sec_homedir, sec_key, sec_password)

        _vhosts = [vhost + basename if vhost.endswith ('.') else vhost for vhost in self.vhosts]
        self.main_name = _vhosts [0] + '/'

        # Создаем клиента роутинга
        if self.service_config ('naming.on', True):
            from . import naming
            self.naming = naming.NamingProxy (self)

        # Родительский конструктор
        super (Service, self).__init__ (
            name = self.code,
            vhosts = _vhosts,
            config = raw_config
        )
        self.app.service = self
        if root:
            self.tree.add ('/', root (self.security_manager))
            self.add_meta ()

    def add_meta (self, path = '/meta'):
        '''
        Добавление в сервис стандартного нешифрованного интерфейса ``meta``.
        Интерфейс по умолчанию монтируется на URI ``/meta``.
        '''
        self.tree.add (
            path,
            interfaces.MetaInterface (
                self.security_manager,
                code = self.code,
                version = self.service_config ('version', '1.0.0'),
                title = self.service_config ('title', self.code)
            )
        )

    def service_config (self, name, default = None, strict = False):
        '''
        Получение значение параметра конфигурации сервиса из раздела ``[service]``.
        
        :param name: Имя параметра
        :param default: Значение по умолчанию
        :param strict: Генерировать KeyError, если параметр не найден.
        :return: Значение параметра конфигурации
        '''
        if strict and name not in self.service_conf:
            raise KeyError ('Service config value "{}" is not found'.format (name))
        return self.service_conf.get (name, default)

    def url (self, method_name = None):
        '''
        Получение полного URL сервиса.
        
        :param method_name: Имя метода. Если отсутствует, будет возвращен общий URL сервиса.
        :return: URL
        :rtype: str
        '''
        return ('http://{}:{}' if method_name else 'http://{}').format (self.main_name, method_name)

