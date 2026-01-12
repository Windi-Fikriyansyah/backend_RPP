from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True) # Matematika, IPAS
    category = Column(String) # Umum, Kejuruan

    goals = relationship("CurriculumGoal", back_populates="subject")

class CurriculumGoal(Base):
    __tablename__ = "curriculum_goals"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    phase = Column(String, index=True) # A, B, C, D, E, F
    element = Column(String) # Bilangan, Aljabar
    cp_content = Column(Text) # Teks CP asli
    version = Column(String, default="2024")

    subject = relationship("Subject", back_populates="goals")
