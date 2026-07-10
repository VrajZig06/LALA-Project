from app.core.message import ErrorMessage, SuccessMessage
from fastapi import HTTPException, status as http_status, Request, Header
from app.core.exception import ServerException
from app.core.config import get_settings
from app.schema.payment import CreateOrderRequest, VerifyPaymentRequest
from app.core.response import success_response
import razorpay
import json

settings = get_settings()

class PaymentService:
    def __init__(self):
        self.RAZORPAY_KEY_ID = settings.RAZORPAY_API_KEY
        self.RAZORPAY_KEY_SECRET = settings.RAZORPAY_API_SECRET

        # Create Razorpay Client
        self.rz_client = self.create_razorpay_client(self.RAZORPAY_KEY_ID, self.RAZORPAY_KEY_SECRET)

    # Method: Create Razorpay Client 
    def create_razorpay_client(self, RAZORPAY_KEY_ID: str, RAZORPAY_KEY_SECRET: str):
        try:
            client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
            if client:
                print(f'Razorpay Client Connected Successully!')
                return client
            else:
                print(f'Razorpay Client Failed to Connect!')
                return None
        except HTTPException:
            raise
        except Exception as e:
            raise ServerException(e)

    # Function: Create Razorpay Order 
    def create_razorpay_order(self, order_data: CreateOrderRequest):
        try:
            # Check Razorpay Client Initialization
            if self.rz_client is None:
                raise HTTPException(        
                    status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail = ErrorMessage.PAYMENT_GATEWAY_INITIALIZATION_ERROR
                )

            # Create Order Payload
            order_payload = {
                "amount": order_data.amount,
                "currency": order_data.currency,
                "payment_capture": 1  # 1 means automatic capture
            }

            # Create order in Razorpay ecosystem
            razorpay_order = self.rz_client.order.create(data=order_payload)

            # Return the order details to your frontend
            return success_response(
                status_code = http_status.HTTP_200_OK,
                msg = SuccessMessage.ORDER_CREATED_SUCCESSFULLY,
                data = {
                    "order_id": razorpay_order["id"],
                    "amount": razorpay_order["amount"],
                    "currency": razorpay_order["currency"]
                }
            )
        except HTTPException:
            raise   
        except Exception as e:
            raise ServerException(e)

    # Function: Handle Razorpay Webhook
    async def handle_razorpay_webhook(self, request: Request, x_razorpay_signature: str):
        try:
            # if not in Header then raise error
            if not x_razorpay_signature:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST, 
                    detail=ErrorMessage.WEBHOOK_SIGNATURE_MISSING
                )
            
            # 1. Get the raw request body bytes
            data_bytes = await request.body()

            try:
                # 2. Verify the webhook signature
                self.rz_client.utility.verify_webhook_signature(
                    data_bytes.decode('utf-8'), 
                    x_razorpay_signature, 
                    settings.RAZORPAY_WEBHOOK_SECRET
                )
            except razorpay.errors.SignatureVerificationError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST, 
                    detail=ErrorMessage.WEBHOOK_SIGNATURE_INVALID
                )
            
            # 3. Parse JSON data once signature is verified
            payload = json.loads(data_bytes)
            event = payload.get("event")

            # 4. Handle specific event flows
            if event == "payment.captured":
                payment_entity = payload["payload"]["payment"]["entity"]
                order_id = payment_entity["order_id"]
                payment_id = payment_entity["id"]
                amount = payment_entity["amount"]
                
                print(f"💰 Success! Payment of {amount} paise captured for Order {order_id}")
                # TODO: Mark order as "PAID" in your database and fulfill the purchase
                
            elif event == "payment.failed":
                payment_entity = payload["payload"]["payment"]["entity"]
                order_id = payment_entity["order_id"]
                print(f"❌ Payment failed for Order {order_id}")
                # TODO: Mark order status as "FAILED" in your database
                
            # 5. Always return a 200 OK response to Razorpay quickly
            return {"status": "ok"}

        except HTTPException:
            raise   
        except Exception as e:
            raise ServerException(e)

    # Function: Verify Payment Signature
    def verify_razorpay_signature(self, payment_data: VerifyPaymentRequest):
        try:
            # Construct the payload dictionary exactly as received
            param_dict = {
                'razorpay_order_id': payment_data.razorpay_order_id,
                'razorpay_payment_id': payment_data.razorpay_payment_id,
                'razorpay_signature': payment_data.razorpay_signature
            }

            # This will raise an error automatically if it's invalid/forged
            self.rz_client.utility.verify_payment_signature(param_dict)

            return success_response(
                status_code= http_status.HTTP_200_OK,
                msg= SuccessMessage.PAYMENT_VERIFY_SUCCESSFULLY
            )
        except razorpay.errors.SignatureVerificationError:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST, 
                detail=ErrorMessage.PAYMENT_VERIFICATION_FAILED
            )
        except HTTPException:
            raise   
        except Exception as e:
            raise ServerException(e)