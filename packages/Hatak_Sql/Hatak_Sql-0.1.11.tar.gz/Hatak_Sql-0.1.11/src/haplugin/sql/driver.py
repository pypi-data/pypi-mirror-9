class Driver(object):

    def __init__(self, db):
        self.db = db

    def add_group(self, group):
        setattr(self, group.name, group)
        group.init(self.db)


class DriverGroup(object):

    def init(self, db):
        self.db = db
        self.query = db.query


class SqlDriver(DriverGroup):

    def get_by_id(self, id):
        return self.get_all().filter_by(id=id).one()

    def get_all(self):
        return self.query(self.model)

    def create(self, **kwargs):
        obj = self.model()
        for key, value in kwargs.items():
            setattr(obj, key, value)
        return obj
