"""Marshmallow schemas: admin login + user list."""

from marshmallow import EXCLUDE, Schema, fields, validate


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


class AdminUserListQuerySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    currentPage = fields.Int(load_default=1, validate=validate.Range(min=1))
    pageSize = fields.Int(load_default=20, validate=validate.Range(min=1, max=200))
    email_contains = fields.Str(load_default="")


class DefaultAdminUserListItemSchema(Schema):
    """
    Default user serializer. Apps with extra columns should pass their own
    serializer via ``AdminAuthConfig.user_serializer`` or pass ``user_serializer=``
    to ``build_admin_blueprint``.
    """

    id = fields.Function(lambda obj: str(obj.id) if obj.id is not None else None)
    email = fields.Str(allow_none=True)
    name = fields.Str(allow_none=True)
    created_at = fields.Function(
        lambda obj: obj.created_at.isoformat() if getattr(obj, "created_at", None) else None
    )
    last_updated = fields.Function(
        lambda obj: obj.last_updated.isoformat() if getattr(obj, "last_updated", None) else None
    )
