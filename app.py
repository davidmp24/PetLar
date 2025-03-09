from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petlar.db'
db = SQLAlchemy(app)

# Modelo para Administrador
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Modelo para Animais
class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    idade = db.Column(db.Integer)
    descricao = db.Column(db.Text)
    adotado = db.Column(db.Boolean, default=False)

# Modelo para Adotantes
class Adotante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    rg = db.Column(db.String(20), unique=True, nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    animal_interesse = db.Column(db.String(100), nullable=False)

@app.route('/')
def home():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))  # Redireciona para o dashboard após o login

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Credenciais inválidas!")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/cadastrar_animal', methods=['GET', 'POST'])
def cadastrar_animal():
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome = request.form['nome']
        especie = request.form['especie']
        idade = request.form['idade']
        descricao = request.form['descricao']
        novo_animal = Animal(nome=nome, especie=especie, idade=idade, descricao=descricao)
        db.session.add(novo_animal)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('cadastrar_animal.html')

@app.route('/listar_animais')
def listar_animais():
    if 'admin' not in session:
        return redirect(url_for('login'))
    animais = Animal.query.all()
    return render_template('listar_animais.html', animais=animais)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
