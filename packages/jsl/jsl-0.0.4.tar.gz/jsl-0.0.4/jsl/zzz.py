from jsl import Document, StringField


class File(Document):
    name = StringField(required=True)
    content = StringField(required=True)