from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import AbstractConcreteBase

from hatak.unpackrequest import unpack

DeclatativeBase = declarative_base()


def get_or_create(model, session, **kwargs):
    try:
        return session.query(model).filter_by(**kwargs).one()
    except NoResultFound:
        created = model(**kwargs)
        try:
            session.add(created)
            session.commit()
            return created
        except IntegrityError:
            session.rollback()
            return session.query(model).filter_by(**kwargs).one()


class Base(AbstractConcreteBase, DeclatativeBase):

    @classmethod
    def get_or_create(cls, *args, **kwargs):
        return get_or_create(cls, *args, **kwargs)

    @classmethod
    def _query(cls, db):
        return db.query(cls)

    @classmethod
    def get_all(cls, db):
        return cls._query(db).all()

    @classmethod
    def get_by_id(cls, db, id_):
        return cls._query(db).filter_by(id=id_).one()

    @classmethod
    def create(cls, db, *args, **kwargs):
        obj = cls(*args, **kwargs)
        db.add(obj)
        db.commit()
        return obj

    @classmethod
    def delete_by_id(cls, db, id_):
        obj = cls.get_by_id(db, id_)
        db.delete(obj)
        db.commit()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = None

    def assign_request(self, request):
        self.request = request
        unpack(self, request)

    def __repr__(self):
        return '%s (%d)' % (self.__class__.__name__, self.id)
