from marshmallow import Schema, fields, validate

class BookSchema(Schema):
    """
    Schema for validating and deserializing complete book data.
    Used for book creation.
    """
    isbn_13 = fields.Str(required=True, validate=validate.And(
        validate.Length(equal=13),
        validate.Regexp('^[0-9]+$', error="ISBN must be numeric")
    ))
    title = fields.Str(requried=True)
    author = fields.Str(required=True)
    description = fields.Str(required=True)
    category = fields.Str(required=True, validate=validate.OneOf(["Romance", "Thriller", "Comics", "Mystery", "Action Adventure"]))
    format = fields.Str(required=True, validate=validate.OneOf(["Ebook", "Audiobook", "Paperback"]))
    length = fields.Str(required=True, validate=validate.OneOf(["Short Read", "Standard Length", "Long Read"]))
    rating = fields.Float(validate=validate.Range(min=0, max=5))
    published_year = fields.Int(required=True, validate=validate.Range(min=1970, max=2024))

class BookUpdateSchema(Schema):
    """
    Schema for validating and deserializing partial book data.
    Used for updating book information.
    """
    isbn_13 = fields.Str(required=True, validate=validate.And(
        validate.Length(equal=13),
        validate.Regexp('^[0-9]+$', error="ISBN must be numeric")
    ))
    title = fields.Str()
    author = fields.Str()
    description = fields.Str()
    category = fields.Str(validate=validate.OneOf(["Romance", "Thriller", "Comics", "Mystery", "Action Adventure"]))
    format = fields.Str(validate=validate.OneOf(["Ebook", "Audiobook", "Paperback"]))
    length = fields.Str(validate=validate.OneOf(["Short Read", "Standard Length", "Long Read"]))
    rating = fields.Float(validate=validate.Range(min=0, max=5))
    published_year = fields.Int(validate=validate.Range(min=1970, max=2024))