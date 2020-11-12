import sys
import os
import bcrypt
import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker



sm_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
Base = declarative_base()


class Database:

    def __init__(self, log=None , username="nunet", password="nunet", database="nunet_db", host="localhost", port=5432):
        self.db = f'postgresql://{username}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(self.db)
        self.session = scoped_session(sessionmaker(bind=self.engine))()
        self.log = self._get_logger(log)
        self._create()

    @staticmethod
    def _get_logger(logger):
        if not logger:
            logging.basicConfig(stream=sys.stdout,
                                format="%(asctime)s - [%(levelname)8s] "
                                       "- %(name)s - %(message)s",
                                level=logging.INFO)
        return logging.getLogger("db_interface")

    def _create(self, drop=False):
        if drop:
            Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    @staticmethod
    def check_password(password, hashed):
        if not isinstance(password, bytes):
            password = password.encode()
        return bcrypt.checkpw(password, hashed )

    @staticmethod
    def hash_password(password):
        if not isinstance(password, bytes):
            password = password.encode()
        return bcrypt.hashpw(password, bcrypt.gensalt())


    def drop(self):
        Base.metadata.drop_all(bind=self.engine)

    def query(self, table, **kwargs):
        if kwargs:
            if "password" in kwargs and "email" in kwargs:
                entry = self.session.query(table).filter_by(
                    email=kwargs["email"]).first()
                if entry and self.check_password(kwargs["password"],
                                                 entry.password):
                    return entry
                else:
                    return None
            return self.session.query(table).filter_by(**kwargs).first()
        return self.session.query(table).first()


    def query_all(self, table, **kwargs):
        if kwargs:
            return self.session.query(table).filter_by(**kwargs).all()
        return self.session.query(table).all()
    def query_by_limit(self, table, offset,size ,order, **kwargs):
        if kwargs:
            return self.session.query(table).filter_by(**kwargs).order_by(order.desc())[offset:size]
        return self.session.query(table).order_by(order.desc())[offset:size]
    def _add(self, table, **kwargs):
        s=scoped_session(sessionmaker(bind=self.engine))()
        if self.query(table, **kwargs):
            return False
        try:
            new_entry = table(**kwargs)
            s.add(new_entry)
            s.commit()
            return True
        except Exception as e:
            s.rollback()
            self.log.error(e)
            return False

    def _update(self, table, where, **update):
        s=scoped_session(sessionmaker(bind=self.engine))()
        try:
            if not self.query(table, **where):
                return False
            s.query(table).filter_by(**where).update(update)
            s.commit()
            return True
        except Exception as e:
            s.rollback()
            self.log.error(e)
            return False

    def _delete(self, table, **kwargs):
        s=self.session
        try:
            entry = self.query(table, **kwargs)
            if not entry:
                return False
            s.delete(entry)
            s.commit()
            return True
        except Exception as e:
            s.rollback()
            self.log.error(e)
            return False

    def add(self, table, **kwargs):
        if not self._add(table, **kwargs):
            self.log.warning("Entry '{}' already exists in Table '{}'!".format(
                kwargs,
                table.__tablename__))
            return False
        return True

    def update(self, table, where, update):
        if not self._update(table, where, **update):
            self.log.warning("Entry '{}' not found in Table '{}'!".format(
                update,
                table.__tablename__))
            return False
        return True
    
    def refresh(self, obj):
        s=scoped_session(sessionmaker(bind=self.engine))()
        s.refresh(obj)

    def delete(self, table, **kwargs):
        if not self._delete(table, **kwargs):
            self.log.warning("Entry '{}' not found in Table '{}'!".format(
                kwargs,
                table.__tablename__))
            return False
        return True

    def print_table(self, table):
        for entry in self.query_all(table):
            self.log.info("\n" + str(entry))