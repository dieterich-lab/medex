from sqlalchemy import Column, Integer, String, Date,  Numeric, ForeignKey, Index, text
from sqlalchemy.ext.declarative import declarative_base


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
    orders = Column(Integer)
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


def drop_tables(rdb):
    Base.metadata.drop_all(rdb)


def create_tables(rdb):
    Base.metadata.create_all(rdb)


def check_if_tables_exists(rdb):
    table = ''
    connection = rdb.connect()
    result = connection.execute(text("SELECT to_regclass('public.examination_numerical')"))
    for row in result:
        table = row[0]
    if table != 'examination_numerical':
        create_tables(rdb)

