from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields
from app import db
from models import User

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User #Modelo a serializar
        load_instance = True 
        sqla_session = db.session # Sesion SQLAlchemy
        include_fk = True

    id = auto_field(dump_only=True)
    name = auto_field()
    email = auto_field()

