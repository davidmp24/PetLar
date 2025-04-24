from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
from werkzeug.utils import secure_filename

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
    raca = db.Column(db.String(100), nullable=True) # Tornar null=True se não for obrigatório
    sexo = db.Column(db.String(10), nullable=True) # "Macho" ou "Fêmea"
    idade = db.Column(db.Integer, nullable=True) # Idade em anos/meses? Definir unidade.

    # --- Campos do Formulário Adicionados ---
    temperamento = db.Column(db.String(200), nullable=True)
    comportamento_outros = db.Column(db.String(200), nullable=True) # Comportamento com outros animais
    comportamento_criancas = db.Column(db.String(200), nullable=True) # Comportamento com crianças
    doencas_preexistentes = db.Column(db.Text, nullable=True)
    tratamentos = db.Column(db.Text, nullable=True)
    cor = db.Column(db.String(50), nullable=True)
    tamanho = db.Column(db.String(50), nullable=True) # 'Pequeno', 'Médio', 'Grande'
    localizacao = db.Column(db.String(255), nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    foto_filename = db.Column(db.String(255), nullable=True) # Nome do arquivo da foto

    # --- Outros Campos ---
    adotado = db.Column(db.Boolean, default=False)
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp()) # Útil ter data de cadastro

    def __repr__(self):
        return f'<Animal {self.id}: {self.nome} ({self.especie})>'

    # (Opcional) Propriedade para obter URL da foto
    @property
    def foto_url(self):
        if self.foto_filename:
            # Retorna o URL para a foto dentro da pasta static/uploads/animais
            return url_for('static', filename=f'uploads/animais/{self.foto_filename}', _external=True)
        else:
            # Retorna URL de uma imagem placeholder se não houver foto
            return url_for('static', filename='images/placeholder_animal.png', _external=True) # Exemplo

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads', 'animais')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Garanta que a pasta de upload exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

import os
from werkzeug.utils import secure_filename
from flask import flash # Certifique-se que flash está importado

