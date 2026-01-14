import hmac
import hashlib
import json
import httpx
from datetime import datetime
from app.config import Config

class TripayService:
    BASE_URL_SANDBOX = "https://tripay.co.id/api-sandbox"
    BASE_URL_PROD = "https://tripay.co.id/api"

    def __init__(self):
        self.api_key = Config.TRIPAY_API_KEY
        self.private_key = Config.TRIPAY_PRIVATE_KEY
        self.merchant_code = Config.TRIPAY_MERCHANT_CODE
        self.is_production = Config.TRIPAY_MODE == "PRODUCTION"
        self.base_url = self.BASE_URL_PROD if self.is_production else self.BASE_URL_SANDBOX

    def _generate_signature(self, merchant_ref: str, amount: int) -> str:
        """
        Signature for Create Transaction: HMAC_SHA256(private_key, merchant_code + merchant_ref + amount)
        """
        payload = f"{self.merchant_code}{merchant_ref}{amount}"
        return hmac.new(
            self.private_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    def validate_callback_signature(self, json_body: bytes, signature_header: str) -> bool:
        """
        Validate incoming callback signature.
        Callback Signature = HMAC_SHA256(private_key, raw_json_body)
        """
        expected_signature = hmac.new(
            self.private_key.encode(),
            json_body, # Raw bytes
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature_header)

    async def create_transaction(self, merchant_ref: str, amount: int, payment_method: str, 
                               customer_name: str, customer_email: str, order_items: list):
        """
        Call Tripay API to create a transaction.
        """
        signature = self._generate_signature(merchant_ref, amount)
        
        payload = {
            "method": payment_method,
            "merchant_ref": merchant_ref,
            "amount": amount,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "order_items": order_items,
            "callback_url": f"{Config.BACKEND_URL}/api/payment/callback",
            "return_url": f"{Config.FRONTEND_URL}/dashboard",
            "expired_time": int(datetime.utcnow().timestamp()) + (24 * 60 * 60), # Unix Timestamp
            "signature": signature
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/transaction/create",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Tripay Error: {response.text}")
            
            return response.json()

    async def get_payment_channels(self):
        """
        Fetch available payment channels from Tripay.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/merchant/payment-channel",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Tripay Error: {response.text}")
            
            return response.json()
