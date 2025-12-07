from marshmallow import Schema, fields, validate, post_load, validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from .models import LibraryItem


class LibraryItemSchema(SQLAlchemyAutoSchema):
class Meta:
model = LibraryItem
include_fk = True
load_instance = True
sqla_session = None


id = fields.Int(dump_only=True)
title = fields.Str(required=True, validate=validate.Length(min=1))
item_type = fields.Str(required=True, validate=validate.OneOf(["book", "magazine", "film", "other"]))
author_or_director = fields.Str(allow_none=True)
published_date = fields.Date(allow_none=True)
isbn = fields.Str(allow_none=True)
description = fields.Str(allow_none=True)


is_available = fields.Bool()
expected_available_date = fields.Date(allow_none=True)


@validates("expected_available_date")
def validate_expected(self, val):
# expected date must be present only when is_available is False, but we won't enforce strict coupling here
return val

class BookSchema(Schema):
	id = fields.Int(dump_only=True)
	title = fields.Str(required=True)
	author = fields.Str(required=True)
