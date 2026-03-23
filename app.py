from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tcg.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
                id = db.Column(db.Integer, primary_key=True)
                username = db.Column(db.String(80), unique=True, nullable=False)
                email = db.Column(db.String(120), unique=True, nullable=False)
                password = db.Column(db.String(200), nullable=False)
                cards = db.relationship('Card', backref='owner', lazy=True)
class Card(db.Model):
                id = db.Column(db.Integer, primary_key=True)
                cardname = db.Column(db.String(120), nullable=False)
                set_name = db.Column(db.String(120), nullable=False)
                rarity = db.Column(db.String(120), nullable=False)
                condition = db.Column(db.String(120), nullable=False)
                holo = db.Column(db.Boolean, nullable=True)
                reverse_holo = db.Column(db.Boolean, nullable=True)
                first_edition = db.Column(db.Boolean, nullable=True)
                estimated_value = db.Column(db.Float, nullable=True)
                quantity = db.Column(db.Integer, nullable=True)
                user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
                notes = db.Column(db.String(500), nullable=True)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))