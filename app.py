from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
from werkzeug.utils import secure_filename
import os
from flask import flash # Certifique-se que flash está importado

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

# --- Configuração de Upload ---
UPLOAD_FOLDER_BASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')
# Define especificamente a pasta para uploads de ADOTANTES
UPLOAD_FOLDER_ADOTANTES = os.path.join(UPLOAD_FOLDER_BASE, 'adotantes')
# Define a configuração que será usada pela rota
app.config['UPLOAD_FOLDER_ADOTANTES'] = UPLOAD_FOLDER_ADOTANTES
# Garante que a pasta exista
os.makedirs(app.config['UPLOAD_FOLDER_ADOTANTES'], exist_ok=True)

# (Manter também a configuração para animais, se necessário)
UPLOAD_FOLDER_ANIMAIS = os.path.join(UPLOAD_FOLDER_BASE, 'animais')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_ANIMAIS # Ou outro nome de config
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
    foto_pessoal_filename = db.Column(db.String(255), nullable=True)
    foto_local_filename = db.Column(db.String(255), nullable=True)
    tem_criancas = db.Column(db.String(3), nullable=True) # 'Sim' ou 'Nao' - Tornar nullable=True por segurança inicial
    quantidade_criancas = db.Column(db.Integer, nullable=True) # Só aplicável se tem_criancas == 'Sim'
    idades_criancas = db.Column(db.Text, nullable=True) # Armazenar como texto (ex: "2, 5 e 10 anos")
    restricoes_criancas = db.Column(db.Text, nullable=True) # Alergias ou outras restrições
    
@property
def foto_pessoal_url(self):
    if self.foto_pessoal_filename:
        return url_for('static', filename=f'uploads/adotantes/{self.foto_pessoal_filename}', _external=True)
    return url_for('static', filename='images/placeholder_adotante.png', _external=True) # Placeholder pessoa

@property
def foto_local_url(self):
    if self.foto_local_filename:
        return url_for('static', filename=f'uploads/adotantes/{self.foto_local_filename}', _external=True)
    return url_for('static', filename='images/placeholder_local.png', _external=True) # Placeholder local    

def criar_admin():
    with app.app_context():
        # db.init_app(app)  # REMOVA ESTA LINHA
        if not Admin.query.filter_by(username="admin").first():
            hashed_password = generate_password_hash("123")
            admin = Admin(username="admin", password=hashed_password)
            db.session.add(admin)
            db.session.commit()
            print("Administrador criado com sucesso!")

def remover_arquivo_se_existe(diretorio, nome_arquivo):
    """Função auxiliar para remover um arquivo se o nome for válido e ele existir."""
    # Só prossegue se ambos diretório e nome_arquivo forem válidos (não None/vazios)
    if diretorio and nome_arquivo:
        caminho_completo = os.path.join(diretorio, nome_arquivo)
        if os.path.exists(caminho_completo):
            try:
                os.remove(caminho_completo)
                app.logger.info(f"Arquivo removido: {caminho_completo}")
                return True
            except OSError as e:
                app.logger.error(f"Erro ao remover arquivo {caminho_completo}: {e}")
    return False        

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

