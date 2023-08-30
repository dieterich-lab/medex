from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Index, DateTime
from sqlalchemy.orm import declarative_base

from medex.services.database import get_db_engine

Base = declarative_base()


class HeaderTable(Base):
    __tablename__ = 'header'
    patient_id = Column(String, primary_key=True)
    measurement = Column(String)


class PatientTable(Base):
    __tablename__ = 'patient'
    patient_id = Column(String, primary_key=True)
    case_id = Column(String, primary_key=True)
    __table_args__ = (Index('idx_patient_id_patient', 'patient_id'), Index('idx_case_id_patient', 'case_id'))


class EntityTable(Base):
    __tablename__ = 'entity'
    key = Column(String, primary_key=True)
    type = Column(String)
    synonym = Column(String)
    description = Column(String)
    unit = Column(String)


class NumericalValueTable(Base):
    __tablename__ = 'numerical_value'
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    case_id = Column(String)
    measurement = Column(String)
    date_time = Column(DateTime)
    key = Column(String, ForeignKey('entity.key'))
    value = Column(Numeric)
    __table_args__ = (Index('idx_key_num', 'key'), Index('idx_patient_id_num', 'patient_id'))


class CategoricalValueTable(Base):
    __tablename__ = 'categorical_value'
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    case_id = Column(String)
    measurement = Column(String)
    date_time = Column(DateTime)
    key = Column(String, ForeignKey('entity.key'))
    value = Column(String)
    __table_args__ = (Index('idx_key_cat', 'key'), Index('idx_patient_id_cat', 'patient_id'))


class DateValueTable(Base):
    __tablename__ = 'date_value'
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    case_id = Column(String)
    measurement = Column(String)
    date_time = Column(DateTime)
    key = Column(String, ForeignKey('entity.key'))
    value = Column(Date)
    __table_args__ = (Index('idx_key_date', 'key'), Index('idx_patient_id_date', 'patient_id'))


class SessionTable(Base):
    __tablename__ = 'session'
    id = Column(String, primary_key=True)
    created = Column(DateTime)
    last_touched = Column(DateTime)


class SessionFilteredPatientTable(Base):
    __tablename__ = 'session_filtered_patient'
    session_id = Column(String, ForeignKey('session.id'), primary_key=True)
    patient_id = Column(String, primary_key=True)
    __table_args__ = tuple([Index('idx_session_filtered_patient_ids_by_session_id', 'session_id')])


class SessionFilteredCaseIdTable(Base):
    __tablename__ = 'session_filtered_case_id'
    session_id = Column(String, ForeignKey('session.id'), primary_key=True)
    case_id = Column(String, primary_key=True)
    __table_args__ = tuple([Index('idx_session_filtered_case_ids_by_session_id', 'session_id')])


class SessionPatientsMatchingFilterTable(Base):
    __tablename__ = 'session_patients_matching_filter'
    session_id = Column(String, ForeignKey('session.id'), primary_key=True)
    patient_id = Column(String, primary_key=True)
    filter = Column(String, primary_key=True)
    __table_args__ = tuple([Index('idx_session_patient_ids_matching_filter_by_session_id', 'session_id')])


def drop_tables():
    Base.metadata.drop_all(get_db_engine())


def create_tables():
    Base.metadata.create_all(get_db_engine())
