from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from contextqa import settings


engine = create_engine(settings.sqlalchemy_url, pool_pre_ping=True, max_overflow=15)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
