from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, String, Text, ForeignKey, JSON
from uuid import uuid4


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True)
    sso_provider = Column(String)