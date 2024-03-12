from datetime import datetime
import pika
import sys
import time
import json
from pathlib import Path
src_path = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(src_path))
# print("SRC_PATH:  ", src_path)

from src.DB.connect import connect_mongoDb
from src.DB.models import Contacts, PreferTypes


def sending_task(message):
    # print(f"email_task: {message=}")
    id = message.get("contact_id")
    # prefer_type = message.get("prefer")
    if id:
        contact = Contacts.objects(id=id).first()
    if  contact:
        prefer_type = contact.prefer.type
        match prefer_type:
            case "SMS":
                sms_task(contact)
            case "EMAIL":
                email_task(contact)
            case _:
                print("Prefer type is unknown, use email by default")
                email_task(contact)
    return


def email_task(contact):
    # print(f"email_task: {message=}")
    # id = message.get("contact_id")
    # if id:
    #     contact = Contacts.objects(id=id).first()
    if contact:
        if not contact.done:
            print(f"Name: {contact.fullname} ")
            print(f"Sending email to: {contact.email}")
            time.sleep(1)
            contact.update(done=True, when_done=datetime.now())
        else:
            print("Task already done")
    return


def sms_task(contact):
    # print(f"email_task: {message=}")
    # id = message.get("contact_id")
    # if id:
    #     contact = Contacts.objects(id=id).first()
    if contact:
        if not contact.done:
            print(f"Name: {contact.fullname} ")
            print(f"Sending SMS to: {contact.phone}")
            time.sleep(1)
            contact.update(done=True, when_done=datetime.now())
        else:
            print("Task already done")
    return


def main(prefer_type: str):
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
    channel.queue_declare(queue="task_queue", durable=True)

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        print(f" [x] Received id: {message.get('id')}")
        prefer_type: PreferTypes = message.get("prefer")
        print(f"{prefer_type=}")
        sending_task(message)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    if connect_mongoDb():
        queue = "_".join(["task_queue", prefer_type])
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue, on_message_callback=callback)

        print(" [*] Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()
    else:
        print("Database not connected")


if __name__ == "__main__":
    try:
        main(prefer_type="for_all")
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0)
