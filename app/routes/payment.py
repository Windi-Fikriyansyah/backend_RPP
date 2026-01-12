from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json
import logging
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.models.payment import Transaction, Subscription, PaymentStatus
from app.routes.auth import get_current_user
from app.services.tripay import TripayService
from app.utils.time_utils import get_jakarta_time

router = APIRouter()
tripay_service = TripayService()
logger = logging.getLogger(__name__)

# --- Pydantic Models ---
class Plan(BaseModel):
    id: str
    name: str
    price: int
    duration_days: int
    features: List[str]

class CreateTransactionRequest(BaseModel):
    plan_id: str
    payment_method: str # e.g., 'BRIVA', 'QRIS'

# Defines available plans (Hardcoded for single source of truth)
AVAILABLE_PLANS = {
    "monthly": Plan(id="monthly", name="Paket Pro", price=49000, duration_days=30, features=["Unlimited RPP", "Export Word"]),
    "yearly": Plan(id="yearly", name="Paket Tahunan", price=450000, duration_days=365, features=["Hemat 25%", "Priority Support"]),
    "school": Plan(id="school", name="Paket Sekolah", price=299000, duration_days=30, features=["Up to 50 Guru", "Admin Dashboard"])
}

@router.get("/plans", response_model=List[Plan])
async def get_plans():
    return list(AVAILABLE_PLANS.values())

@router.get("/channels")
async def get_channels():
    try:
        channels_res = await tripay_service.get_payment_channels()
        return channels_res
    except Exception as e:
        logger.error(f"Failed to fetch channels: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch payment channels")

@router.post("/create")
async def create_payment(
    req: CreateTransactionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    plan = AVAILABLE_PLANS.get(req.plan_id)
    if not plan:
        raise HTTPException(status_code=400, detail="Invalid Plan ID")

    # Calculate Fee (User bears the fee)
    try:
        channels_res = await tripay_service.get_payment_channels()
        channels = channels_res.get("data", [])
        channel = next((c for c in channels if c["code"] == req.payment_method), None)
        
        if not channel:
            raise HTTPException(status_code=400, detail="Metode pembayaran tidak valid.")
            
        fee_data = channel.get("fee_merchant", {})
        flat_fee = fee_data.get("flat", 0)
        percent_fee = float(fee_data.get("percent", 0))
        
        total_fee = flat_fee + int((plan.price * percent_fee) / 100)
        total_amount = plan.price + total_fee
        
    except Exception as e:
        logger.error(f"Error calculating fees: {e}")
        # Fallback to base price if something fails, but better to error to be transparent
        raise HTTPException(status_code=500, detail="Gagal menghitung rincian biaya.")

    # 1. Generate Merchant Ref
    merchant_ref = f"INV-{current_user.id}-{uuid.uuid4().hex[:8].upper()}"
    
    # 2. Save Pending Transaction to DB (Store total_amount)
    new_trx = Transaction(
        user_id=current_user.id,
        merchant_ref=merchant_ref,
        amount=total_amount,
        payment_method=req.payment_method,
        payment_status=PaymentStatus.UNPAID.value,
        plan_id=plan.id
    )
    db.add(new_trx)
    # No commit here yet to avoid object expiration before update
    
    # 3. Call Tripay with total_amount
    try:
        tripay_res = await tripay_service.create_transaction(
            merchant_ref=merchant_ref,
            amount=total_amount,
            payment_method=req.payment_method,
            customer_name=current_user.full_name or "User",
            customer_email=current_user.email,
            order_items=[
                {
                    "sku": plan.id,
                    "name": plan.name,
                    "price": plan.price,
                    "quantity": 1
                },
                {
                    "sku": "FEE",
                    "name": f"Biaya Layanan ({channel['name']})",
                    "price": total_fee,
                    "quantity": 1
                }
            ]
        )
        data = tripay_res.get("data", {})
        
        # 4. Update Transaction with Tripay Data
        new_trx.tripay_reference = data.get("reference")
        new_trx.checkout_url = data.get("checkout_url")
        await db.commit()
        
        return {
            "success": True,
            "checkout_url": data.get("checkout_url"),
            "amount": data.get("amount"),
            "expiry_time": data.get("expired_time")
        }
        
    except Exception as e:
        logger.error(f"Tripay Error: {e}")
        # Rollback or mark failed? 
        # Since we committed UNPAID, we can verify later.
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/callback")
async def payment_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        # 1. Get Raw Body & Signature
        raw_body = await request.body()
        signature = request.headers.get("X-Callback-Signature")
        
        # Logging for Debugging
        logger.info(f"--- Tripay Callback Received ---")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Raw Body: {raw_body.decode('utf-8', errors='ignore')}")
        
        if not signature:
            logger.error("Missing X-Callback-Signature header")
            return JSONResponse(status_code=400, content={"success": False, "message": "Missing Signature"})

        # 2. Validate Signature
        if not tripay_service.validate_callback_signature(raw_body, signature):
            logger.warning("Invalid Tripay Callback Signature")
            return JSONResponse(status_code=403, content={"success": False, "message": "Invalid Signature"})

        # 3. Parse Data
        data = json.loads(raw_body)
        merchant_ref = data.get("merchant_ref")
        status = data.get("status") # 'PAID', 'EXPIRED', 'FAILED'
        
        logger.info(f"Processing callback for {merchant_ref} with status {status}")

        # 4. Find Transaction
        result = await db.execute(select(Transaction).where(Transaction.merchant_ref == merchant_ref))
        trx = result.scalars().first()
        
        if not trx:
            logger.error(f"Transaction not found: {merchant_ref}")
            return JSONResponse(status_code=404, content={"success": False, "message": "Transaction Not Found"})
            
        if trx.payment_status == PaymentStatus.PAID.value:
            logger.info(f"Transaction {merchant_ref} is already PAID. Skipping.")
            return {"success": True, "message": "Already Paid"} # Idempotent

        # 5. Update Status
        if status == "PAID":
            trx.payment_status = PaymentStatus.PAID.value
            
            # 6. Activate Subscription
            plan_id = trx.plan_id or "monthly"
            plan = AVAILABLE_PLANS.get(plan_id, AVAILABLE_PLANS["monthly"])
            
            # Check existing subscription
            sub_res = await db.execute(select(Subscription).where(Subscription.user_id == trx.user_id))
            sub = sub_res.scalars().first()
            
            if not sub:
                sub = Subscription(user_id=trx.user_id)
                db.add(sub)
                
            sub.plan_type = plan.id
            sub.start_date = get_jakarta_time()
            sub.end_date = get_jakarta_time() + timedelta(days=plan.duration_days)
            sub.is_active = True
            logger.info(f"Subscription activated for user {trx.user_id}")
            
        elif status == "EXPIRED":
            trx.payment_status = PaymentStatus.EXPIRED.value
        elif status == "FAILED":
            trx.payment_status = PaymentStatus.FAILED.value
            
        await db.commit()
        logger.info(f"Callback processed successfully for {merchant_ref}")
        
        return {"success": True}

    except Exception as e:
        logger.error(f"Callback Error: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"success": False, "message": str(e)})
