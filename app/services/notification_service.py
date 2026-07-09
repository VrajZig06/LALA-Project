from app.core.message import SuccessMessage
from app.core.response import success_response
from app.schema.notification import NotificationBlock
from app.core.message import LoggerMessage
from app.core.logger import get_logger
from app.core.exception import ServerException
from fastapi import HTTPException, status as http_status
from firebase_admin import messaging

logger =  get_logger(__name__)

class NotificationService:
    # Send Push Notification 
    def send_notification(self, data: NotificationBlock):
        try:
            # Extract Notification Data
            title = data.title
            body = data.body
            token = data.token 

            # Prepare Notification Message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=data.title,
                    body=data.body,
                ),
                token=token
            )

            # Send to Client
            response = messaging.send(message)
            return success_response(
                status_code=http_status.HTTP_200_OK,
                msg=SuccessMessage.NOTIFICATION_SENT_SUCCESSFULLY,
                data={
                    "message_id": response
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            raise ServerException(e)

