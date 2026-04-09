from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI           = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME             = os.getenv("DB_NAME", "phishguard")
JWT_SECRET          = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM       = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES  = int(os.getenv("JWT_EXPIRE_MINUTES", 1440))
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY", "")
SMTP_EMAIL          = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD       = os.getenv("SMTP_PASSWORD", "")
TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