# ... (configuração do UPLOAD_FOLDER como mostrado anteriormente) ...
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# --- Rota para Marcar como Disponível ---
@app.route('/marcar_disponivel/<int:animal_id>', methods=['POST'])
def marcar_disponivel(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login')) # Proteção: Apenas admin pode fazer isso

    animal = Animal.query.get_or_404(animal_id) # Pega o animal ou retorna 404

    # Verifica se o animal realmente estava adotado (opcional, mas boa prática)
    if not animal.adotado:
        flash(f'O animal "{animal.nome}" já está marcado como disponível.', 'info')
        return redirect(url_for('listar_animais'))

    try:
        animal.adotado = False # Define o status como NÃO adotado
        db.session.commit()
        flash(f'Animal "{animal.nome}" marcado como disponível novamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao marcar o animal como disponível: {e}', 'danger')
        # app.logger.error(f"Erro DB Mark Available: {e}") # Logar erro

    return redirect(url_for('listar_animais')) # Redireciona de volta para a lista

# --- Rota para Cadastrar Adotante (GET e POST) ---
@app.route('/cadastrar_adotante', methods=['GET', 'POST'])
def cadastrar_adotante():
    # Verifica se o administrador está logado
    if 'admin' not in session:
        return redirect(url_for('login'))

    # Busca animais disponíveis ANTES de verificar o método da requisição
    # Isso garante que a lista esteja disponível para GET e para re-renderização em POST com erros
    try:
        animais_disponiveis = Animal.query.filter_by(adotado=False).order_by(Animal.nome).all()
    except Exception as e:
        flash(f"Erro ao buscar animais disponíveis: {e}", "warning")
        app.logger.error(f"Erro ao buscar animais disponíveis: {e}")
        animais_disponiveis = [] # Define como lista vazia em caso de erro

    # Processa o formulário se a requisição for POST
    if request.method == 'POST':
        # --- Ler dados do formulário ---
        nome_completo = request.form.get('nome_completo')
        rg = request.form.get('rg')
        cpf = request.form.get('cpf')
        endereco = request.form.get('endereco')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        cep = request.form.get('cep')
        telefone = request.form.get('telefone')
        email = request.form.get('email')
        animal_interesse = request.form.get('animal_interesse') # Será o nome do animal selecionado
        tipo_animal_interesse = request.form.get('tipo_animal_interesse') # Pode se tornar redundante
        justificativa_adocao = request.form.get('justificativa_adocao')
        tem_outros_animais = request.form.get('tem_outros_animais')
        tempo_sozinho_str = request.form.get('tempo_sozinho')
        quantidade_animais_str = request.form.get('quantidade_animais')
        tipos_animais = request.form.get('tipos_animais')
        tem_criancas = request.form.get('tem_criancas')
        quantidade_criancas_str = request.form.get('quantidade_criancas')
        idades_criancas = request.form.get('idades_criancas')
        restricoes_criancas = request.form.get('restricoes_criancas')
        foto_pessoal = request.files.get('foto_pessoal')
        foto_local = request.files.get('foto_local')

        # Inicializa a lista de erros
        erros = []

        # --- Validações (campos obrigatórios, formato, unicidade, etc.) ---
        if not nome_completo: erros.append("Nome completo é obrigatório.")
        if not rg: erros.append("RG é obrigatório.")
        if not cpf:
            erros.append("CPF é obrigatório.")
        else:
            cpf_existente = Adotante.query.filter_by(cpf=cpf).first()
            if cpf_existente:
                erros.append(f'O CPF "{cpf}" já está cadastrado. Por favor, insira um CPF diferente.')
        if not endereco: erros.append("Endereço é obrigatório.")
        if not bairro: erros.append("Bairro é obrigatório.")
        if not cidade: erros.append("Cidade é obrigatória.")
        if not cep: erros.append("CEP é obrigatório.")
        if not telefone: erros.append("Telefone é obrigatório.")
        if not email: erros.append("Email é obrigatório.")
        if not animal_interesse: erros.append("Selecione um animal de interesse.") # Atualizada msg
        if not tipo_animal_interesse: erros.append("Tipo de animal de interesse é obrigatório.") # Manter ou remover?
        if not justificativa_adocao: erros.append("Justificativa é obrigatória.")
        if not tem_outros_animais: erros.append("Informe se possui outros animais.")
        if not tem_criancas: erros.append("Informe se há crianças na residência.")

        # --- Processar Foto Pessoal ---
        foto_pessoal_filename_salvar = None
        if foto_pessoal and foto_pessoal.filename != '':
            if allowed_file(foto_pessoal.filename):
                nome_seguro = secure_filename(f"{uuid.uuid4()}_{foto_pessoal.filename}")
                caminho = os.path.join(app.config['UPLOAD_FOLDER_ADOTANTES'], nome_seguro)
                try:
                    foto_pessoal.save(caminho)
                    foto_pessoal_filename_salvar = nome_seguro
                except Exception as e:
                    erros.append(f"Erro ao salvar foto pessoal: {e}")
                    app.logger.error(f"Erro ao salvar foto pessoal: {e}")
            else:
                erros.append('Tipo de arquivo não permitido para foto pessoal.')

        # --- Processar Foto do Local ---
        foto_local_filename_salvar = None
        if foto_local and foto_local.filename != '':
            if allowed_file(foto_local.filename):
                nome_seguro = secure_filename(f"{uuid.uuid4()}_{foto_local.filename}")
                caminho = os.path.join(app.config['UPLOAD_FOLDER_ADOTANTES'], nome_seguro)
                try:
                    foto_local.save(caminho)
                    foto_local_filename_salvar = nome_seguro
                except Exception as e:
                    erros.append(f"Erro ao salvar foto do local: {e}")
                    app.logger.error(f"Erro ao salvar foto do local: {e}")
            else:
                erros.append('Tipo de arquivo não permitido para foto do local.')

        # --- Conversão de Tipos e Validações Condicionais ---
        tempo_sozinho = None
        if tempo_sozinho_str:
            try:
                tempo_sozinho = int(tempo_sozinho_str)
                if tempo_sozinho < 0:
                     erros.append('Tempo sozinho (horas) não pode ser negativo.')
            except ValueError:
                erros.append('Tempo sozinho (horas) deve ser um número válido.')

        quantidade_animais = None
        if tem_outros_animais == 'Sim':
             if not quantidade_animais_str:
                 erros.append('Informe a quantidade de outros animais que possui.')
             else:
                 try:
                    quantidade_animais = int(quantidade_animais_str)
                    if quantidade_animais < 1:
                         erros.append('Quantidade de outros animais deve ser pelo menos 1.')
                 except ValueError:
                     erros.append('Quantidade de outros animais deve ser um número válido.')
             if quantidade_animais is not None and quantidade_animais > 0 and not tipos_animais:
                 erros.append('Informe os tipos dos outros animais que possui.')
        elif tem_outros_animais == 'Nao':
            quantidade_animais = None # Garante que seja None
            tipos_animais = None    # Garante que seja None

        quantidade_criancas = None
        if tem_criancas == 'Sim':
            if not quantidade_criancas_str:
                erros.append("Informe a quantidade de crianças.")
            else:
                try:
                    quantidade_criancas = int(quantidade_criancas_str)
                    if quantidade_criancas < 1:
                        erros.append('Quantidade de crianças deve ser pelo menos 1.')
                except ValueError:
                    erros.append('Quantidade de crianças deve ser um número válido.')
            if not idades_criancas:
                 erros.append("Informe a(s) idade(s) da(s) criança(s).")
            # restricoes_criancas é opcional
        elif tem_criancas == 'Nao':
            quantidade_criancas = None # Garante que seja None
            idades_criancas = None    # Garante que seja None
            restricoes_criancas = None # Garante que seja None

        # --- Se houver erros (de validação ou upload), re-renderizar o formulário ---
        if erros:
            # Tenta remover arquivos que podem ter sido salvos no disco ANTES de detectar o erro
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_pessoal_filename_salvar)
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_local_filename_salvar)

            # Exibe todas as mensagens de erro acumuladas para o usuário
            for erro in erros:
                 flash(erro, 'danger')

            # Re-renderiza o template, passando os dados já digitados de volta (request.form)
            # e a lista de animais_disponiveis (que foi buscada no início da função)
            return render_template('cadastrar_adotante.html',
                                   form_data=request.form,
                                   animais_disponiveis=animais_disponiveis)

        # --- Se tudo ok (sem erros), criar e salvar o objeto ---
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
            # Outros animais
            tem_outros_animais=tem_outros_animais,
            tempo_sozinho=tempo_sozinho,
            quantidade_animais=quantidade_animais,
            tipos_animais=tipos_animais,
            # Crianças
            tem_criancas=tem_criancas,
            quantidade_criancas=quantidade_criancas,
            idades_criancas=idades_criancas,
            restricoes_criancas=restricoes_criancas,
            # Fotos (nomes dos arquivos salvos ou None)
            foto_pessoal_filename=foto_pessoal_filename_salvar,
            foto_local_filename=foto_local_filename_salvar
        )

        try:
            # Adiciona o novo objeto à sessão do banco de dados
            db.session.add(novo_adotante)
            # Tenta salvar as mudanças no banco de dados
            db.session.commit()
            # Se o commit funcionou, exibe mensagem de sucesso
            flash('Adotante cadastrado com sucesso!', 'success')
            # Redireciona para o dashboard (ou outra página, como a lista se reativada)
            return redirect(url_for('dashboard'))

        except Exception as e:
            # Se o commit falhar (ex: outra constraint do DB, erro de conexão)
            db.session.rollback() # Desfaz quaisquer mudanças pendentes na sessão
            flash(f'Erro interno ao salvar o adotante no banco de dados: {e}', 'danger')
            app.logger.error(f"Erro DB Insert Adotante: {e}")

            # Tenta remover as fotos que foram salvas no disco durante esta requisição
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_pessoal_filename_salvar)
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_local_filename_salvar)

            # Re-renderiza o formulário com os dados que o usuário tentou enviar e a lista de animais
            return render_template('cadastrar_adotante.html',
                                   form_data=request.form,
                                   animais_disponiveis=animais_disponiveis)

    # --- Requisição GET ---
    # Se não for POST, simplesmente renderiza o formulário vazio (form_data=None)
    # A lista de animais_disponiveis já foi buscada no início da função
    return render_template('cadastrar_adotante.html',
                           form_data=None,
                           animais_disponiveis=animais_disponiveis)

