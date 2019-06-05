from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '6@kr$IhQ%teki}Juetg*x]U/QmKz{P<g'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
bootstrap = Bootstrap(app)


# PEP8 violation to avoid circular imports
from fsnd_catalog_app.models import User

# If app being run for first time, check if sqlite database
# already exists. If not, create it.
exists = os.path.isfile('/catalog.db')
if not exists:
    db.create_all()

# PEP8 violation to avoid circular imports
from fsnd_catalog_app import routes

