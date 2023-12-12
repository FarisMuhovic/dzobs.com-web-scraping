from pymongo import MongoClient

class JobsScraperPipeline:
    def process_item(self, item, spider):
        return item
    
# MongoDB connection 
class MongoDBConnector:
    def __init__(self, connection_string, database_name, collection_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    def insert_data(self, data):
        self.collection.insert_one(data)
    def drop_collection(self):
        self.collection.drop()
    def close_connection(self):
        self.client.close()