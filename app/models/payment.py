from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base
from app.utils.time_utils import get_jakarta_time

class PaymentStatus(str, enum.Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    merchant_ref = Column(String, unique=True, index=True, nullable=False) # Our Reference
    tripay_reference = Column(String, nullable=True) # Tripay Reference
    
    amount = Column(Integer, nullable=False)
    payment_method = Column(String, nullable=True) # e.g. BRIVA, ALFAMART
    payment_status = Column(String, default=PaymentStatus.UNPAID.value) # Use String for compatibility
    plan_id = Column(String, nullable=True) # To track plan correctly on callback
    
    checkout_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=get_jakarta_time)
    updated_at = Column(DateTime, default=get_jakarta_time, onupdate=get_jakarta_time)

    # Relationship
    owner = relationship("User", back_populates="transactions")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    plan_type = Column(String, nullable=False) # 'monthly', 'yearly'
    start_date = Column(DateTime, default=get_jakarta_time)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=get_jakarta_time)
    updated_at = Column(DateTime, default=get_jakarta_time, onupdate=get_jakarta_time)

    # Relationship
    owner = relationship("User", back_populates="subscriptions")
