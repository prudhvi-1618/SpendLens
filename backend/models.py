import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, TIMESTAMP, Boolean, Numeric, Float, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_id = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expiry = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    raw_emails = relationship("RawEmail", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")

class RawEmail(Base):
    __tablename__ = 'raw_emails'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    gmail_message_id = Column(String, unique=True, nullable=False)
    subject = Column(Text)
    snippet = Column(Text)
    received_at = Column(TIMESTAMP)
    processed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="raw_emails")
    transactions = relationship("Transaction", back_populates="raw_email")

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    raw_email_id = Column(UUID(as_uuid=True), ForeignKey('raw_emails.id'), nullable=False)
    merchant = Column(String)
    amount = Column(Numeric(12, 2))
    currency = Column(String(3))
    category = Column(String)
    date = Column(Date)
    confidence = Column(Float)
    flagged = Column(Boolean, default=False)
    flag_reason = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    raw_email = relationship("RawEmail", back_populates="transactions")
