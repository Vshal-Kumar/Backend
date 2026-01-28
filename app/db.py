import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set")

if not DB_NAME:
    raise RuntimeError("DB_NAME not set")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

# Check connection
client.admin.command("ping")

db = client[DB_NAME]
users_col = db.users
user_skills_col = db.user_skills
internships_col = db.internships
weekly_plans_col = db.weekly_plans
tasks_col = db.tasks

submissions_col = db.submissions      # ✅ REQUIRED
feedback_col = db.feedback            # ✅ REQUIRED
feedback_col.create_index("submissionId", unique=True)



print(f"✅ MongoDB connected: {DB_NAME}")
