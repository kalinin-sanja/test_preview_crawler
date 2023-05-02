from marshmallow import Schema, fields


class PreviewParameter(Schema):
    url = fields.URL(required=True)


class PreviewDataSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    imageUrl = fields.URL(allow_none=True)


class PreviewSchema(Schema):
    data = fields.Nested(PreviewDataSchema, required=True)


class ErrorMessageScheme(Schema):
    message = fields.Str(required=True)


class ErrorScheme(Schema):
    error = fields.Nested(ErrorMessageScheme, required=True)
