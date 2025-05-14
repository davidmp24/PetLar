from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
from werkzeug.utils import secure_filename
import os
from flask import flash # Certifique-se que flash está importado
from sqlalchemy import func 
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_chave_dev_muito_segura_padrao')
if os.environ.get('DATABASE_URL'):
    # Para o Render, a URL já vem no formato correto para SQLAlchemy >= 1.4
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petlar.db' # Local
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
    data_cadastro = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
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
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    adotante_id = db.Column(db.Integer, db.ForeignKey('adotante.id'), nullable=True)
    adotante = db.relationship('Adotante', backref=db.backref('animais_adotados', lazy=True))

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
    data_cadastro = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    
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

# --- Rotas de Gerenciamento de Administradores ---

# Rota para Listar Admins
@app.route('/listar_admins')
def listar_admins():
    if 'admin' not in session:
        return redirect(url_for('login'))
    # Busca todos os admins, talvez ordenados por username
    try:
        admins = Admin.query.order_by(Admin.username).all()
    except Exception as e:
        flash(f"Erro ao buscar administradores: {e}", "danger")
        admins = []
    # Passa o nome do admin logado para o template, para evitar auto-exclusão/edição
    admin_logado = session.get('admin')
    return render_template('listar_admins.html', admins=admins, admin_logado=admin_logado)

