from enum import Enum


# Login Type
class LoginType(str, Enum):
    EMAIL = "email"
    GOOGLE = "google"
    GITHUB = "github"
    FACEBOOK = "facebook"

# Razorpay Transaction Types
class RazorpayPaymentStatus(str, Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"

# Razorpay Period Cycle
class RazorpayPeriodCycles(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

# Razorpay Currency 
class RazorpayCurrency(str, Enum):
    USD = "USD"
    AED = "AED"
    INR = "INR"