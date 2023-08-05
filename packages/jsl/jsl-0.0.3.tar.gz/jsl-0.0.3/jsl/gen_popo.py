import redbaron
from jsl import Document, StringField


class File(Document):
    name = StringField(required=True)
    content = StringField(required=True)


red = redbaron.RedBaron("class X(object):\n    pass")
class_node = red[0]
class_node.name = 'File'
class_node.value.pop()
class_node.value.append('test = 123')


i = redbaron.RedBaron("def __init__(): pass")
init = i[0]
i.arguments = redbaron.CommaProxyList(redbaron.NodeList())
redbaron.DefArgumentNode()
for field_name, field in File._fields.iteritems():
    print field_name, field
