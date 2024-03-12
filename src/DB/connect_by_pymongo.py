import os
from pathlib import Path

from dotenv import load_dotenv
import pymongo

env_path = Path(__file__).parent.parent.parent.joinpath(".env")
if env_path.is_file:
    print(env_path)
    load_dotenv(env_path)

MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASS = os.getenv("MONGODB_PASS")
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_NAME = os.getenv("MONGODB_NAME")

client = None
URI = None

if MONGODB_USER:
    URI = f"{MONGODB_URL}?retryWrites=true&w=majority&appName=Cluster0"

    try:
        client = pymongo.MongoClient(URI)
    except pymongo.errors.ConfigurationError:
        print(
            "An Invalid URI host error was received. Is your Atlas host name correct in your connection string?"
        )
    except pymongo.errors as e:
        print("pymongo error:", e)
else:
    print("not defined MONGODB_USER. Database not connected")

if __name__ == "__main__":
    print(f"{client=}")
    print(f"{URI=}")
    # testing connect
    db = client[f"{MONGODB_NAME}"]
    collection = db["test"]
    
    document_data = {"name": "testValue"}
    # Insert a document into the collection
    result = collection.insert_one(document_data)
    print(f"Inserted document ID: {result.inserted_id}")
    
    document_data = {"name2": "testValue2"}
    # Insert second document into the collection
    result = collection.insert_one(document_data)
    print(f"Inserted document ID: {result.inserted_id}")
    # Find all documents in the collection
    documents = collection.find()
    for document in documents:
        print(document)
     
    # Update second document in the collection
    query = {"name2": "testValue2"}
    new_data = {"$set": {"name2": "testValue3"}}

    result = collection.update_one(query, new_data)
    print(f"Modified {result.modified_count} document(s)")
    documents = collection.find()
    for document in documents:
        print(document)
        
    # # Delete a document from the collection
    # deletion_query = {"name2": "testValue3"}

    # result = collection.delete_one(deletion_query)
    # print(f"Deleted {result.deleted_count} document(s)")
    # documents = collection.find()
    # for document in documents:
    #     print(document)
     
     
    client.close()
