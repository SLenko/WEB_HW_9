from datetime import datetime

from mongoengine import EmbeddedDocument, Document, CASCADE
from mongoengine.fields import (
    IntField,
    BooleanField,
    DateTimeField,
    EmbeddedDocumentField,
    ListField,
    StringField,
    ObjectIdField,
    ReferenceField,
    DateField,
)


class Authors(Document):
    fullname = StringField()
    born_date = StringField()
    born_location = StringField()
    description = StringField()


class Tag(EmbeddedDocument):
    name = StringField()


class Quotes(Document):
    tags = ListField(StringField())
    author = ReferenceField("Authors", reverse_delete_rule=CASCADE)
    quote = StringField()


class PreferTypes(EmbeddedDocument):
    type = StringField(required=True, choices=["SMS", "EMAIL"])


class Contacts(Document):
    fullname = StringField()
    email = StringField()
    phone = StringField()
    prefer = EmbeddedDocumentField(PreferTypes)
    address = StringField()
    birthday = DateField()
    done = BooleanField(default=False)
    when_done = DateTimeField(null=True)
