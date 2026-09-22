"""Small persistence layer for the document analysis workspace."""
import os
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Session

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/intelligent_document_analyzer")

class Base(DeclarativeBase):
    pass

class DocumentRecord(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    document_id = Column(String(64), unique=True, nullable=False, index=True)
    filename = Column(String(512), nullable=False)
    file_type = Column(String(16), nullable=False)
    chunk_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

class AnalysisRecord(Base):
    __tablename__ = "analyses"
    id = Column(Integer, primary_key=True)
    document_id = Column(String(64), nullable=False, index=True)
    analysis_type = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)

def get_engine():
    return create_engine(DATABASE_URL, pool_pre_ping=True)

def initialize_database():
    Base.metadata.create_all(get_engine())

def save_document(document_id, filename, chunk_count):
    with Session(get_engine()) as session:
        record = session.scalar(select(DocumentRecord).where(DocumentRecord.document_id == document_id))
        if record is None:
            session.add(DocumentRecord(document_id=document_id, filename=filename,
                file_type=filename.rsplit(".", 1)[-1].upper(), chunk_count=chunk_count,
                created_at=datetime.now(timezone.utc)))
        else:
            record.filename, record.chunk_count = filename, chunk_count
        session.commit()

def save_analysis(document_id, analysis_type, content):
    with Session(get_engine()) as session:
        session.add(AnalysisRecord(document_id=document_id, analysis_type=analysis_type,
            content=content, created_at=datetime.now(timezone.utc)))
        session.commit()

def recent_documents(limit=8):
    with Session(get_engine()) as session:
        return list(session.scalars(select(DocumentRecord).order_by(DocumentRecord.created_at.desc()).limit(limit)))
