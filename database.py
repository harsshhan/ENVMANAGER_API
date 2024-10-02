
from pymongo import MongoClient


uri = "mongodb+srv://harshan:harshan@envmanager.f518n.mongodb.net/?retryWrites=true&w=majority&appName=envmanager"

client = MongoClient(uri)

try:
    client.admin.command('ping')
    db=client['env']
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)