from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["chatuserinfo"]

users_collection = db["userdata"]  # Ensure this matches your database structure
otp_collection = db["otp_storage"]  # Define the OTP collection
messages_collection = db["messages"]  # Define the messages collection