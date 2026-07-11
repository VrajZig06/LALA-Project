from pydantic import BaseModel

class OrderItems(BaseModel):
    name: str
    quantity: int
    price: float

class CreateOrderRequest(BaseModel):
    order_items: list[OrderItems] 
    currency: str = "INR"

class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str 