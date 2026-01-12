from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.utils.time_utils import get_jakarta_time

class SavedRPP(Base):
    __tablename__ = "saved_rpps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    mapel = Column(String, nullable=False)
    kelas = Column(String, nullable=False)
    topik = Column(String, nullable=False)
    
    # Content
    content_markdown = Column(Text, nullable=False) # The generated RPP
    input_data = Column(JSON, nullable=True) # Full form inputs
    
    created_at = Column(DateTime, default=get_jakarta_time)
    updated_at = Column(DateTime, default=get_jakarta_time, onupdate=get_jakarta_time)

    # Relationship
    owner = relationship("User", back_populates="rpps")

class SavedQuiz(Base):
    __tablename__ = "saved_quizzes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    mapel = Column(String, nullable=False)
    topik = Column(String, nullable=False)
    tingkat_kesulitan = Column(String, nullable=False)
    
    # Content
    quiz_data = Column(JSON, nullable=False) # The generated JSON quiz
    
    created_at = Column(DateTime, default=get_jakarta_time)

    # Relationship
    owner = relationship("User", back_populates="quizzes")

class GenerationLog(Base):
    __tablename__ = "generation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    plan_type = Column(String, nullable=False) # Store plan at time of generation
    created_at = Column(DateTime, default=get_jakarta_time)

# Update User model to include this relationship? 
# Or just define back_populates here and ensure User model has it or we can skip back_populates on one side if not needed.
# Let's check user.py content first to be clean, but for now defining it here is step 1.
