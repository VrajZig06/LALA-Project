from app.core.config import get_settings
from app.core.logger import get_logger
from datetime import datetime
from sib_api_v3_sdk.rest import ApiException
import asyncio
import sib_api_v3_sdk

# Logger Setup
logger = get_logger(__name__)
settings = get_settings()


class EmailService:
    def __init__(self):
        self.api_key = settings.BREVO_API_KEY
        self.sender_email = settings.BREVO_SENDER_EMAIL
        self.sender_name = settings.BREVO_SENDER_NAME

        if not self.api_key or not self.sender_email:
            logger.error("Brevo API key or sender email not configured")
            raise ValueError("Brevo API key and sender email must be configured")

        # Configure API key authorization
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = self.api_key

        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> bool:
        """
        Send a transactional email via Brevo with retry logic

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
            max_retries: Maximum number of retry attempts (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)
        """
        attempt = 0
        last_error = None

        while attempt < max_retries:
            attempt += 1
            try:
                sender = {"name": self.sender_name, "email": self.sender_email}
                to = [{"email": to_email}]

                logger.info(
                    f"[Attempt {attempt}/{max_retries}] Preparing to send email to {to_email} "
                    f"from {self.sender_email} at {datetime.utcnow().isoformat()}"
                )

                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=to,
                    sender=sender,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content or self._strip_html(html_content),
                )

                response = self.api_instance.send_transac_email(send_smtp_email)
                logger.info(
                    f"[Attempt {attempt}/{max_retries}] Email sent successfully to {to_email}, "
                    f"message_id: {response.message_id}, timestamp: {datetime.utcnow().isoformat()}"
                )
                return True

            except ApiException as e:
                last_error = e
                logger.error(
                    f"[Attempt {attempt}/{max_retries}] Brevo API exception when sending email to {to_email}: {e}"
                )
                logger.error(f"Status code: {e.status}")
                logger.error(f"Response body: {e.body}")

                # Don't retry on certain error codes
                if e.status in [400, 401, 403]:  # Bad request, Unauthorized, Forbidden
                    logger.error(f"Non-retryable error, giving up")
                    return False

                if attempt < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

            except Exception as e:
                last_error = e
                logger.error(
                    f"[Attempt {attempt}/{max_retries}] Error sending email to {to_email}: {e}"
                )
                import traceback

                logger.error(f"Traceback: {traceback.format_exc()}")

                if attempt < max_retries:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

        # All retries exhausted
        logger.error(
            f"All {max_retries} attempts failed for email to {to_email}. Last error: {last_error}"
        )
        return False

    def _strip_html(self, html: str) -> str:
        """Simple HTML to text conversion for plain text fallback"""
        import re

        text = re.sub("<[^<]+?>", "", html)
        return text.strip()

    async def send_welcome_email(self, to_email: str, name: str) -> bool:
        """
        Send welcome email to new users
        """
        subject = "Welcome to HotelPilot!"
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2c3e50;">Welcome to HotelPilot!</h1>
                <p>Hi {name},</p>
                <p>We're excited to have you on board. HotelPilot helps you manage your restaurant operations efficiently.</p>
                <p>Get started by logging into your dashboard.</p>
                <a href="https://your-app-url.com/login" 
                   style="display: inline-block; padding: 12px 24px; background-color: #3498db; 
                          color: white; text-decoration: none; border-radius: 4px;">
                    Go to Dashboard
                </a>
            </div>
        </body>
        </html>
        """
        return await self.send_email(to_email, subject, html_content)


# Singleton instance
email_service = EmailService()
