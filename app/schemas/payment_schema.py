from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TransactionResponse(BaseModel):
    id: int
    merchant_ref: str
    tripay_reference: Optional[str]
    amount: int
    payment_method: Optional[str]
    payment_status: str
    checkout_url: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