# --- Rota para Listar Adotantes ---
@app.route('/listar_adotantes')
def listar_adotantes():
    if 'admin' not in session:
        return redirect(url_for('login'))
    try:
        # Ordena por ID decrescente para mostrar os mais recentes primeiro
        adotantes = Adotante.query.order_by(Adotante.id.desc()).all()
    except Exception as e:
        flash(f"Erro ao buscar adotantes: {e}", "danger")
        app.logger.error(f"Erro ao buscar adotantes: {e}")
        adotantes = []
    return render_template('listar_adotantes.html', adotantes=adotantes)

# --- Rota para Ver Detalhes do Adotante ---
@app.route('/adotante/<int:adotante_id>')
def detalhes_adotante(adotante_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    adotante = Adotante.query.get_or_404(adotante_id)
    return render_template('detalhes_adotante.html', adotante=adotante)

# --- Rota para Editar Adotante (GET - Mostrar formulário preenchido) ---
@app.route('/editar_adotante/<int:adotante_id>', methods=['GET'])
def editar_adotante_form(adotante_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    adotante = Adotante.query.get_or_404(adotante_id)
    
    try:
        animais_disponiveis = Animal.query.filter_by(adotado=False).order_by(Animal.nome).all()
        # Opcional: Se o animal de interesse atual do adotante JÁ FOI ADOTADO por outra pessoa,
        # você pode querer buscá-lo separadamente para ainda mostrá-lo como selecionado,
        # talvez com um aviso. Ou simplesmente mostrar apenas os disponíveis.
        # Para simplicidade, vamos mostrar apenas os disponíveis. O usuário terá que re-selecionar
        # se o animal original não estiver mais disponível.
    except Exception as e:
        flash(f"Erro ao buscar animais disponíveis: {e}", "warning")
        app.logger.error(f"Erro ao buscar animais disponíveis: {e}")
        animais_disponiveis = []

    # Passa o adotante e a lista de animais para o template
    return render_template('editar_adotante.html',
                           adotante=adotante,
                           animais_disponiveis=animais_disponiveis,
                           form_data=None) # form_data não é necessário aqui, usamos o objeto adotante

# --- Rota para Editar Adotante (POST - Processar formulário) ---
@app.route('/editar_adotante/<int:adotante_id>', methods=['POST'])
def editar_adotante_submit(adotante_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    adotante = Adotante.query.get_or_404(adotante_id)

    # --- Ler dados do formulário ---
    nome_completo = request.form.get('nome_completo')
    rg = request.form.get('rg')
    cpf = request.form.get('cpf')
    # ... (ler todos os outros campos de texto/select: endereco, bairro, etc.) ...
    # Crianças
    tem_criancas = request.form.get('tem_criancas')
    quantidade_criancas_str = request.form.get('quantidade_criancas')
    idades_criancas = request.form.get('idades_criancas')
    restricoes_criancas = request.form.get('restricoes_criancas')
    # Fotos
    foto_pessoal_nova = request.files.get('foto_pessoal')
    foto_local_nova = request.files.get('foto_local')

    erros = []
    # --- Validações ---
    if not nome_completo: erros.append("Nome completo é obrigatório.")
    if not rg: erros.append("RG é obrigatório.")
    # Validar CPF (Obrigatório e Único, mas permitir o CPF atual do próprio adotante)
    if not cpf:
        erros.append("CPF é obrigatório.")
    else:
        # Verifica se o CPF pertence a OUTRO adotante
        cpf_existente = Adotante.query.filter(Adotante.cpf == cpf, Adotante.id != adotante_id).first()
        if cpf_existente:
            erros.append(f'O CPF "{cpf}" já está cadastrado para outro adotante ({cpf_existente.nome_completo}).')
    # ... (Adicione TODAS as outras validações obrigatórias) ...
    if not tem_criancas: erros.append("Informe se há crianças na residência.")

    # --- Processar Foto Pessoal (Substituição) ---
    foto_pessoal_filename_atualizar = adotante.foto_pessoal_filename
    nova_foto_pessoal_salva = False
    if foto_pessoal_nova and foto_pessoal_nova.filename != '':
        if allowed_file(foto_pessoal_nova.filename):
            nome_seguro = secure_filename(f"{uuid.uuid4()}_{foto_pessoal_nova.filename}")
            caminho = os.path.join(app.config['UPLOAD_FOLDER_ADOTANTES'], nome_seguro)
            try:
                foto_pessoal_nova.save(caminho)
                nova_foto_pessoal_salva = True
                foto_pessoal_filename_atualizar = nome_seguro
            except Exception as e:
                erros.append(f"Erro ao salvar nova foto pessoal: {e}")
                app.logger.error(f"Erro ao salvar nova foto pessoal para adotante {adotante_id}: {e}")
        else:
            erros.append('Tipo de arquivo não permitido para foto pessoal.')

    # --- Processar Foto do Local (Substituição) ---
    foto_local_filename_atualizar = adotante.foto_local_filename
    nova_foto_local_salva = False
    if foto_local_nova and foto_local_nova.filename != '':
        if allowed_file(foto_local_nova.filename):
            nome_seguro = secure_filename(f"{uuid.uuid4()}_{foto_local_nova.filename}")
            caminho = os.path.join(app.config['UPLOAD_FOLDER_ADOTANTES'], nome_seguro)
            try:
                foto_local_nova.save(caminho)
                nova_foto_local_salva = True
                foto_local_filename_atualizar = nome_seguro
            except Exception as e:
                erros.append(f"Erro ao salvar nova foto do local: {e}")
                app.logger.error(f"Erro ao salvar nova foto do local para adotante {adotante_id}: {e}")
        else:
            erros.append('Tipo de arquivo não permitido para foto do local.')

    # --- Conversão e Validação de Tipos (Crianças e Outros) ---
    # ... (lógica de conversão para tempo_sozinho, quantidade_animais, quantidade_criancas) ...
    # ... (validações relacionadas a 'Sim'/'Nao' para outros_animais e criancas) ...
    quantidade_criancas = None
    if tem_criancas == 'Sim':
        if not quantidade_criancas_str: erros.append("Informe a quantidade de crianças.")
        else:
            try:
                quantidade_criancas = int(quantidade_criancas_str)
                if quantidade_criancas < 1: erros.append('Quantidade de crianças deve ser pelo menos 1.')
            except ValueError: erros.append('Quantidade de crianças deve ser um número válido.')
        if not idades_criancas: erros.append("Informe a(s) idade(s) da(s) criança(s).")
    elif tem_criancas == 'Nao':
        quantidade_criancas = None
        idades_criancas = None
        restricoes_criancas = None

    # --- Se houver erros, re-renderizar o formulário de edição ---
    if erros:
        # Não remove as fotos novas aqui, pois o usuário pode tentar corrigir
        for erro in erros: flash(erro, 'danger')
        # Passa o objeto adotante *original* de volta, os erros serão exibidos
        # O template usará os dados do objeto adotante para repopular
        return render_template('editar_adotante.html', adotante=adotante, form_data=None)

    # --- Se não houver erros, atualizar os dados do objeto adotante ---
    # Tenta remover as fotos antigas ANTES de atualizar os nomes no objeto
    if nova_foto_pessoal_salva:
        remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], adotante.foto_pessoal_filename)
    if nova_foto_local_salva:
         remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], adotante.foto_local_filename)

    # Atualiza os atributos do objeto
    adotante.nome_completo = nome_completo
    adotante.rg = rg
    adotante.cpf = cpf
    # ... (atualizar TODOS os outros campos lidos do formulário) ...
    adotante.tem_criancas = tem_criancas
    adotante.idades_criancas = idades_criancas
    adotante.restricoes_criancas = restricoes_criancas
    adotante.foto_pessoal_filename = foto_pessoal_filename_atualizar
    adotante.foto_local_filename = foto_local_filename_atualizar

    # Lógica para campos condicionais (outros animais e crianças)
    if adotante.tem_outros_animais == 'Sim':
        adotante.quantidade_animais = quantidade_animais # Assumindo que 'quantidade_animais' foi convertido
        adotante.tipos_animais = request.form.get('tipos_animais') # Lê novamente ou usa variável
    else:
        adotante.quantidade_animais = None
        adotante.tipos_animais = None

    if adotante.tem_criancas == 'Sim':
         adotante.quantidade_criancas = quantidade_criancas # Usa valor convertido
    else:
         adotante.quantidade_criancas = None
         # idades_criancas e restricoes já foram atualizados acima

    # --- Tenta salvar as alterações no banco de dados ---
    try:
        db.session.commit()
        flash(f'Dados de "{adotante.nome_completo}" atualizados com sucesso!', 'success')
        return redirect(url_for('listar_adotantes'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar dados do adotante no banco de dados: {e}', 'danger')
        app.logger.error(f"Erro DB Update Adotante {adotante.id}: {e}")
        # Tenta remover as *novas* fotos que podem ter sido salvas se o commit falhar
        if nova_foto_pessoal_salva:
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_pessoal_filename_atualizar)
        if nova_foto_local_salva:
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_local_filename_atualizar)
        # Re-renderiza com o objeto *antes* do rollback ter desfeito as mudanças na sessão
        return render_template('editar_adotante.html', adotante=adotante, form_data=None)


