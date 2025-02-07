# utils/db.py
from pymongo import MongoClient
from config import MONGO_URI

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["StockAlertBot"]
alerts_collection = db["alerts"]

def get_alerts(query):
    return list(alerts_collection.find(query))

def insert_alert(alert):
    alerts_collection.insert_one(alert)

def delete_alert(query):
    return alerts_collection.delete_one(query)

def delete_alerts(query):
    return alerts_collection.delete_many(query)