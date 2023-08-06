from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from morfdict import StringDict

from hatak.plugin import Plugin, RequestPlugin

from .driver import Driver


class SqlPlugin(Plugin):

    def __init__(self, fixturecls=None):
        super().__init__()
        self.groups = []
        self.fixture = fixturecls(self) if fixturecls else None

    def append_settings(self):
        def morf_sql_url(obj, value):
            if obj['type'] == 'sqlite':
                value = 'sqlite:///%(paths:sqlite_db)s'
            else:
                value = (
                    '%(type)s://%(login)s:%(password)s@%(host)s:%(port)s/'
                    '%(name)s'
                )
            return value % obj

        def morf_main_sql_url(obj, url):
            if obj['type'] == 'sqlite':
                return 'sqlite:///%(paths:sqlite_db)s' % obj
            else:
                return (
                    '%(type)s://%(login)s:%(password)s@%(host)s:%(port)s'
                    '/postgres'
                    % obj
                )
        dbsettings = self.settings.get('db', StringDict())
        dbsettings['url'] = ''
        dbsettings.set_morf('url', morf_sql_url)
        dbsettings['mainurl'] = ''
        dbsettings.set_morf('mainurl', morf_main_sql_url)
        self.settings['db'] = dbsettings

    def add_to_registry(self):
        engine = create_engine(self.settings['db:url'])
        self.config.registry['db_engine'] = engine
        self.config.registry['db'] = sessionmaker(bind=engine)()

    def add_request_plugins(self):
        if self.settings['db']['url'].startswith('sqlite'):
            self.add_request_plugin(SqliteRequestPlugin)
        else:
            self.add_request_plugin(DatabaseRequestPlugin)
        self.add_request_plugin(DriverRequestPlugin)

    def add_unpackers(self):
        self.unpacker.add('db', lambda req: req.db)
        self.unpacker.add('query', lambda req: req.db.query)
        self.unpacker.add('driver', lambda req: req.driver)

    def add_group(self, group):
        self.groups.append(group)

    def interract_with(self, plugin):
        method = getattr(plugin, 'generate_drivers', None)
        if method:
            method(self)


class DatabaseRequestPlugin(RequestPlugin):

    def __init__(self):
        super().__init__('db')

    def return_once(self):
        db = self.registry['db']
        db.expire_all()
        return db


class SqliteRequestPlugin(DatabaseRequestPlugin):

    def return_once(self):
        engine = self.registry['db_engine']
        self.registry['db'] = sessionmaker(bind=engine)()
        return super().return_once()


class DriverRequestPlugin(RequestPlugin):

    def __init__(self):
        super().__init__('driver')

    def return_once(self):
        driver = Driver(self.request.db)
        for group in self.parent.groups:
            driver.add_group(group)
        return driver
