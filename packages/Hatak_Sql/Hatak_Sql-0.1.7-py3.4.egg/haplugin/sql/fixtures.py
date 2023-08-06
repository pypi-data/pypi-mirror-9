class BaseFixtures(object):

    def __init__(self, db, application):
        self.db = db
        self.fixtures = {}
        self.application = application

    def create_all(self):
        self.make_all()
        return self.fixtures

    def _create(self, cls, **kwargs):
        obj = cls.get_or_create(self.db, **kwargs)
        data = self.fixtures.get(cls.__name__, {})
        data[kwargs['name']] = obj
        self.fixtures[cls.__name__] = data
        return obj

    def _create_nameless(self, cls, **kwargs):
        obj = cls.get_or_create(self.db, **kwargs)
        data = self.fixtures.get(cls.__name__, [])
        data.append(obj)
        self.fixtures[cls.__name__] = data
        return obj
