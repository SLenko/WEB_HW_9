from datetime import datetime
import pika
from tqdm import tqdm
import json
import sys
from pathlib import Path

src_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(src_path))
# print("SRC_PATH:  ", src_path)

from src.DB.connect import connect_mongoDb
from src.DB.seed_to_db import seed_contacts


def seed(seed_on: bool = True) -> list[str]:
    result = []
    if connect_mongoDb():
        if seed_on:
            result = seed_contacts()
    return result


def main(seed_on: bool = True, prefer_type=None, max_records=None):
    contacts = seed(seed_on=seed_on)
    if not contacts:
        print("contacts not ready")
        return

    try:
        credentials = pika.PlainCredentials("guest", "guest")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="localhost", port=5672, credentials=credentials
            )
        )
    except pika.exceptions.AMQPConnectionError:
        print("ERROR RabbitMQ connection")
        return

    channel = connection.channel()

    exchange = "task_mock"
    routing_key = "_".join(["task_queue", prefer_type if prefer_type else "for_all"])

    channel.exchange_declare(exchange=exchange, exchange_type="direct")
    channel.queue_declare(queue=routing_key, durable=True)
    channel.queue_bind(exchange=exchange, queue=routing_key)

    for _ in range(2):
        print(f"Sending '{len(contacts)}' contacts ...")
        for i, contact in tqdm(enumerate(contacts, 1), total=len(contacts)):
            message = {
                "id": i,
                "contact_id": contact,
                "date": datetime.now().isoformat(),
                "prefer": prefer_type,
            }

            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=json.dumps(message).encode(),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
            )

    connection.close()


if __name__ == "__main__":
    main(max_records=100, prefer_type=None)
