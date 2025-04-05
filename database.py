from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["chatuserinfo"]

users_collection = db["userdata"]
otp_collection = db["otp_storage"]
messages_collection = db["messages"]
