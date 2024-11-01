from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    JSON,
    DateTime,
    func,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class QueueRequest(Base):
    __tablename__ = "queue_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uri = Column(String, nullable=False)
    method = Column(String, nullable=False)
    params = Column(JSON, nullable=True)
    headers = Column(JSON, nullable=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    retries = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QueueResponse(Base):
    __tablename__ = "queue_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, nullable=False)
    status_code = Column(Integer, nullable=True)
    body = Column(Text, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
