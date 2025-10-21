from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from .database import Base
from datetime import datetime

class String(Base):
    __tablename__ = 'strings'

    id = Column(Integer, primary_key=True, index=True)
    value = Column(String, nullable=False)
    length = Column(Integer)
    is_palindrome = Column(Boolean)
    unique_characters = Column(Integer)
    word_count = Column(Integer)
    sha256_hash = Column(String)
    character_freq = Column(Text, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

