from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class CodeReview(Base):
    """Model for storing code reviews"""
    __tablename__ = 'code_reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    code_snippet = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    review_text = Column(Text, nullable=False)
    suggestions = Column(Text)
    potential_bugs = Column(Text)
    quality_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'code_snippet': self.code_snippet,
            'language': self.language,
            'review_text': self.review_text,
            'suggestions': self.suggestions,
            'potential_bugs': self.potential_bugs,
            'quality_score': self.quality_score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///code_reviews.db')
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

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