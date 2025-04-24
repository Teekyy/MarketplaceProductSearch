from flask.json.provider import DefaultJSONProvider
from bson import ObjectId

class CustomJSONEncoder(DefaultJSONProvider):
    """
    Custom JSON encoder needed because we are using Flask with MongoDB.
    It allows any ObjectId items (from MongoDB) to be serialized to JSON.
    """
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return DefaultJSONProvider.default(self, obj)