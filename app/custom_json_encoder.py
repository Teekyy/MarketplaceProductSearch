from flask.json.provider import DefaultJSONProvider
from bson import ObjectId

class CustomJSONEncoder(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return DefaultJSONProvider.default(self, obj)