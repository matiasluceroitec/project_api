from flask import Flask, request
from models import (
    db,
    Movie,
    User, 
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://BD2021:BD2021itec@143.198.156.171:3306/movies_pp1'
)
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False
db.init_app(app)

@app.route('/users', methods=['POST', 'GET'])
def users():
    if request.method == 'POST':
        data = request.json
        name = data.get('name')
        email = data.get('email')
        new_user = User(name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return {
            "name":new_user.name,
            "email":new_user.email
        },201

    users = User.query.all()
    return [
        {
            "user": user.name,
            "email": user.email
        } for user in users
    ]

@app.route(
    '/users/<int:id>',
    methods=['GET', 'PUT', 'PATCH', 'DELETE']
)
def user(id):
    user = User.query.get_or_404(id)
    if request.method == 'PUT':
        data = request.json
        if 'email' and 'name' in data:
            user.email = data['email']
            user.name = data['name']
            db.session.commit()

    if request.method == 'PATCH':
        data = request.json
        if 'email' in data:
            user.email = data['email']
        if 'name' in data:
            user.name = data['name']
        db.session.commit()
    if request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return {"Message": "Deleted user"}, 204

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email
    }, 200


@app.route('/movies')
def movies():
    movies = Movie.query.all()
    return [
        {
            "title": movie.title,
            "year": movie.year,
            #"genres": movie.genres
        } for movie in movies
    ]


if __name__ == '__main__':
    app.run(debug=True)