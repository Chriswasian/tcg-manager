from flask import Flask, render_template, request, redirect, url_for, flash
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

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))
            
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
    flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        if existing_user or existing_email:
            flash('Username or email already taken')
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')
        
@app.route('/dashboard')
@login_required
def dashboard():
      cards = Card.query.filter_by(user_id=current_user.id).all()
      return render_template('dashboard.html', cards=cards)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add():
      if request.method == 'POST':
            card = Card(
            cardname=request.form['cardname'],
            set_name=request.form['set_name'],
            rarity=request.form['rarity'],
            condition=request.form['condition'],
            holo=bool(request.form.get('holo')),
            reverse_holo=bool(request.form.get('reverse_holo')),
            first_edition=bool(request.form.get('first_edition')),
            estimated_value=float(request.form.get('estimated_value') or 0),
            quantity=int(request.form.get('quantity') or 1),
            notes=request.form.get('notes', ''),
            user_id=current_user.id)
            db.session.add(card)
            db.session.commit()
            return redirect(url_for('dashboard'))
      return render_template('add_card.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_card(id):
      card = Card.query.get_or_404(id)
      if card.user_id != current_user.id:
        return redirect(url_for('dashboard'))
      if request.method == 'POST':
        card.cardname = request.form['cardname']
        card.set_name = request.form['set_name']
        card.rarity = request.form['rarity']
        card.condition = request.form['condition']
        card.holo = bool(request.form.get('holo'))
        card.reverse_holo = bool(request.form.get('reverse_holo'))
        card.first_edition = bool(request.form.get('first_edition'))
        card.estimated_value = float(request.form.get('estimated_value') or 0)
        card.quantity = int(request.form.get('quantity') or 1)
        card.notes = request.form.get('notes', '')
        db.session.commit()
        return redirect(url_for('dashboard'))
      return render_template('edit_card.html', card=card)

@app.route('/delete/<int:id>')
@login_required
def delete_card(id):
      card = Card.query.get_or_404(id)
      if card.user_id == current_user.id:
        db.session.delete(card)
        db.session.commit()
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
     with app.app_context():
        db.create_all()
app.run(debug=True) 
      
      

      


      