# Rota para Registrar Novo Admin (GET e POST)
@app.route('/registrar_admin', methods=['GET', 'POST'])
def registrar_admin():
    if 'admin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        erros = []
        # Validações
        if not username:
            erros.append('Nome de usuário é obrigatório.')
        else:
            # Verifica se username já existe
            user_existente = Admin.query.filter_by(username=username).first()
            if user_existente:
                erros.append(f'O nome de usuário "{username}" já está em uso.')
        if not password:
            erros.append('Senha é obrigatória.')
        if password != confirm_password:
            erros.append('As senhas não coincidem.')

        if erros:
            for erro in erros: flash(erro, 'danger')
            # Passa o username digitado de volta para repopular
            return render_template('registrar_admin.html', username=username)

        # Se passou nas validações
        try:
            hashed_password = generate_password_hash(password)
            novo_admin = Admin(username=username, password=hashed_password)
            db.session.add(novo_admin)
            db.session.commit()
            flash(f'Administrador "{username}" registrado com sucesso!', 'success')
            return redirect(url_for('listar_admins'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar administrador: {e}', 'danger')
            app.logger.error(f"Erro DB Insert Admin: {e}")
            return render_template('registrar_admin.html', username=username)

    # Método GET
    return render_template('registrar_admin.html')

# Rota para Editar Admin (GET - Mostrar formulário)
@app.route('/editar_admin/<int:admin_id>', methods=['GET'])
def editar_admin_form(admin_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    admin_a_editar = Admin.query.get_or_404(admin_id)
    # Passa o objeto admin para o template
    return render_template('editar_admin.html', admin=admin_a_editar)

# Rota para Editar Admin (POST - Processar formulário, focado em senha)
@app.route('/editar_admin/<int:admin_id>', methods=['POST'])
def editar_admin_submit(admin_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    admin_a_editar = Admin.query.get_or_404(admin_id)
    # Não permitir editar o próprio nome de usuário facilmente via este form
    # Foco na atualização de senha

    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    erros = []
    # Só valida e atualiza se o usuário preencheu os campos de senha
    if new_password or confirm_password:
        if not new_password:
            erros.append('Nova senha é obrigatória para alterar.')
        if new_password != confirm_password:
            erros.append('As novas senhas não coincidem.')

        if not erros:
            try:
                # Atualiza a senha hashada
                admin_a_editar.password = generate_password_hash(new_password)
                db.session.commit()
                flash(f'Senha do administrador "{admin_a_editar.username}" atualizada com sucesso!', 'success')
                return redirect(url_for('listar_admins'))
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao atualizar a senha: {e}', 'danger')
                app.logger.error(f"Erro DB Update Admin Password: {e}")
                # Re-renderiza o form de edição em caso de erro no DB
                return render_template('editar_admin.html', admin=admin_a_editar)
        else:
            # Se houver erros de validação de senha
            for erro in erros: flash(erro, 'danger')
            return render_template('editar_admin.html', admin=admin_a_editar)
    else:
        # Se nenhum campo de senha foi preenchido, apenas volta para a lista
        flash('Nenhuma alteração de senha foi fornecida.', 'info')
        return redirect(url_for('listar_admins'))


# Rota para Excluir Admin (Opcional, mas útil)
@app.route('/excluir_admin/<int:admin_id>', methods=['POST'])
def excluir_admin(admin_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    admin_a_excluir = Admin.query.get_or_404(admin_id)
    admin_logado = session.get('admin')

    # IMPEDE AUTO-EXCLUSÃO
    if admin_a_excluir.username == admin_logado:
        flash('Você não pode excluir sua própria conta de administrador.', 'danger')
        return redirect(url_for('listar_admins'))

    # (Opcional) Impedir exclusão do último admin
    if Admin.query.count() <= 1:
         flash('Não é possível excluir o último administrador.', 'danger')
         return redirect(url_for('listar_admins'))

    try:
        nome_excluido = admin_a_excluir.username
        db.session.delete(admin_a_excluir)
        db.session.commit()
        flash(f'Administrador "{nome_excluido}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir administrador: {e}', 'danger')
        app.logger.error(f"Erro DB Delete Admin: {e}")

    return redirect(url_for('listar_admins'))

@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))

    try:
        # --- Consultas para Estatísticas ---
        total_animais = db.session.query(func.count(Animal.id)).scalar()
        animais_disponiveis = db.session.query(func.count(Animal.id)).filter(Animal.adotado == False).scalar()
        animais_adotados = db.session.query(func.count(Animal.id)).filter(Animal.adotado == True).scalar()
        total_adotantes = db.session.query(func.count(Adotante.id)).scalar()

        # --- Consultas para Listas Recentes (Exemplo: Últimos 5 animais) ---
        ultimos_animais = Animal.query.order_by(Animal.data_cadastro.desc()).limit(5).all()
        # (Adicionar consulta para últimos adotantes se desejar)

        # --- Consultas para Gráficos (Exemplo) ---
        # Dados para gráfico de Status (Disponível/Adotado)
        stats_status = {
            'Disponível': animais_disponiveis,
            'Adotado': animais_adotados
        }
        # Dados para gráfico por Espécie
        stats_especie = db.session.query(Animal.especie, func.count(Animal.especie)).group_by(Animal.especie).order_by(func.count(Animal.especie).desc()).all()
        # Formatar para o gráfico (ex: [['Cachorro', 15], ['Gato', 10]])
        dados_grafico_especie = [[especie, count] for especie, count in stats_especie]


    except Exception as e:
        flash(f"Erro ao carregar dados do dashboard: {e}", "danger")
        app.logger.error(f"Erro Dashboard Query: {e}")
        # Definir valores padrão em caso de erro
        total_animais = 0
        animais_disponiveis = 0
        animais_adotados = 0
        total_adotantes = 0
        ultimos_animais = []
        stats_status = {}
        dados_grafico_especie = []


    # Passa todos os dados para o template
    return render_template('dashboard.html', # <- MUDAR AQUI
                           page="dashboard",
                           total_animais=total_animais,
                           animais_disponiveis=animais_disponiveis,
                           animais_adotados=animais_adotados,
                           total_adotantes=total_adotantes,
                           ultimos_animais=ultimos_animais,
                           stats_status=stats_status,
                           dados_grafico_especie=dados_grafico_especie
                           )

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

    if request.method == 'POST':
        # --- Ler dados do formulário ---
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
        localizacao_texto = request.form.get('localizacao') # Renomeado para clareza
        descricao = request.form.get('descricao')
        foto = request.files.get('foto')
        latitude_str = request.form.get('latitude')
        longitude_str = request.form.get('longitude')

        # Inicializa lista de erros
        erros = []

        # --- Validações de Campos Obrigatórios ---
        if not nome: erros.append('O nome do animal é obrigatório.')
        if not especie: erros.append('A espécie do animal é obrigatória.')
        # Adicione outras validações obrigatórias (sexo, tamanho?)

        # --- Conversão e Validação de Idade ---
        idade = None
        if idade_str: # Só converte se algo foi digitado
            try:
                idade = int(idade_str)
                if idade < 0:
                    erros.append('A idade não pode ser negativa.')
            except ValueError:
                erros.append('A idade deve ser um número válido.')

        # --- Conversão e Validação de Coordenadas ---
        latitude = None
        longitude = None
        if latitude_str or longitude_str: # Processa se pelo menos um foi enviado
            if not latitude_str or not longitude_str:
                 erros.append("Latitude e Longitude devem ser fornecidas juntas.")
            else:
                try:
                    latitude = float(latitude_str)
                    longitude = float(longitude_str)
                    if not (-90 <= latitude <= 90): erros.append("Latitude inválida (deve ser entre -90 e 90).")
                    if not (-180 <= longitude <= 180): erros.append("Longitude inválida (deve ser entre -180 e 180).")
                except (ValueError, TypeError):
                     erros.append("Latitude e Longitude devem ser números válidos.")

        # --- Tratamento da Foto ---
        foto_filename_salvar = None # Inicializa como None
        if foto and foto.filename != '':
            if allowed_file(foto.filename):
                nome_seguro = secure_filename(f"{uuid.uuid4()}_{foto.filename}")
                # Certifique-se de usar a pasta correta para ANIMAIS
                caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro) # UPLOAD_FOLDER para animais
                try:
                    foto.save(caminho)
                    foto_filename_salvar = nome_seguro # Guarda nome apenas se salvou
                except Exception as e:
                    erros.append(f"Erro ao salvar a foto: {e}")
                    app.logger.error(f"Erro ao salvar foto do animal: {e}")
            else:
                erros.append('Tipo de arquivo de foto não permitido.')

        # --- Se houver erros (validação, conversão ou upload), re-renderizar ---
        if erros:
            # Tenta remover o arquivo de foto que pode ter sido salvo antes do erro
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER'], foto_filename_salvar)

            for erro in erros:
                flash(erro, 'danger')

            # Re-renderiza passando os dados do formulário de volta
            # CORREÇÃO: Usando keyword arguments corretamente
            return render_template('cadastrar_animal.html', form_data=request.form)

        # --- Se tudo ok, criar e salvar o objeto ---
        # Removida lógica 'is_creating' / 'else' que era da edição
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
            localizacao=localizacao_texto, # Usando a variável renomeada
            descricao=descricao,
            foto_filename=foto_filename_salvar, # Nome do arquivo salvo ou None
            latitude=latitude,                  # Coordenada salva ou None
            longitude=longitude                 # Coordenada salva ou None
            # 'adotado' e 'data_cadastro' terão valores padrão definidos no modelo
        )

        try:
            db.session.add(novo_animal)
            db.session.commit()
            flash(f'Animal "{novo_animal.nome}" cadastrado com sucesso!', 'success')
            # Redireciona para a lista de animais após sucesso
            return redirect(url_for('listar_animais'))

        except Exception as e:
            db.session.rollback() # Desfaz a tentativa de commit
            flash(f'Erro ao salvar o animal no banco de dados: {e}', 'danger')
            app.logger.error(f"Erro DB Insert Animal: {e}")

            # Tenta remover a foto salva se o commit falhar
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER'], foto_filename_salvar)

            # Re-renderiza com os dados do formulário
            # CORREÇÃO: Usando keyword arguments corretamente
            return render_template('cadastrar_animal.html', form_data=request.form)

    # --- Requisição GET ---
    # Renderiza o formulário vazio
    # CORREÇÃO: Passando form_data=None explicitamente
    return render_template('cadastrar_animal.html', form_data=None)

# Em app.py

@app.route('/listar_animais', methods=['GET'])
def listar_animais():
    if 'admin' not in session:
        return redirect(url_for('login'))

    query = Animal.query

    # Ler parâmetros de filtro da URL
    filtro_nome = request.args.get('filtro_nome', '').strip()
    filtro_especie = request.args.get('filtro_especie', '').strip()
    filtro_data_inicio_str = request.args.get('filtro_data_inicio', '').strip()
    filtro_data_fim_str = request.args.get('filtro_data_fim', '').strip()

    # Aplicar filtros à query
    if filtro_nome:
        query = query.filter(Animal.nome.ilike(f'%{filtro_nome}%'))
    if filtro_especie:
        query = query.filter(Animal.especie.ilike(f'%{filtro_especie}%'))

    # Aplicar filtro de data de início
    if filtro_data_inicio_str:
        try:
            # Converte a string de data para objeto datetime
            data_inicio = datetime.strptime(filtro_data_inicio_str, '%Y-%m-%d').date()
            # Filtra registros onde data_cadastro é maior ou igual à data_inicio
            # Precisamos usar func.date() se a coluna for DateTime e quisermos comparar só a data
            query = query.filter(db.func.date(Animal.data_cadastro) >= data_inicio)
        except ValueError:
            flash("Formato de Data de Início inválido. Use AAAA-MM-DD.", "warning")
            # Pode optar por não aplicar o filtro ou retornar erro

    # Aplicar filtro de data de fim
    if filtro_data_fim_str:
        try:
            data_fim = datetime.strptime(filtro_data_fim_str, '%Y-%m-%d').date()
            # Filtra registros onde data_cadastro é menor ou igual à data_fim
            query = query.filter(db.func.date(Animal.data_cadastro) <= data_fim)
        except ValueError:
            flash("Formato de Data de Fim inválido. Use AAAA-MM-DD.", "warning")

    # Ordena e executa a query
    try:
        animais = query.order_by(Animal.data_cadastro.desc(), Animal.nome).all() # Ordena por data (mais novo primeiro) e nome
    except Exception as e:
        flash(f"Erro ao buscar animais: {e}", "danger")
        app.logger.error(f"Erro Listar Animais Query: {e}")
        animais = []

    return render_template('listar_animais.html', animais=animais)

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
# Em app.py

@app.route('/marcar_disponivel/<int:animal_id>', methods=['POST'])
def marcar_disponivel(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    animal = Animal.query.get_or_404(animal_id)

    if not animal.adotado:
        flash(f'O animal "{animal.nome}" já está marcado como disponível.', 'info')
        return redirect(url_for('listar_animais'))

    try:
        animal.adotado = False # Define status como NÃO adotado
        animal.adotante_id = None # REMOVE o vínculo com o adotante!
        # Se tiver data da adoção, limpar também: animal.data_adocao = None
        db.session.commit()
        flash(f'Animal "{animal.nome}" marcado como disponível novamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao marcar o animal como disponível: {e}', 'danger')
        app.logger.error(f"Erro DB Mark Available: {e}")

    return redirect(url_for('listar_animais'))

# --- Rota para Cadastrar Adotante (GET e POST) ---
import os
import uuid # Necessário para nomes de arquivo únicos
from werkzeug.utils import secure_filename # Necessário para nomes de arquivo seguros
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash
)
# Certifique-se de que seus modelos (Adotante, Animal) e o objeto db estão importados
# from .models import db, Adotante, Animal # Exemplo se estiver usando blueprints/models.py
# Ou se estiver tudo em app.py:
# from app import db, Adotante, Animal

# Certifique-se de que as configurações e funções auxiliares estão definidas:
# app.config['UPLOAD_FOLDER_ADOTANTES'] = ...
# def allowed_file(filename): ...
# def remover_arquivo_se_existe(diretorio, nome_arquivo): ... # Lembre-se que atualizamos esta função

# --- Rota para Cadastrar Adotante (GET e POST) ---
@app.route('/cadastrar_adotante', methods=['GET', 'POST'])
def cadastrar_adotante():
    # Verifica se o administrador está logado
    if 'admin' not in session:
        return redirect(url_for('login'))

    # Busca animais disponíveis ANTES de verificar o método da requisição
    # Isso garante que a lista esteja disponível para GET e para re-renderização em POST com erros
    # (Removido pois a lista de animais não está sendo usada ativamente neste formulário simplificado)
    # try:
    #     animais_disponiveis_para_interesse = Animal.query.filter_by(adotado=False).order_by(Animal.nome).all()
    # except Exception as e:
    #     flash(f"Erro ao buscar animais disponíveis: {e}", "warning")
    #     app.logger.error(f"Erro ao buscar animais disponíveis: {e}")
    #     animais_disponiveis_para_interesse = []

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
        animal_interesse = request.form.get('animal_interesse') # Nome do animal, pode ser um campo de texto
        tipo_animal_interesse = request.form.get('tipo_animal_interesse') # Cão, Gato, etc.
        justificativa_adocao = request.form.get('justificativa_adocao')
        tem_outros_animais = request.form.get('tem_outros_animais') # 'Sim' ou 'Nao'
        tempo_sozinho_str = request.form.get('tempo_sozinho')
        quantidade_animais_str = request.form.get('quantidade_animais')
        tipos_animais = request.form.get('tipos_animais')
        # Removendo campos de crianças por enquanto, já que não estão no modelo Adotante
        # tem_criancas = request.form.get('tem_criancas')
        # quantidade_criancas_str = request.form.get('quantidade_criancas')
        # idades_criancas = request.form.get('idades_criancas')
        # restricoes_criancas = request.form.get('restricoes_criancas')
        foto_pessoal = request.files.get('foto_pessoal')
        foto_local = request.files.get('foto_local')

        # Inicializa a lista de erros
        erros = []

        # --- Validações (campos obrigatórios, formato, unicidade, etc.) ---
        if not nome_completo: erros.append("Nome completo é obrigatório.")
        if not rg:
            erros.append("RG é obrigatório.")
        else:
            rg_existente = Adotante.query.filter_by(rg=rg).first()
            if rg_existente:
                erros.append(f'O RG "{rg}" já está cadastrado para o adotante "{rg_existente.nome_completo}".')
        if not cpf:
            erros.append("CPF é obrigatório.")
        else:
            cpf_existente = Adotante.query.filter_by(cpf=cpf).first()
            if cpf_existente:
                erros.append(f'O CPF "{cpf}" já está cadastrado para o adotante "{cpf_existente.nome_completo}".')
        if not endereco: erros.append("Endereço é obrigatório.")
        if not bairro: erros.append("Bairro é obrigatório.")
        if not cidade: erros.append("Cidade é obrigatória.")
        if not cep: erros.append("CEP é obrigatório.")
        if not telefone: erros.append("Telefone é obrigatório.")
        if not email: erros.append("Email é obrigatório.") # Adicionar validação de formato de email
        if not animal_interesse: erros.append("Nome do animal de interesse é obrigatório.")
        if not tipo_animal_interesse: erros.append("Tipo de animal de interesse é obrigatório.")
        if not justificativa_adocao: erros.append("Justificativa da adoção é obrigatória.")
        if not tem_outros_animais: erros.append("Informe se possui outros animais na residência.")
        # Validação de tempo_sozinho se fornecido
        if tempo_sozinho_str and not tempo_sozinho_str.isdigit():
             erros.append("Tempo sozinho deve ser um número de horas.")


        # --- Processar Foto Pessoal ---
        foto_pessoal_filename_salvar = None # Inicializa como None
        if foto_pessoal and foto_pessoal.filename != '':
            if allowed_file(foto_pessoal.filename):
                nome_seguro = secure_filename(f"{uuid.uuid4()}_{foto_pessoal.filename}")
                caminho = os.path.join(app.config['UPLOAD_FOLDER_ADOTANTES'], nome_seguro)
                try:
                    foto_pessoal.save(caminho)
                    foto_pessoal_filename_salvar = nome_seguro # Guarda nome se salvou
                except Exception as e:
                    erros.append(f"Erro ao salvar foto pessoal: {e}")
                    app.logger.error(f"Erro ao salvar foto pessoal: {e}")
            else:
                erros.append(f"Tipo de arquivo não permitido para foto pessoal: {foto_pessoal.filename.rsplit('.',1)[-1] if '.' in foto_pessoal.filename else 'desconhecido'}")

        # --- Processar Foto do Local ---
        foto_local_filename_salvar = None # Inicializa como None
        if foto_local and foto_local.filename != '':
            if allowed_file(foto_local.filename):
                nome_seguro = secure_filename(f"{uuid.uuid4()}_{foto_local.filename}")
                caminho = os.path.join(app.config['UPLOAD_FOLDER_ADOTANTES'], nome_seguro)
                try:
                    foto_local.save(caminho)
                    foto_local_filename_salvar = nome_seguro # Guarda nome se salvou
                except Exception as e:
                    erros.append(f"Erro ao salvar foto do local: {e}")
                    app.logger.error(f"Erro ao salvar foto do local: {e}")
            else:
                erros.append(f"Tipo de arquivo não permitido para foto do local: {foto_local.filename.rsplit('.',1)[-1] if '.' in foto_local.filename else 'desconhecido'}")

        # --- Conversão de Tipos e Validações Condicionais ---
        tempo_sozinho = None
        if tempo_sozinho_str:
            try:
                tempo_sozinho = int(tempo_sozinho_str)
                if tempo_sozinho < 0:
                     erros.append('Tempo sozinho (horas) não pode ser negativo.')
            except ValueError:
                # Erro já adicionado na validação inicial se não for digit
                if "Tempo sozinho deve ser um número de horas." not in erros and "Tempo sozinho deve ser um número válido." not in erros :
                    erros.append('Tempo sozinho (horas) deve ser um número válido.')


        quantidade_animais_convertida = None # Renomeada para evitar confusão
        tipos_animais_para_salvar = tipos_animais # Usa valor do form

        if tem_outros_animais == 'Sim':
             if not quantidade_animais_str:
                 erros.append('Informe a quantidade de outros animais que possui.')
             else:
                 try:
                    quantidade_animais_convertida = int(quantidade_animais_str)
                    if quantidade_animais_convertida < 1:
                         erros.append('Quantidade de outros animais deve ser pelo menos 1.')
                 except ValueError:
                     erros.append('Quantidade de outros animais deve ser um número válido.')

             if quantidade_animais_convertida is not None and quantidade_animais_convertida > 0 and not tipos_animais_para_salvar:
                 erros.append('Informe os tipos dos outros animais que possui.')

        elif tem_outros_animais == 'Nao':
            quantidade_animais_convertida = None
            tipos_animais_para_salvar = None
        # else: erro já tratado em 'if not tem_outros_animais'


        # --- Se houver erros (de validação ou upload), re-renderizar o formulário ---
        if erros:
            # Tenta remover arquivos que podem ter sido salvos no disco ANTES de detectar o erro
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_pessoal_filename_salvar)
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_local_filename_salvar)

            for erro in erros:
                 flash(erro, 'danger')

            return render_template('cadastrar_adotante.html',
                                   form_data=request.form)
                                   # animais_disponiveis=animais_disponiveis_para_interesse) # Removido se não usado no form

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
            tem_outros_animais=tem_outros_animais,
            tempo_sozinho=tempo_sozinho,
            quantidade_animais=quantidade_animais_convertida, # Usa variável convertida
            tipos_animais=tipos_animais_para_salvar,         # Usa variável tratada
            # Removendo campos de crianças por enquanto
            # tem_criancas=tem_criancas,
            # quantidade_criancas=quantidade_criancas,
            # idades_criancas=idades_criancas,
            # restricoes_criancas=restricoes_criancas,
            foto_pessoal_filename=foto_pessoal_filename_salvar,
            foto_local_filename=foto_local_filename_salvar
        )

        try:
            db.session.add(novo_adotante)
            db.session.commit()
            flash('Adotante cadastrado com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            # Tratar erros de integridade do DB (como UNIQUE constraint) de forma mais específica se necessário
            if "UNIQUE constraint failed" in str(e):
                if "adotante.cpf" in str(e):
                    flash(f"Erro: O CPF '{cpf}' já está cadastrado. Por favor, verifique os dados.", 'danger')
                elif "adotante.rg" in str(e):
                    flash(f"Erro: O RG '{rg}' já está cadastrado. Por favor, verifique os dados.", 'danger')
                else:
                    flash(f'Erro de integridade ao salvar no banco de dados: {e}', 'danger')
            else:
                flash(f'Erro interno ao salvar o adotante no banco de dados: {e}', 'danger')

            app.logger.error(f"Erro DB Insert Adotante: {e} - Dados: {request.form}")

            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_pessoal_filename_salvar)
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_local_filename_salvar)

            return render_template('cadastrar_adotante.html',
                                   form_data=request.form)
                                   # animais_disponiveis=animais_disponiveis_para_interesse)

    # --- Requisição GET ---
    return render_template('cadastrar_adotante.html',
                           form_data=None)
                           # animais_disponiveis=animais_disponiveis_para_interesse)

