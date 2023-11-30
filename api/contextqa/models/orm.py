from sqlalchemy import Column, DateTime, func, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ORMBase(Base):
    __abstract__ = True

    created_at = Column(DateTime, default=func.current_timestamp())


class Source(ORMBase):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    digest = Column(String(64), nullable=False)
