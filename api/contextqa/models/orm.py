from sqlalchemy import Column, DateTime, func, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ORMBase(Base):
    """Base ORM"""

    __abstract__ = True

    created_at = Column(DateTime, default=func.current_timestamp())


class VectorStore(ORMBase):
    """Vector store types"""

    __tablename__ = "store"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)


class Index(ORMBase):
    """Indexes pertaining to a vector store type"""

    __tablename__ = "index"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    store_id = Column(Integer, ForeignKey("store.id"), nullable=False)


class Source(ORMBase):
    """Sources ingestes by users"""

    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    digest = Column(String(64), nullable=False)
    index_id = Column(Integer, ForeignKey("index.id"), nullable=False)
