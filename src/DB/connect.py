import os
from pathlib import Path

from dotenv import load_dotenv
from mongoengine import connect, OperationError

env_path = Path(__file__).parent.parent.parent.joinpath(".env")
if env_path.is_file:
    print(env_path)
    load_dotenv(env_path)

MONGODB_USER = os.getenv("MONGODB_USER")
MONGODB_PASS = os.getenv("MONGODB_PASS")
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_NAME = os.getenv("MONGODB_NAME")

connect_state = False
def connect_mongoDb():
    global connect_state
    if MONGODB_USER:
        URI = f"mongodb+srv://{MONGODB_USER}:{MONGODB_PASS}@{MONGODB_HOST}/{MONGODB_NAME}?retryWrites=true&w=majority"
        print(URI)
        try:
            connect(host = URI, ssl =  True)
        except OperationError:
            print(
                "An Invalid URI host error was received. Is your Atlas host name correct in your connection string?"
            )
        except Exception as e:
            print("error:", e)
        else:
            print("Connected to MongoDB Server!")
            connect_state = True
    else:
        print("not defined MONGODB_USER. Database not connected")
    return  connect_state

if __name__ == "__main__":
    connect_mongoDb()
