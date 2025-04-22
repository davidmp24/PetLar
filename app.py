from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petlar.db'

db = SQLAlchemy(app)  # Inicialize SQLAlchemy *apenas aqui*

# Modelos definidos dentro do contexto da aplicação
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer)
    adotado = db.Column(db.Boolean, default=False)

class Adotante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    rg = db.Column(db.String(20), unique=True, nullable=False)
    cpf = db.Column(db.String(20), unique=True, nullable=False)
    endereco = db.Column(db.String(255), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    animal_interesse = db.Column(db.String(100), nullable=False)
    tipo_animal_interesse = db.Column(db.String(50), nullable=False)
    justificativa_adocao = db.Column(db.Text)
    tem_outros_animais = db.Column(db.String(3), nullable=False)
    tempo_sozinho = db.Column(db.Integer)
    quantidade_animais = db.Column(db.Integer)
    tipos_animais = db.Column(db.String(200))

def criar_admin():
    with app.app_context():
        # db.init_app(app)  # REMOVA ESTA LINHA
        if not Admin.query.filter_by(username="admin").first():
            hashed_password = generate_password_hash("123")
            admin = Admin(username="admin", password=hashed_password)
            db.session.add(admin)
            db.session.commit()
            print("Administrador criado com sucesso!")

@app.route('/')
def home():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin'] = username
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Usuário ou senha inválidos!")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', page="dashboard")

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

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

from sqlalchemy import func

@app.route('/cadastrar_adotante', methods=['GET', 'POST'])
def cadastrar_adotante():
    if 'admin' not in session:
        return redirect(url_for('login'))

    # Encontre o maior ID existente e adicione 1
    ultimo_adotante = Adotante.query.order_by(Adotante.id.desc()).first()
    if ultimo_adotante:
        proximo_id = ultimo_adotante.id + 1
    else:
        proximo_id = 0

    if request.method == 'POST':
        nome_completo = request.form['nome_completo']
        rg = request.form['rg']
        cpf = request.form['cpf']
        endereco = request.form['endereco']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        cep = request.form['cep']
        telefone = request.form['telefone']
        email = request.form['email']
        animal_interesse = request.form['animal_interesse']
        tipo_animal_interesse = request.form['tipo_animal_interesse']
        justificativa_adocao = request.form['justificativa_adocao']
        tem_outros_animais = request.form['tem_outros_animais']
        tempo_sozinho = request.form['tempo_sozinho']
        quantidade_animais = request.form.get('quantidade_animais')
        tipos_animais = request.form.get('tipos_animais')

        novo_adotante = Adotante(
            nome_completo=nome_completo,
            rg=rg,
            cpf=cpf,
            endereco=endereco,
            bairro=bairro,
            cidade=cidade,
            cep=cep,
            telefone=telefone,
            email=email,
            animal_interesse=animal_interesse,
            tipo_animal_interesse=tipo_animal_interesse,
            justificativa_adocao=justificativa_adocao,
            tem_outros_animais=tem_outros_animais,
            tempo_sozinho=tempo_sozinho,
            quantidade_animais=quantidade_animais if quantidade_animais else None,
            tipos_animais=tipos_animais if tipos_animais else None
        )

        db.session.add(novo_adotante)  # Corrija a indentação aqui
        db.session.commit() # E aqui
        flash('Adotante cadastrado com sucesso!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('cadastrar_adotante.html', proximo_id=proximo_id)

if __name__ == '__main__':
    with app.app_context():
        # db.init_app(app)  # REMOVA ESTA LINHA
        db.create_all()  # Crie as tabelas *dentro* do contexto da aplicação
        criar_admin()  # Garante que o admin existe no banco
    app.run(debug=True)