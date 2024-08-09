
from pymongo import MongoClient
from django.conf import settings

class MongoDBClient:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client.get_database()

    def get_collection(self, pythontest):
        return self.db['users']

mongo_client = MongoDBClient()