@app.route('/listar_adotantes', methods=['GET']) # Adicionar GET explicitamente
def listar_adotantes():
    if 'admin' not in session:
        return redirect(url_for('login'))

    # Inicia a query base para Adotante
    query = Adotante.query

    # --- LER PARÂMETROS DE FILTRO DA URL ---
    filtro_nome_adotante = request.args.get('filtro_nome_adotante', '').strip()
    filtro_cpf_adotante = request.args.get('filtro_cpf_adotante', '').strip()
    filtro_data_inicio_adotante_str = request.args.get('filtro_data_inicio_adotante', '').strip()
    filtro_data_fim_adotante_str = request.args.get('filtro_data_fim_adotante', '').strip()

    # --- APLICAR FILTROS À QUERY (SE FORNECIDOS) ---
    if filtro_nome_adotante:
        query = query.filter(Adotante.nome_completo.ilike(f'%{filtro_nome_adotante}%'))
    if filtro_cpf_adotante:
        # Para CPF, uma busca exata ou 'startswith' pode ser melhor que 'contains'
        query = query.filter(Adotante.cpf.like(f'{filtro_cpf_adotante}%')) # Começa com...
        # Ou exato: query = query.filter(Adotante.cpf == filtro_cpf_adotante)

    # Aplicar filtro de data de início
    if filtro_data_inicio_adotante_str:
        try:
            data_inicio = datetime.strptime(filtro_data_inicio_adotante_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Adotante.data_cadastro) >= data_inicio)
        except ValueError:
            flash("Formato de Data de Início (Adotante) inválido. Use AAAA-MM-DD.", "warning")

    # Aplicar filtro de data de fim
    if filtro_data_fim_adotante_str:
        try:
            data_fim = datetime.strptime(filtro_data_fim_adotante_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Adotante.data_cadastro) <= data_fim)
        except ValueError:
            flash("Formato de Data de Fim (Adotante) inválido. Use AAAA-MM-DD.", "warning")

    # Ordena e executa a query
    try:
        adotantes = query.order_by(Adotante.data_cadastro.desc(), Adotante.nome_completo).all()
    except Exception as e:
        flash(f"Erro ao buscar adotantes: {e}", "danger")
        app.logger.error(f"Erro Listar Adotantes Query: {e}")
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

