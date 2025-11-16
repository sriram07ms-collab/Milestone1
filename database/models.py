"""Database models for ICICI Prudential funds"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
from config.settings import DATABASE_URL

Base = declarative_base()


class Scheme(Base):
    """ICICI Prudential scheme model"""
    __tablename__ = 'icici_schemes'
    
    scheme_id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_name = Column(String(255), nullable=False)
    scheme_slug = Column(String(255), unique=True)
    category = Column(String(100))
    risk_level = Column(String(50))
    nav = Column(Float)
    expense_ratio = Column(String(20))
    rating = Column(Integer)
    fund_size_cr = Column(Float)
    returns_1y = Column(String(20))
    returns_3y = Column(String(20))
    returns_5y = Column(String(20))
    groww_url = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    facts = relationship("SchemeFact", back_populates="scheme", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Scheme(name='{self.scheme_name}', url='{self.groww_url}')>"


class SchemeFact(Base):
    """Scheme facts with source URLs"""
    __tablename__ = 'scheme_facts'
    
    fact_id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_id = Column(Integer, ForeignKey('icici_schemes.scheme_id'), nullable=False)
    fact_type = Column(String(50), nullable=False)
    fact_value = Column(Text, nullable=False)
    source_url = Column(Text, nullable=False)
    extraction_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scheme = relationship("Scheme", back_populates="facts")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('scheme_id', 'fact_type', 'extraction_date', name='uq_scheme_fact_date'),
    )
    
    def __repr__(self):
        return f"<SchemeFact(scheme_id={self.scheme_id}, type='{self.fact_type}', value='{self.fact_value}')>"


class ScrapingLog(Base):
    """Scraping logs for monitoring"""
    __tablename__ = 'scraping_logs'
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    source_url = Column(Text)
    scheme_name = Column(String(255))
    status = Column(String(20))  # success, failed, partial
    records_extracted = Column(Integer, default=0)
    error_message = Column(Text)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ScrapingLog(url='{self.source_url}', status='{self.status}')>"


# Database setup
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

