from app.core.message import ErrorMessage, SuccessMessage
from fastapi import HTTPException, status as http_status, Request, Header
from app.core.exception import ServerException
from app.core.config import get_settings
from app.schema.payment import CreateOrderRequest, VerifyPaymentRequest
from app.core.response import success_response
from sqlalchemy.orm import Session
from app.repository.order_repository import OrderRepository
from app.repository.order_item_repository import OrderItemRepository
from app.repository.payment_transaction_repository import PaymentTransactionRepository
from app.repository.subscription_repository import SubscriptionRepository
from app.repository.invoice_repository import InvoiceRepository
from app.core.enums import RazorpayPaymentStatus
from app.schema.subscription import SubscriptionPlanCreate
import razorpay
import json

settings = get_settings()

class PaymentService:
    def __init__(self, db: Session):

        # Local Variable
        self.db = db

        # Razorpay Secrets 
        self.RAZORPAY_KEY_ID = settings.RAZORPAY_API_KEY
        self.RAZORPAY_KEY_SECRET = settings.RAZORPAY_API_SECRET

        # Create Razorpay Client
        self.rz_client = self.create_razorpay_client(self.RAZORPAY_KEY_ID, self.RAZORPAY_KEY_SECRET)

        # Initalize Repository here
        self.order_repo = OrderRepository(self.db)
        self.order_item_repo = OrderItemRepository(self.db)
        self.payment_transaction_repo = PaymentTransactionRepository(self.db)
        self.subscription_repo = SubscriptionRepository(self.db)
        self.invoice_repo = InvoiceRepository(self.db)



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
    def create_razorpay_order(self, data: CreateOrderRequest, current_user):
        try:
            # Check Razorpay Client Initialization
            if self.rz_client is None:
                raise HTTPException(        
                    status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail = ErrorMessage.PAYMENT_GATEWAY_INITIALIZATION_ERROR
                )

            order_data = data.model_dump()
        
            # Calculate Total Amount
            amount = 0
            for item in order_data.get("order_items"):
                # Calculate Total
                amount +=(item.get("price", 0) * item.get("quantity"))

            # Create Order Payload
            order_payload = {
                "amount": amount * 100,
                "currency": order_data.get("currency"),
                "payment_capture": 1  # 1 means automatic capture
            }

            # Create order in Razorpay ecosystem
            razorpay_order = self.rz_client.order.create(data=order_payload)

            # Check Order is Created 
            if razorpay_order.get("id", None) is None:
                raise HTTPException(
                    status_code = http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail = ErrorMessage.ORDER_CREATION_FAILED
                )
            
            # Add Order Detail in Database
            db_order_data = self.order_repo.create({
                "razorpay_order_id" : razorpay_order["id"],
                "user_id": current_user.get("id", None),
                "amount": amount * 100
            })

            # Add order Items 
            order_data_id = db_order_data.id
            order_items_data = []
            for item in order_data.get("order_items"):
                order_item_data = {
                    "order_id": order_data_id,
                    "user_id": current_user.get('id', None),
                    "item_price": item["price"], 
                    "item_quantity": item["quantity"]
                }

                order_items_data.append(order_item_data)
            
            # Now we need to add This order item data to DB
            self.order_item_repo.create_all(order_items_data)

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
                status = payment_entity["status"]
                
                # Check First is there any entry related to this payment_id
                is_payment_entry = self.payment_transaction_repo.get_by_field("payment_id", payment_id)

                # Find Order with Razorpay Order Id
                order = self.order_repo.get_by_field("razorpay_order_id",order_id)

                if not is_payment_entry:
                    transaction_record = {
                        "payment_id": payment_id,
                        "order_id": order.id,
                        "status": status
                    }

                    # Add payment transaction record
                    self.payment_transaction_repo.create(transaction_record)

                
            elif event == "payment.failed":
                payment_entity = payload["payload"]["payment"]["entity"]
                payment_id = payment_entity["id"]
                order_id = payment_entity["order_id"]
                status = payment_entity["status"]

                # Check First is there any entry related to this payment_id
                is_payment_entry = self.payment_transaction_repo.get_by_field("payment_id", payment_id)

                if not is_payment_entry:

                    # Find Order with Razorpay Order Id
                    order = self.order_repo.get_by_field("razorpay_order_id",order_id)


                    transaction_record = {
                        "payment_id": payment_id,
                        "order_id": order.id,
                        "status": status
                    }

                    # Add payment transaction record
                    self.payment_transaction_repo.create(transaction_record)

            elif event == "subscription.cancelled":
                subscription_payload = payload["payload"]["subscription"]

                # Key Feaure extracts from Webhook
                status = subscription_payload["entity"]["status"]
                notes = subscription_payload["entity"]["notes"]
                user_id = notes["user_id"]

                # Find Current Subscription
                subscription_detail = self.subscription_repo.fetch_current_subscription(user_id)

                # Now Extract And Deactivate that Subscription
                subscription_id = subscription_detail.id
                self.subscription_repo.cancelled_current_subscription(subscription_id)

            elif event == "invoice.paid":
                invoice_payload = payload["payload"]["invoice"]["entity"]
                
                razorpay_invoice_id = invoice_payload.get("id")
                razorpay_subscription_id = invoice_payload.get("subscription_id")
                payment_id = invoice_payload.get("payment_id")
                amount = invoice_payload.get("amount")
                status = invoice_payload.get("status")
                billing_start = invoice_payload.get("billing_start")
                billing_end = invoice_payload.get("billing_end")
                paid_at = invoice_payload.get("paid_at")

                # Find the subscription in our database using razorpay_subscription_id
                subscription = self.subscription_repo.get_by_field("razorpay_subscription_id", razorpay_subscription_id)
                if not subscription:
                    # Log error and skip since we cannot save without a valid subscription foreign key
                    print(f"Error: Subscription not found for razorpay_subscription_id: {razorpay_subscription_id}")
                else:
                    # Check if invoice already exists
                    existing_invoice = self.invoice_repo.get_by_field("razorpay_invoice_id", razorpay_invoice_id)
                    
                    invoice_data = {
                        "subscription_id": subscription.id,
                        "razorpay_invoice_id": razorpay_invoice_id,
                        "payment_id": payment_id,
                        "amount": amount,
                        "status": status,
                        "billing_start": billing_start,
                        "billing_end": billing_end,
                        "paid_at": paid_at
                    }

                    if existing_invoice:
                        # Update existing invoice to maintain idempotency
                        self.invoice_repo.update(existing_invoice, invoice_data)
                    else:
                        # Create new invoice record
                        self.invoice_repo.create(invoice_data)

            # 5. Always return a 200 OK response to Razorpay quickly
            return success_response(
                status_code= http_status.HTTP_200_OK,
                msg= SuccessMessage.PAYMENT_WEBHOOK_RECIEVED_SUCCESSFULLY
            )

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

            # Find Order Id from DB using Razorpay Order Id
            razorpay_order_id = payment_data.razorpay_order_id
            order = self.order_repo.get_by_field("razorpay_order_id", razorpay_order_id)

            # Create Payment Transaction Record 
            transaction_record = {
                "payment_id": payment_data.razorpay_payment_id,
                "order_id": order.id,
                "status": RazorpayPaymentStatus.CAPTURED.value
            }

            # Add To DB
            self.payment_transaction_repo.create(transaction_record)

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

    # Create Razorpay Plan 
    def create_razorpay_plan(self, plan_data: SubscriptionPlanCreate):
        try:
            # create razorpay plan payload
            razorpay_plan_payload = {
                "period": plan_data.period,
                "interval": plan_data.interval,
                "item": {
                    "name":(plan_data.name).lower(),
                    "amount": plan_data.price * 100, # Razorpay Price must be * 10
                    "currency": plan_data.currency,
                    "description": plan_data.description
                }
            }

            # Create Plan in razorpay using razorpay client
            razorpay_plan = self.rz_client.plan.create(data=razorpay_plan_payload)

            return razorpay_plan
            
        except HTTPException:
            raise
        except Exception as e:
            raise ServerException(e)

    # Update Plan Details 
    def update_razorpay_plan(self):
        pass

    # Create Subscription
    def create_subscription(self, payload):
        try:
            # Create Razorpay Subscription
            razorpay_response = self.rz_client.subscription.create(data = payload)
            return razorpay_response

        except razorpay.errors.BadRequestError as e:
            # Catch validation errors from Razorpay (e.g., bad plan_id)
            raise HTTPException(
                status_code=400, 
                detail=ErrorMessage.RAZORPAY_BAD_REQUEST.format(e = str(e)))
        except Exception as e:
            raise ServerException(e)

    # Update Subscription (Downgrade and Upgrade Subscription)
    def update_subscription(self):
        pass

    # Cancel Subscription
    def cancel_subscription(self, payload):
        try:
            subscription_id = payload.get("subscription_id", None)
            at_cycle_end = payload.get("at_cycle_end", None)

            options= {
                "cancel_at_cycle_end": at_cycle_end
            }

            # subscription_id and at_cycle_end not then raise error
            if subscription_id is None or at_cycle_end is None:
                raise HTTPException(
                    status_code = http_status.HTTP_400_BAD_REQUEST,
                    detail = ErrorMessage.SUBSCRIPTION_NOT_CANCELLED
                )

            # Create Razorpay Subscription
            razorpay_cancel_response = self.rz_client.subscription.cancel(subscription_id, options)
            return razorpay_cancel_response

        except razorpay.errors.BadRequestError as e:
            raise HTTPException(
                status_code=400, 
                detail=ErrorMessage.RAZORPAY_BAD_REQUEST.format(e = str(e)))
        except HTTPException:
            raise 
        except Exception as e:
            raise ServerException(e)


