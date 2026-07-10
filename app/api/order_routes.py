from fastapi import Query, Header
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.core.dependecy import current_user
from app.core.logger import get_logger
from app.core.message import LoggerMessage
from app.db.session import get_db
from app.services.payment_service import PaymentService
from app.schema.payment import CreateOrderRequest, VerifyPaymentRequest

logger = get_logger(__name__)

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/create")
def create_order(payload: CreateOrderRequest, db: Session = Depends(get_db)):
    payment_service = PaymentService()
    return payment_service.create_razorpay_order(payload)

@router.post("/verify")
def verify_order(payload: VerifyPaymentRequest, user = Depends(current_user), db: Session = Depends(get_db)):
    payment_service = PaymentService()
    return payment_service.verify_razorpay_signature(payload)

@router.post("/razerpay/webhook")
async def handle_razerpay_webhook(request: Request, x_razorpay_signature: str = Header(None)):
    payment_service = PaymentService()
    return await payment_service.handle_razorpay_webhook(request, x_razorpay_signature)