from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Nullable if google login only
    full_name = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    
    from sqlalchemy.orm import relationship
    rpps = relationship("SavedRPP", back_populates="owner")
    quizzes = relationship("SavedQuiz", back_populates="owner")
    transactions = relationship("Transaction", back_populates="owner")
    subscriptions = relationship("Subscription", back_populates="owner")
