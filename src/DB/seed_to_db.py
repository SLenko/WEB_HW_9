import json
from faker import Faker
from faker.providers import DynamicProvider
from tqdm import tqdm
from random import choice
import sys
from pathlib import Path

src_path = Path(__file__).resolve().parent.parent
sys.path.append(str(src_path) + "/DB")
from models import Authors, Quotes, Contacts, PreferTypes


def load_json_files_from_dir(json_dir: Path) -> dict:
    result = {}
    if json_dir.exists():
        for file_item in json_dir.glob("*.json"):
            if file_item.is_file():
                with file_item.open("r", encoding="UTF-8") as fp:
                    result[file_item.stem] = json.load(fp)
    return result


def seeds(debug: bool = False):
    json_dir = Path(__file__).parent.parent.joinpath("data")
    # print("PATH:  ", json_dir)
    json_dict = load_json_files_from_dir(json_dir)
    # print("json_dict:  ", json_dict)

    if not json_dict:
        print("Files JSON not found")
        return 1

    authors_id = {}
    authors_object = "authors"  # Separate variable for authors
    print(f"Add {authors_object}...")
    if authors_object in json_dict:
        Authors.drop_collection()
        so = json_dict.get(authors_object)
        for author in tqdm(
            so, total=len(so), desc="processing in progress, processed:"
        ):
            rec = Authors(**author).save()
            authors_id[author.get("fullname")] = rec.id
            print(f"added {authors_object} id: {rec.id} ({rec.fullname})")

    quotes_object = "quotes"  # Separate variable for quotes
    print(f"Add {quotes_object}...")
    if quotes_object in json_dict:
        Quotes.drop_collection()
        so = json_dict.get(quotes_object)
        for quote in tqdm(so, total=len(so)):
            author = quote.get("author")
            author_id = authors_id.get(author)
            if author_id:
                quote["author"] = author_id
                rec = Quotes(**quote).save()
                print(f"added {quotes_object} id: {rec.id}")
                # author_by_id = Authors.objects(id=author_id).first()
                # print(f"added quote of quote.author {author}, author id [{author_id}] = ({author_by_id.fullname}) ")

    # authors = Authors.objects()
    # for record in authors:
    #     print("-------------------")
    #     print(record.to_mongo().to_dict())

    # quotes = Quotes.objects()
    # for record in quotes:
    #     print("-------------------")
    #     print(record.to_mongo().to_dict())

    # find1 = Authors.objects(fullname="Steve Martin").delete()
    # print("deleted", find1)

    # find1 = Authors.objects()
    # for record in find1:
    #     print("-------------------")
    #     print(record.to_mongo().to_dict())


def seed_prefer_types() -> list[str]:
    result = {
        "type_sms": PreferTypes(type="SMS"),
        "type_email": PreferTypes(type="EMAIL"),
    }
    return result


def seed_contacts(
    max_records: int = 20, prefer_type: str = None, drop: bool = True) -> list[str]:
    # print("PREFER_TYPE:  >>> ", prefer_type)
    prefer_types_provider = DynamicProvider(
        provider_name="prefer_types", elements=["type_email", "type_sms"]
    )
    fake = Faker("uk-UA")
    fake.add_provider(prefer_types_provider)
    types = seed_prefer_types()

    print(f"Add contacts: {max_records} ...")
    if drop:
        Contacts.drop_collection()
    result = []
    for i in tqdm(range(max_records), desc="Contacts Seed Progress"):
        obj = {
            "fullname": " ".join([fake.first_name(), fake.last_name()]),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "birthday": fake.date_between(),
            "prefer": types.get(fake.prefer_types()),
        }
        # print("OBJ>>>> ",obj["prefer"].type)
        contact = Contacts(**obj).save()
        result.append(str(contact.id))
    return result

if __name__ == "__main__":
    from connect import connect_mongoDb

    if connect_mongoDb():
        seeds()
        seed_contacts(20)
