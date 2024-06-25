from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, String, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from typing import List
from uuid import uuid4

db_string = r"z~)#7uUw.Zn}y}#$fp27sGX%aG[s"

DATABASE_URL = "postgresql://postgres:"+db_string+"@trcapi.c1e6s6gqgubd.us-east-1.rds.amazonaws.com/apidb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# class Message(Base):
#     __tablename__ = "messages"
#     id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
#     chat_id = Column(String, ForeignKey("chats.id"))
#     sender = Column(String)
#     content = Column(Text)
#     chat = relationship("Chat", back_populates="messages")

class Chat(Base):
    __tablename__ = 'chats'
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid4()))
    messages = Column(JSON)
    owner = Column(String)

Base.metadata.create_all(bind=engine)

class MessageSchema(BaseModel):
    chatid: str
    query: str

class CompletedMessageSchema(BaseModel):
    query: str
    response: str

class ChatSchema(BaseModel):
    id: str
    messages: List[MessageSchema] = []

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


