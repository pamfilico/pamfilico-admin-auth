"""Marshmallow schemas: admin login only.

Listing users, filtering, pagination — none of that belongs here. Those are
app-specific concerns; this package is only about admin **authentication**.
"""

from marshmallow import EXCLUDE, Schema, fields


class AdminLoginLoadSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(required=True)
    password = fields.Str(required=True)


class AdminLoginDataSchema(Schema):
    """Response payload for admin login."""

    accessToken = fields.Str(required=True)
    tokenType = fields.Str()
    expiresIn = fields.Int()
