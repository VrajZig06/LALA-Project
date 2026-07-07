import asyncio
from datetime import datetime

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.core.config import get_settings
from app.core.logger import get_logger

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
                    logger.error("Non-retryable error, giving up")
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

    async def send_otp_email(
        self, to_email: str, otp: int, name: str = None, expiry_minutes: int = 5
    ) -> bool:
        """
        Send OTP verification email to the user with a premium design
        """
        subject = f"{otp} is your verification code"
        app_name = settings.APP_NAME or "LALA"
        display_name = name or self._strip_email_name(to_email)
        year = datetime.now().year

        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify Your Email</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: 'Inter', system-ui, -apple-system, sans-serif; -webkit-font-smoothing: antialiased; width: 100% !important;">
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; padding: 40px 10px;">
    <tr>
      <td align="center">
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
          <!-- Top Gradient Bar -->
          <tr>
            <td style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); padding: 32px 40px; text-align: center;">
              <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;">{app_name}</h1>
            </td>
          </tr>
          <!-- Content Body -->
          <tr>
            <td style="padding: 40px 40px 30px 40px;">
              <h2 style="margin: 0 0 16px 0; color: #1e293b; font-size: 20px; font-weight: 700; text-align: center;">Verify Your Email Address</h2>
              <p style="margin: 0 0 24px 0; color: #475569; font-size: 15px; line-height: 24px;">
                Hi {display_name},<br><br>
                Thank you for choosing <strong>{app_name}</strong>. To complete your verification, please use the 4-digit verification code (OTP) below.
              </p>
              
              <!-- OTP Box -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f1f5f9; border-radius: 12px; margin-bottom: 24px; border: 1px dashed #cbd5e1;">
                <tr>
                  <td align="center" style="padding: 24px;">
                    <div style="font-size: 38px; font-weight: 800; letter-spacing: 12px; color: #4f46e5; font-family: 'Courier New', Courier, monospace; text-shadow: 1px 1px 0px #ffffff; padding-left: 12px;">{otp}</div>
                  </td>
                </tr>
              </table>
              
              <p style="margin: 0 0 24px 0; color: #64748b; font-size: 13px; line-height: 20px; text-align: center;">
                This verification code is valid for <strong>{expiry_minutes} minutes</strong>.<br>
                For security reasons, do not share this code with anyone.
              </p>
              <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">
              <p style="margin: 0; color: #94a3b8; font-size: 12px; line-height: 18px; text-align: center;">
                If you did not request this code, please ignore this email or contact support if you suspect unauthorized access.
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background-color: #f8fafc; padding: 24px 40px; text-align: center; border-top: 1px solid #f1f5f9;">
              <p style="margin: 0 0 8px 0; color: #64748b; font-size: 12px; font-weight: 600;">{self.sender_name}</p>
              <p style="margin: 0; color: #94a3b8; font-size: 11px;">© {year} {self.sender_name}. All rights reserved.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
        return await self.send_email(to_email, subject, html_content)

    async def send_reset_password_email(
        self, to_email: str, reset_link: str, name: str = None, expiry_minutes: int = 5
    ) -> bool:
        """
        Send a password reset link email to the user with a premium design
        """
        subject = "Reset Your Password"
        app_name = settings.APP_NAME or "LALA"
        display_name = name or self._strip_email_name(to_email)
        year = datetime.now().year

        html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset Your Password</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: 'Inter', system-ui, -apple-system, sans-serif; -webkit-font-smoothing: antialiased; width: 100% !important;">
  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f8fafc; padding: 40px 10px;">
    <tr>
      <td align="center">
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 520px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05), 0 8px 10px -6px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">
          <!-- Top Gradient Bar -->
          <tr>
            <td style="background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); padding: 32px 40px; text-align: center;">
              <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 800; letter-spacing: -0.5px;">{app_name}</h1>
            </td>
          </tr>
          <!-- Content Body -->
          <tr>
            <td style="padding: 40px 40px 30px 40px;">
              <h2 style="margin: 0 0 16px 0; color: #1e293b; font-size: 20px; font-weight: 700; text-align: center;">Reset Your Password</h2>
              <p style="margin: 0 0 24px 0; color: #475569; font-size: 15px; line-height: 24px;">
                Hi {display_name},<br><br>
                We received a request to reset the password for your <strong>{app_name}</strong> account. Click the button below to set a new password.
              </p>
              
              <!-- CTA Button -->
              <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 30px;">
                <tr>
                  <td align="center">
                    <a href="{reset_link}" 
                       style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.2), 0 2px 4px -1px rgba(79, 70, 229, 0.1);">
                      Reset Password
                    </a>
                  </td>
                </tr>
              </table>
              
              <p style="margin: 0 0 24px 0; color: #64748b; font-size: 13px; line-height: 20px; text-align: center;">
                This link is valid for <strong>{expiry_minutes} minutes</strong>.<br>
                If you did not request a password reset, you can safely ignore this email.
              </p>
              
              <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0;">
              
              <p style="margin: 0 0 8px 0; color: #94a3b8; font-size: 12px; line-height: 18px; text-align: center;">
                If you're having trouble clicking the button, copy and paste the link below into your web browser:
              </p>
              <p style="margin: 0; color: #6366f1; font-size: 12px; line-height: 18px; text-align: center; word-break: break-all;">
                <a href="{reset_link}" style="color: #6366f1; text-decoration: underline;">{reset_link}</a>
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="background-color: #f8fafc; padding: 24px 40px; text-align: center; border-top: 1px solid #f1f5f9;">
              <p style="margin: 0 0 8px 0; color: #64748b; font-size: 12px; font-weight: 600;">{self.sender_name}</p>
              <p style="margin: 0; color: #94a3b8; font-size: 11px;">© {year} {self.sender_name}. All rights reserved.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
        return await self.send_email(to_email, subject, html_content)

    def _strip_email_name(self, email: str) -> str:
        """Helper to extract a name from email if name is not provided"""
        try:
            return email.split("@")[0].capitalize()
        except Exception:
            return "User"


# Singleton instance
email_service = EmailService()
