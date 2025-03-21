
from pymongo import MongoClient


uri = ""

client = MongoClient(uri)

try:
    client.admin.command('ping')
    db=client['env']
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
