import uuid
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import db, Admin
from werkzeug.security import generate_password_hash

with db.app.app_context():
    hashed_password = generate_password_hash("123")
    admin = Admin(username="admin", password=hashed_password)
    db.session.add(admin)
    db.session.commit()
    print("Administrador criado com sucesso!")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petlar.db'
app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)

def generate_unique_code():
    return str(uuid.uuid4().hex)  # Gerando um código único com UUID

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer)
    adotado = db.Column(db.Boolean, default=False)
    codigo_animal = db.Column(db.String(32), unique=True, nullable=False, default=generate_unique_code)  # Código único do animal

class Adotante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    rg = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(15))
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)

db.create_all()
