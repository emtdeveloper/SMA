import os
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# Connect immediately when importing
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Mongo connected!")

    db = client["smart-meals-database"]
    users_collection = db["users"]
    logs_collection = db["logs"]
    meals_collection = db["meals"]

except Exception as e:
    print(f"❌ Mongo connection failed: {e}")
    st.error("Database not reachable. Please check your connection settings.")
    st.stop()