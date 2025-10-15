from datetime import datetime, timedelta
from functools import wraps

from flask import request
from marshmallow import ValidationError
from flask.views import MethodView
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    get_jwt_identity,
    get_jwt
)
from passlib.hash import bcrypt

from app import db
from models import User, UserCredentials
from schemas import UserSchema, RegisterSchema, LoginSchema


def role_required(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            role = claims.get('role')
            if not role or role not in allowed_roles:
                return {"Error":"Rol no autorizado"}
            return fn(*args, **kwargs)
        return wrapper
    return decorator
        

class UserAPI(MethodView):
    @jwt_required()
    def get(self):
        users = User.query.all()
        return UserSchema(many=True).dump(users)

    def post(self):
        try:
            data = UserSchema().load(request.json)
            new_user = User(
                name=data.get('name'),
                email=data.get('email')
            )
            db.session.add(new_user)
            db.session.commit()
        except ValidationError as err:
            return {"Errors": f"{err.messages}"}, 400
        return UserSchema().dump(new_user), 201


class UserDetailAPI(MethodView):
    @jwt_required()
    @role_required('admin')
    def get(self, id):
        user = User.query.get_or_404(id)
        return UserSchema().dump(user), 200
    
    
    def put(self, id):
        user = User.query.get_or_404(id)
        try: 
            data = UserSchema().load(request.json)
            user.name = data['name']
            user.email = data['email']
            db.session.commit()
            return UserSchema().dump(user), 200
        except ValidationError as err:
            return {"Error": err.messages}

    def patch(self, id):
        user = User.query.get_or_404(id)
        try: 
            data = UserSchema(partial=True).load(request.json)
            if 'name' in data:
                user.name = data.get('name')
            if 'email' in data:
                user.email = data.get('email')
            db.session.commit()
            return UserSchema().dump(user), 200
        except ValidationError as err:
            return {"Error": err.messages}
        
    def delete(self, id):
        user = User.query.get_or_404(id)
        try:
            db.session.delete(user)
            db.session.commit()
            return {"Message": "Deleted User"}, 204
        except:
            return {"Error": "No es posible borrarlo"}


class UserRegisterAPI(MethodView):
    def post(self):
        try:
            data = RegisterSchema().load(request.json)
        except ValidationError as err:
            return {"Error": err}
        
        if User.query.filter_by(email=data['email']).first():
            return {"Error": "Email en uso"}
        
        new_user = User(name=data["name"], email=data['email'])
        db.session.add(new_user)
        db.session.flush()
        password_hash = bcrypt.hash(data['password'])
        credenciales = UserCredentials(
            user_id=new_user.id,
            password_hash=password_hash,
            role=data['role']
        )
        db.session.add(credenciales)
        db.session.commit()
        return UserSchema().dump(new_user)


class AuthLoginAPI(MethodView):
    def post(self):
        try:
            data = LoginSchema().load(request.json)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        user = User.query.filter_by(email=data["email"]).first()
        if not user or not user.credential:
            return {"errors": {"credentials": ["Inválidas"]}}, 401
        if not bcrypt.verify(data["password"], user.credential.password_hash):
            return {"errors": {"credentials": ["Inválidas"]}}, 401
        identity = str(user.id)
        additional_claims =  {
            "id": user.id,
            "email": user.email,
            "role": user.credential.role,
            "name": user.name
        }
        token = create_access_token(
            identity=identity,
            additional_claims=additional_claims,
            expires_delta=timedelta(minutes=15)
        )
        return {"access_token": token}, 200