# --- Rota para Excluir Adotante ---
@app.route('/excluir_adotante/<int:adotante_id>', methods=['POST'])
def excluir_adotante(adotante_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    adotante = Adotante.query.get_or_404(adotante_id)
    foto_pessoal_del = adotante.foto_pessoal_filename
    foto_local_del = adotante.foto_local_filename
    nome_adotante = adotante.nome_completo

    try:
        db.session.delete(adotante)
        db.session.commit()
        # Tenta remover os arquivos associados APÓS o commit
        removido_pessoal = remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_pessoal_del)
        removido_local = remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_local_del)
        msg = f'Adotante "{nome_adotante}" excluído com sucesso!'
        cat = 'success'
        if (foto_pessoal_del and not removido_pessoal) or (foto_local_del and not removido_local):
             msg += " (Aviso: erro ao remover um ou mais arquivos de foto associados)."
             cat = 'warning'
        flash(msg, cat)
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir o adotante: {e}', 'danger')
        app.logger.error(f"Erro DB Delete Adotante {adotante.id}: {e}")

    return redirect(url_for('listar_adotantes'))

if __name__ == '__main__':
    with app.app_context():
        # db.init_app(app)  # REMOVA ESTA LINHA
        db.create_all()  # Crie as tabelas *dentro* do contexto da aplicação
        criar_admin()  # Garante que o admin existe no banco
    app.run(debug=True)