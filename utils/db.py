import os
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

def connect_to_mongo():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ Mongo connected!")
        return client
    except Exception as e:
        print(f"❌ Mongo connection failed: {e}")
        st.error("Database not reachable.")
        st.stop()