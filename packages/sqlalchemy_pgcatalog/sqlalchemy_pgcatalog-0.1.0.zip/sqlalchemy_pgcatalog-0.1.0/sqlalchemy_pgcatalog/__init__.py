"""SQLAlchemy schema definition (partially reflected) for the PostgreSQL catalog (pg_catalog
schema)

This module has been developed for PostgreSQL 9.3. It may work with later versions.

Call the prepare function to reflect the DB before using.
"""


from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base, DeferredReflection
from sqlalchemy.orm import relationship, foreign, remote

Base = declarative_base(cls=DeferredReflection)


Oid = Integer


class AuthMember(Base):
    __tablename__ = "pg_auth_members"

    roleid = Column(Integer, ForeignKey('pg_roles.oid'), primary_key=True)
    member = Column(Integer, ForeignKey('pg_roles.oid'), primary_key=True)
    grantor = Column(Integer, ForeignKey('pg_roles.oid'))

    
class Role(Base):
    __tablename__ = "pg_roles"
    oid = Column(Integer, primary_key=True)
    groups = relationship("Role",
                          secondary=AuthMember.__table__,
                          primaryjoin=(oid == AuthMember.member),
                          secondaryjoin=(oid == AuthMember.roleid),
                          backref="members")


class Namespace(Base):
    __tablename__ = "pg_namespace"
    oid = Column(Integer, primary_key=True)


class Class(Base):
    __tablename__ = "pg_class"
    oid = Column(Integer, primary_key=True)
    relnamespace = Column(Oid, ForeignKey(Namespace.oid))
    namespace = relationship(Namespace, backref="classes")


class Activity(Base):
    __tablename__ = "pg_stat_activity"

    pid = Column(Integer, primary_key=True)


class StatDatabase(Base):
    __tablename__ = "pg_stat_database"

    datid = Column(Integer, primary_key=True)


class StatBgWriter(Base):
    __tablename__ = "pg_stat_bgwriter"

    stats_reset = Column(DateTime, primary_key=True)  # table always contains a single row


class StatUserTables(Base):
    __tablename__ = "pg_stat_user_tables"

    relid = Column(Integer, primary_key=True)


class StatUserIndexes(Base):
    __tablename__= "pg_stat_user_indexes"

    relid = Column(Integer, primary_key=True)


class StatIOUserTables(Base):
    __tablename__ = "pg_statio_user_tables"

    relid = Column(Integer, primary_key=True)


class StatIOUserIndexes(Base):
    __tablename__ = "pg_statio_user_indexes"

    relid = Column(Integer, primary_key=True)


class StatIOUserSequences(Base):
    __tablename__ = "pg_statio_user_sequences"

    relid = Column(Integer, primary_key=True)


class StatReplication(Base):
    __tablename__ = "pg_stat_replication"

    pid = Column(Integer, primary_key=True)


class Database(Base):
    __tablename__ = "pg_database"

    oid = Column(Oid, primary_key=True)


class Lock(Base):
    __tablename__ = "pg_locks"

    locktype = Column(Text, primary_key=True)
    database = Column(Oid, primary_key=True)
    relation = Column(Oid, ForeignKey("pg_class.oid"), primary_key=True)
    page = Column(Integer, primary_key=True)
    tuple = Column(SmallInteger, primary_key=True)
    virtualxid = Column(Text, primary_key=True)
    transactionid = Column(Text, primary_key=True)  # type - xid
    classid = Column(Oid, ForeignKey("pg_class.oid"), primary_key=True)
    objid = Column(Oid, primary_key=True)  # any OID column
    objsubid = Column(SmallInteger, primary_key=True)
    virtualtransaction = Column(Text, primary_key=True)
    pid = Column(Integer, primary_key=True)
    mode = Column(Text, primary_key=True)
    granted = Column(Boolean)
    fastpath = Column(Boolean)

    relation_obj = relationship(Class, backref="relation_locks", foreign_keys=relation)
    class_obj = relationship(Class, backref="class_locks", foreign_keys=classid)
    activity = relationship(Activity, backref="locks",
                            primaryjoin=(foreign(pid) == remote(Activity.pid)))

    def tuple_data(self):
        """Get the locked row, for tuple locks"""
        
        if self.locktype != "tuple":
            raise ValueError("Not a tuple lock")

        return self._sa_instance_state.session.execute(
            "SELECT * FROM {}.{} WHERE ctid = '({},{})'".format(
                self.relation_obj.namespace.nspname,
                self.relation_obj.relname,
                self.page,
                self.tuple)).first()


def prepare(engine):
    """Call before using any of the declaratively defined schema classes in this module"""

    Base.prepare(engine)
