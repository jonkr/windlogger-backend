from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from config import DB_URI

engine = None

Session = scoped_session(
        sessionmaker(
                autocommit=False,
                autoflush=False,
        )
)


class BaseModel(object):

    BASE_CASCADE = 'all, delete, delete-orphan'

    @classmethod
    def get_by_id(cls, *args):
        return cls.query.get(*args)

    def store(self, commit=True):
        session = get_session()
        session.add(self)
        if commit:
            try:
                session.commit()
            except:
                session.rollback()
                raise

    def delete(self):
        session = get_session()
        session.delete(self)
        try:
            session.commit()
        except:
            session.rollback()
            raise



Base = declarative_base(cls=BaseModel)
Base.query = Session.query_property()


def get_session():
    return Session()

def remove_session():
    Session.remove()


def init(db_uri=DB_URI):
    global engine
    engine = create_engine(db_uri,
                           convert_unicode=True,
                           echo=False)
    Session.configure(bind=engine)
    Base.metadata.create_all(bind=engine)

def clear():
    Base.metadata.drop_all(bind=engine)
