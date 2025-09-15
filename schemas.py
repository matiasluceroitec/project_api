from app import db

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from models import User

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True 
        sqla_session = db.session

    id = auto_field(dump_only=True)
    name = auto_field()
    email = auto_field()