from pymongo import MongoClient
from backend.config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
db     = client[DB_NAME]

users_col   = db["users"]
results_col = db["quiz_results"]
reports_col = db["awareness_reports"]

def ping():
    client.admin.command("ping")
    return True
