import os

from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hatak import _test_cache as CACHE
from hatak.testing import RequestFixture
from hatak.unpackrequest import unpack

from .models import Base
from .plugin import SqlPlugin
from .driver import Driver


class DatabaseFixture(RequestFixture):

    @fixture(scope="session")
    def raw_db(self, app):
        if 'db' not in CACHE:
            print('Recreating database...')
            database = DatabaseTestCreation(app.settings)
            database.recreate_database()

            engine, session = database.get_engine_and_session()

            print('Creating all tables...')
            database.create_all(engine)

            CACHE['db'] = engine, session

        return CACHE['db']

    @fixture
    def db(self, raw_db, request):
        db = raw_db[1]
        request.registry['db'] = db
        request.db = db
        unpack(self, request)
        return db

    @fixture(scope="session")
    def db_engine(self, raw_db):
        return raw_db[0]

    @fixture
    def driver(self, app, request):
        sql = app.get_plugin(SqlPlugin)
        request.driver = Driver(request.db)
        for group in sql.groups:
            request.driver.add_group(group)
        return request.driver

    @fixture
    def fixtures(self, db, app, driver):
        if 'fixtures' not in CACHE:
            print("Creating fixtures...")
            sql = app.get_plugin(SqlPlugin)
            if sql.fixture:
                sql.fixture.init_fixture(db, app)
                CACHE['fixtures'] = sql.fixture.create_all()
            else:
                CACHE['fixtures'] = None
        return CACHE['fixtures']


class DatabaseTestCreation(object):

    def __init__(self, settings):
        self.settings = settings

    def recreate_database(self, dburlkey='testurl'):
        if self.settings['db']['type'] == 'sqlite':
            self.recreate_sqlite_database()
            return
        url = self.settings['db'][dburlkey]
        engine = create_engine(url)

        connection = engine.connect()
        connection.execute("commit")
        connection.execute(
            "drop database if exists %(db:name)s" % (self.settings))
        connection.execute("commit")
        connection.execute("create database %(db:name)s" % (self.settings))
        connection.close()

    def recreate_sqlite_database(self):
        try:
            os.unlink(self.settings['db']['name'])
        except FileNotFoundError:
            pass

    def get_engine_and_session(self):
        url = self.settings['db']['url']
        engine = create_engine(url)
        session = sessionmaker(bind=engine)()
        return engine, session

    def create_all(self, engine):
        Base.metadata.bind = engine
        Base.metadata.create_all(engine)

    def init_db(self):
        engine, session = self.get_engine_and_session()
        self.create_all(engine)
        return session


class TemporaryDatabaseObject(object):

    def __init__(self, db, cls, prepere=None):
        self.db = db
        self.cls = cls
        self.obj = None
        self.prepere = prepere

    def __enter__(self):
        self.obj = self.cls()
        if self.prepere:
            self.prepere(self.obj)
        self.db.add(self.obj)
        self.db.commit()
        return self.obj

    def __exit__(self, type, value, traceback):
        self.obj.delete(self.db)
