from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Index, text, DateTime
from sqlalchemy.orm import declarative_base

from medex.services.database import get_db_engine, get_db_session

Base = declarative_base()


class Header(Base):
    __tablename__ = "header"
    name_id = Column(String, primary_key=True)
    measurement = Column(String)


class Patient(Base):
    __tablename__ = "patient"
    name_id = Column(String, primary_key=True)
    case_id = Column(String, primary_key=True)
    __table_args__ = (Index('idx_name_id_patient', 'name_id'), Index('idx_case_id_patient', 'case_id'))


class NameType(Base):
    __tablename__ = "name_type"
    key = Column(String, primary_key=True)
    type = Column(String)
    synonym = Column(String)
    description = Column(String)
    unit = Column(String)
    show = Column(String)


class TableNumerical(Base):
    __tablename__ = "examination_numerical"
    id = Column(Integer, primary_key=True)
    name_id = Column(String)
    case_id = Column(String)
    measurement = Column(String)
    date = Column(String)
    time = Column(String)
    key = Column(String, ForeignKey('name_type.key'))
    value = Column(Numeric)
    __table_args__ = (Index('idx_key_num', 'key'), Index('idx_name_id_num', 'name_id'))


class TableCategorical(Base):
    __tablename__ = "examination_categorical"
    id = Column(Integer, primary_key=True)
    name_id = Column(String)
    case_id = Column(String)
    measurement = Column(String)
    date = Column(String)
    time = Column(String)
    key = Column(String, ForeignKey('name_type.key'))
    value = Column(String)
    __table_args__ = (Index('idx_key_cat', 'key'), Index('idx_name_id_cat', 'name_id'))


class TableDate(Base):
    __tablename__ = "examination_date"
    id = Column(Integer, primary_key=True)
    name_id = Column(String)
    case_id = Column(String)
    measurement = Column(String)
    date = Column(String)
    time = Column(String)
    key = Column(String, ForeignKey('name_type.key'))
    value = Column(Date)
    __table_args__ = (Index('idx_key_date', 'key'), Index('idx_name_id_date', 'name_id'))


class Sessions(Base):
    __tablename__ = 'sessions'
    id = Column(String, primary_key=True)
    created = Column(DateTime)
    last_touched = Column(DateTime)


class SessionFilteredNameIds(Base):
    __tablename__ = 'session_filtered_name_ids'
    session_id = Column(String, ForeignKey('sessions.id'), primary_key=True)
    name_id = Column(String, primary_key=True)
    __table_args__ = tuple([Index('idx_session_filtered_name_ids_by_session_id', 'session_id')])


class SessionFilteredCaseIds(Base):
    __tablename__ = 'session_filtered_case_ids'
    session_id = Column(String, ForeignKey('sessions.id'), primary_key=True)
    case_id = Column(String, primary_key=True)
    __table_args__ = tuple([Index('idx_session_filtered_case_ids_by_session_id', 'session_id')])


class SessionNameIdsMatchingFilter(Base):
    __tablename__ = 'session_name_ids_matching_filter'
    session_id = Column(String, ForeignKey('sessions.id'), primary_key=True)
    name_id = Column(String, primary_key=True)
    filter = Column(String, primary_key=True)
    __table_args__ = tuple([Index('idx_session_name_ids_matching_filter_by_session_id', 'session_id')])


def drop_tables():
    Base.metadata.drop_all(get_db_engine())


def create_tables():
    Base.metadata.create_all(get_db_engine())


def check_if_tables_exists():
    table = ''
    result = get_db_session().execute(text("SELECT to_regclass('public.examination_numerical')"))
    for row in result:
        table = row[0]
    if table != 'examination_numerical':
        create_tables()
