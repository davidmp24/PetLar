from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petlar.db'
app.config['SECRET_KEY'] = 'mysecretkey'
db = SQLAlchemy(app)

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer)
    adotado = db.Column(db.Boolean, default=False)

class Adotante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    rg = db.Column(db.String(20), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    telefone = db.Column(db.String(15))
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False)

db.create_all()