# ... (configuração do UPLOAD_FOLDER como mostrado anteriormente) ...
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/cadastrar_animal', methods=['GET', 'POST'])
def cadastrar_animal():
    if 'admin' not in session:
        return redirect(url_for('login'))

    # Código do animal pode ser derivado do ID após salvar, ou gerado aqui se necessário
    # Se for para exibir no GET, calcule aqui:
    # ultimo_animal = Animal.query.order_by(Animal.id.desc()).first()
    # codigo_para_exibir = (ultimo_animal.id + 1) if ultimo_animal else 1

    if request.method == 'POST':
        # --- Ler dados do formulário (usando .get()) ---
        nome = request.form.get('nome')
        especie = request.form.get('especie')
        raca = request.form.get('raca')
        sexo = request.form.get('sexo')
        idade_str = request.form.get('idade')
        temperamento = request.form.get('temperamento')
        comportamento_outros = request.form.get('comportamento_outros')
        comportamento_criancas = request.form.get('comportamento_criancas')
        doencas_preexistentes = request.form.get('doencas_preexistentes')
        tratamentos = request.form.get('tratamentos')
        cor = request.form.get('cor')
        tamanho = request.form.get('tamanho')
        localizacao = request.form.get('localizacao')
        descricao = request.form.get('descricao')
        foto = request.files.get('foto')

        # --- Validação Básica (Exemplo) ---
        erros = []
        if not nome:
            erros.append('O nome do animal é obrigatório.')
        if not especie:
            erros.append('A espécie do animal é obrigatória.')
        # Adicione mais validações conforme necessário

        # --- Conversão de Idade ---
        idade = None
        if idade_str:
            try:
                idade = int(idade_str)
                if idade < 0:
                    erros.append('A idade não pode ser negativa.')
            except ValueError:
                erros.append('A idade deve ser um número.')

        # --- Tratamento da Foto ---
        foto_filename = None
        if foto and foto.filename != '':
            if allowed_file(foto.filename):
                # Gera um nome de arquivo seguro para evitar conflitos/ataques
                foto_filename = secure_filename(f"{uuid.uuid4()}_{foto.filename}") # Adiciona UUID para unicidade
                foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto_filename)
                try:
                    foto.save(foto_path)
                except Exception as e:
                    erros.append(f"Erro ao salvar a foto: {e}")
                    foto_filename = None # Não salva o nome do arquivo se houve erro
            else:
                erros.append('Tipo de arquivo de foto não permitido.')

        # --- Se houver erros, re-renderizar o formulário ---
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            # Recalcular codigo_para_exibir se necessário para re-renderizar
            # ultimo_animal = Animal.query.order_by(Animal.id.desc()).first()
            # codigo_para_exibir = (ultimo_animal.id + 1) if ultimo_animal else 1
            # É importante repassar os dados que o usuário já digitou de volta para o template
            # usando o argumento 'value' nos inputs ou usando Flask-WTF que faz isso automaticamente.
            return render_template('cadastrar_animal.html') # codigo_animal=codigo_para_exibir)

        # --- Se tudo ok, criar e salvar o objeto ---
        novo_animal = Animal(
            nome=nome,
            especie=especie,
            raca=raca,
            sexo=sexo,
            idade=idade,
            temperamento=temperamento,
            comportamento_outros=comportamento_outros,
            comportamento_criancas=comportamento_criancas,
            doencas_preexistentes=doencas_preexistentes,
            tratamentos=tratamentos,
            cor=cor,
            tamanho=tamanho,
            localizacao=localizacao,
            descricao=descricao,
            foto_filename=foto_filename # Salva o nome do arquivo da foto
            # 'adotado' e 'data_cadastro' terão valores padrão
        )

        try:
            db.session.add(novo_animal)
            db.session.commit()
            flash(f'Animal "{novo_animal.nome}" cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_animais'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar no banco de dados: {e}', 'danger')
            # app.logger.error(f"Erro DB: {e}") # Logar erro é bom
            # Tenta remover a foto salva se o commit falhar
            if foto_filename:
                 try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
                 except OSError:
                     pass # Ignora erro se não conseguir remover
            # Recalcular codigo_para_exibir se necessário
            # ultimo_animal = Animal.query.order_by(Animal.id.desc()).first()
            # codigo_para_exibir = (ultimo_animal.id + 1) if ultimo_animal else 1
            return render_template('cadastrar_animal.html') #, codigo_animal=codigo_para_exibir)

    # --- Requisição GET ---
    # Calcular codigo_para_exibir se necessário para o GET
    # ultimo_animal = Animal.query.order_by(Animal.id.desc()).first()
    # codigo_para_exibir = (ultimo_animal.id + 1) if ultimo_animal else 1
    return render_template('cadastrar_animal.html') #, codigo_animal=codigo_para_exibir)

@app.route('/listar_animais')
def listar_animais():
    if 'admin' not in session:
        return redirect(url_for('login'))
    animais = Animal.query.all()
    return render_template('listar_animais.html', animais=animais)

from sqlalchemy import func

# --- Rota para Ver Detalhes ---
@app.route('/animal/<int:animal_id>')
def detalhes_animal(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    animal = Animal.query.get_or_404(animal_id) # Pega o animal ou retorna 404 se não existir
    # Você precisará criar o template 'detalhes_animal.html'
    return render_template('detalhes_animal.html', animal=animal)

# --- Rota para Editar (GET - Mostrar formulário preenchido) ---
@app.route('/editar_animal/<int:animal_id>', methods=['GET'])
def editar_animal_form(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    animal = Animal.query.get_or_404(animal_id)
    # Você precisará criar/adaptar o template 'editar_animal.html'
    # Ele será muito parecido com 'cadastrar_animal.html', mas preenchido
    return render_template('editar_animal.html', animal=animal)

# --- Rota para Editar (POST - Processar formulário) ---
@app.route('/editar_animal/<int:animal_id>', methods=['POST'])
def editar_animal_submit(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    animal = Animal.query.get_or_404(animal_id)

    # --- Ler dados do formulário (similar ao cadastro) ---
    nome = request.form.get('nome')
    especie = request.form.get('especie')
    raca = request.form.get('raca')
    sexo = request.form.get('sexo')
    idade_str = request.form.get('idade')
    temperamento = request.form.get('temperamento')
    comportamento_outros = request.form.get('comportamento_outros')
    comportamento_criancas = request.form.get('comportamento_criancas')
    doencas_preexistentes = request.form.get('doencas_preexistentes')
    tratamentos = request.form.get('tratamentos')
    cor = request.form.get('cor')
    tamanho = request.form.get('tamanho')
    localizacao = request.form.get('localizacao')
    descricao = request.form.get('descricao')
    foto = request.files.get('foto')

    # --- Validação (igual ou similar ao cadastro) ---
    erros = []
    if not nome: erros.append('O nome do animal é obrigatório.')
    if not especie: erros.append('A espécie do animal é obrigatória.')
    idade = animal.idade # Mantem a idade antiga se não for alterada
    if idade_str:
        try:
            idade = int(idade_str)
            if idade < 0: erros.append('A idade não pode ser negativa.')
        except ValueError: erros.append('A idade deve ser um número.')
    # Adicione mais validações

    # --- Tratamento da Foto (Substituição) ---
    foto_filename = animal.foto_filename # Mantem foto antiga por padrão
    if foto and foto.filename != '':
        if allowed_file(foto.filename):
            # Apaga a foto antiga ANTES de salvar a nova (se existir)
            if animal.foto_filename:
                old_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], animal.foto_filename)
                if os.path.exists(old_photo_path):
                    try:
                        os.remove(old_photo_path)
                    except OSError as e:
                        app.logger.error(f"Erro ao remover foto antiga {animal.foto_filename}: {e}") # Logar erro
            # Salva a nova foto
            foto_filename = secure_filename(f"{uuid.uuid4()}_{foto.filename}")
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto_filename)
            try:
                foto.save(foto_path)
            except Exception as e:
                erros.append(f"Erro ao salvar a nova foto: {e}")
                foto_filename = animal.foto_filename # Reverte para a antiga se erro
        else:
            erros.append('Tipo de arquivo de foto não permitido.')

    # --- Se houver erros, re-renderizar o formulário de edição ---
    if erros:
        for erro in erros:
            flash(erro, 'danger')
        # Re-renderiza o formulário de edição passando o objeto animal (com dados não salvos)
        return render_template('editar_animal.html', animal=animal)

    # --- Atualizar os dados do objeto animal ---
    animal.nome = nome
    animal.especie = especie
    animal.raca = raca
    animal.sexo = sexo
    animal.idade = idade
    animal.temperamento = temperamento
    animal.comportamento_outros = comportamento_outros
    animal.comportamento_criancas = comportamento_criancas
    animal.doencas_preexistentes = doencas_preexistentes
    animal.tratamentos = tratamentos
    animal.cor = cor
    animal.tamanho = tamanho
    animal.localizacao = localizacao
    animal.descricao = descricao
    animal.foto_filename = foto_filename # Atualiza o nome do arquivo da foto

    try:
        db.session.commit() # Salva as alterações
        flash(f'Animal "{animal.nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('listar_animais'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar o animal: {e}', 'danger')
        # app.logger.error(f"Erro DB Update: {e}")
        return render_template('editar_animal.html', animal=animal)


# --- Rota para Excluir ---
@app.route('/excluir_animal/<int:animal_id>', methods=['POST'])
def excluir_animal(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    animal = Animal.query.get_or_404(animal_id)

    foto_filename_to_delete = animal.foto_filename # Guarda o nome antes de deletar o objeto

    try:
        db.session.delete(animal)
        db.session.commit()

        # Tenta remover o arquivo da foto associada APÓS o commit bem sucedido
        if foto_filename_to_delete:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], foto_filename_to_delete)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    # Logar o erro, mas não impedir o fluxo principal
                    app.logger.error(f"Erro ao remover arquivo de foto {foto_filename_to_delete}: {e}")
                    flash(f'Animal excluído, mas houve um erro ao remover o arquivo de foto associado.', 'warning')

        flash(f'Animal "{animal.nome}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir o animal: {e}', 'danger')
        # app.logger.error(f"Erro DB Delete: {e}")

    return redirect(url_for('listar_animais'))


# --- Rota para Marcar como Adotado ---
@app.route('/marcar_adotado/<int:animal_id>', methods=['POST'])
def marcar_adotado(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    animal = Animal.query.get_or_404(animal_id)

    try:
        animal.adotado = True # Marca como adotado
        db.session.commit()
        flash(f'Animal "{animal.nome}" marcado como adotado!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao marcar o animal como adotado: {e}', 'danger')
        # app.logger.error(f"Erro DB Mark Adopted: {e}")

    return redirect(url_for('listar_animais'))

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