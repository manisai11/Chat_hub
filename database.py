from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv("priv.env")  # Load environment variables from .env file

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["chatuserinfo"]

users_collection = db["userdata"]  # Ensure this matches your database structure
otp_collection = db["otp_storage"]  # Define the OTP collection
messages_collection = db["messages"]  # Define the messages collection