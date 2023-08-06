


import json


from tornado.escape import to_basestring

def json_encode(value):
    """improve json decode when include datetime object"""
    return json.dumps(value,default=str).replace("</", "<\\/")


def json_decode(value):
    """Returns Python objects for the given JSON string."""
    return json.loads(to_basestring(value))