@app.route('/registrar_adocao/<int:animal_id>', methods=['GET'])
def registrar_adocao_form(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    animal = Animal.query.get_or_404(animal_id)
    # Verifica se o animal já está adotado, não deveria chegar aqui se estiver
    if animal.adotado:
        flash(f'O animal "{animal.nome}" já está marcado como adotado.', 'warning')
        return redirect(url_for('listar_animais'))

    # Busca todos os adotantes para popular o dropdown
    try:
        adotantes_disponiveis = Adotante.query.order_by(Adotante.nome_completo).all()
    except Exception as e:
        flash(f"Erro ao buscar adotantes: {e}", "danger")
        return redirect(url_for('listar_animais'))

    return render_template('registrar_adocao.html', animal=animal, adotantes=adotantes_disponiveis)

@app.route('/registrar_adocao/<int:animal_id>', methods=['POST'])
def registrar_adocao_submit(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    animal = Animal.query.get_or_404(animal_id)
    # Pega o ID do adotante selecionado no formulário
    adotante_id_selecionado = request.form.get('adotante_selecionado_id')

    # Validação básica
    if not adotante_id_selecionado:
        flash('Você precisa selecionar um adotante.', 'danger')
        # É preciso buscar os adotantes novamente para re-renderizar o form
        adotantes_disponiveis = Adotante.query.order_by(Adotante.nome_completo).all()
        return render_template('registrar_adocao.html', animal=animal, adotantes=adotantes_disponiveis)

    adotante_selecionado = Adotante.query.get(adotante_id_selecionado)
    if not adotante_selecionado:
        flash('Adotante selecionado inválido ou não encontrado.', 'danger')
        adotantes_disponiveis = Adotante.query.order_by(Adotante.nome_completo).all()
        return render_template('registrar_adocao.html', animal=animal, adotantes=adotantes_disponiveis)

    # Verifica se o animal já está adotado (dupla checagem)
    if animal.adotado:
        flash(f'O animal "{animal.nome}" já foi adotado (possivelmente por outra pessoa enquanto você preenchia).', 'warning')
        return redirect(url_for('listar_animais'))

    try:
        # --- ATUALIZA O ANIMAL ---
        animal.adotado = True             # Marca como adotado
        animal.adotante_id = adotante_id_selecionado # Vincula o ID do adotante!
        # Se adicionou data da adoção no form, salve aqui:
        # data_adocao_str = request.form.get('data_adocao')
        # if data_adocao_str: animal.data_adocao = datetime.strptime(data_adocao_str, '%Y-%m-%d').date()

        db.session.commit()
        flash(f'Adoção do animal "{animal.nome}" por "{adotante_selecionado.nome_completo}" registrada com sucesso!', 'success')
        return redirect(url_for('listar_animais'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar a adoção: {e}', 'danger')
        app.logger.error(f"Erro DB Register Adoption: {e}")
        adotantes_disponiveis = Adotante.query.order_by(Adotante.nome_completo).all()
        return render_template('registrar_adocao.html', animal=animal, adotantes=adotantes_disponiveis)

if __name__ == '__main__':
    with app.app_context():
        # db.init_app(app)  # REMOVA ESTA LINHA
        db.create_all()  # Crie as tabelas *dentro* do contexto da aplicação
        criar_admin()  # Garante que o admin existe no banco
    app.run(debug=True)