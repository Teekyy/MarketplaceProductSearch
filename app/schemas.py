from marshmallow import Schema, fields, validate

class BookSchema(Schema):
    title = fields.Str(requried=True)
    author = fields.Str(required=True)
    description = fields.Str(required=True)
    category = fields.Str(required=True, validate=validate.Oneof(["Romance", "Thriller", "Comics", "Mystery", "Action Adventure"]))
    format = fields.Str(required=True, validate=validate.Oneof(["Ebook", "Audiobook", "Paperback"]))
    length = fields.Str(required=True, validate=validate.Oneof(["Short Read", "Standard Length", "Long Read"]))
    published_year = fields.Int(required=True)

class BookUpdateSchema(Schema):
    title = fields.Str()
    author = fields.Str()
    description = fields.Str()
    category = fields.Str(validate=validate.Oneof(["Romance", "Thriller", "Comics", "Mystery", "Action Adventure"]))
    format = fields.Str(validate=validate.Oneof(["Ebook", "Audiobook", "Paperback"]))
    length = fields.Str(validate=validate.Oneof(["Short Read", "Standard Length", "Long Read"]))
    published_year = fields.Int()