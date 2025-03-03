# app.py
import flask
from flask import Flask, request, render_template
#import core
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')
    CORS(app)  # , origins="https://trello.com")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://boris:pass@localhost/mesync'
    db.init_app(app)

    # imports
    from routes import register_routes
    register_routes(app, db)

    migrate = Migrate(app, db)

    return app


app = Flask(__name__)
CORS(app) #, origins="https://trello.com")