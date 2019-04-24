from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = '6@kr$IhQ%teki}Juetg*x]U/QmKz{P<g'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


from fsnd_catalog_app.models import User
import os
# If app being run for first time, check if sqlite database
# already exists. If not, create it.
exists = os.path.isfile('/catalog.db')
if not exists:
    db.create_all()


# Temporary usr for testing
# TODO
# remove when you delete dummy test user
def get_current_user():
    if 'current_user' not in g:
        g.current_user = User(username='henok', email='henokhm2@gmail.com',
                              hashed_password=bcrypt.generate_password_hash("1234").decode('utf-8'))

    return g.current_user


get_current_user()

from fsnd_catalog_app import routes

