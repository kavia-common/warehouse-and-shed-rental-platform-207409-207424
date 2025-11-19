from marshmallow import Schema, fields

# PUBLIC_INTERFACE
class UserSchema(Schema):
    """Schema for serializing User instances."""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    is_owner = fields.Bool()
    # password excluded from dump

# PUBLIC_INTERFACE
class WarehouseSchema(Schema):
    """Schema for serializing Warehouse instances."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    description = fields.Str()
    city = fields.Str(required=True)
    address = fields.Str(required=True)
    owner_id = fields.Int()
    is_available = fields.Bool()
    image_url = fields.Str()
    created_at = fields.DateTime()

# PUBLIC_INTERFACE
class RentalRequestSchema(Schema):
    """Schema for serializing RentalRequest instances."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    warehouse_id = fields.Int(required=True)
    message = fields.Str()
    status = fields.Str()
    created_at = fields.DateTime()
    warehouse = fields.Nested(WarehouseSchema, dump_only=True)
