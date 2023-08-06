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
