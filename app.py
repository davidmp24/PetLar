from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os
from werkzeug.utils import secure_filename
import os
from flask import flash 
from sqlalchemy import func 
from datetime import datetime
import logging
from flask import Flask, make_response
from flask_migrate import Migrate 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'uma_chave_dev_muito_segura_padrao')
if os.environ.get('DATABASE_URL'):
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)

else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petlar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  

migrate = Migrate(app, db)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(100), nullable=False)
    raca = db.Column(db.String(100), nullable=True) 
    sexo = db.Column(db.String(10), nullable=True) 
    idade = db.Column(db.Integer, nullable=True) 
    data_cadastro = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    temperamento = db.Column(db.String(200), nullable=True)
    comportamento_outros = db.Column(db.String(200), nullable=True) 
    comportamento_criancas = db.Column(db.String(200), nullable=True) 
    doencas_preexistentes = db.Column(db.Text, nullable=True)
    tratamentos = db.Column(db.Text, nullable=True)
    cor = db.Column(db.String(50), nullable=True)
    tamanho = db.Column(db.String(50), nullable=True) 
    localizacao = db.Column(db.String(255), nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    foto_filename = db.Column(db.String(255), nullable=True) 
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    localizacao = db.Column(db.String(255), nullable=True)
    adotante_id = db.Column(db.Integer, db.ForeignKey('adotante.id'), nullable=True)
    adotante = db.relationship('Adotante', backref=db.backref('animais_adotados', lazy=True))
    adotado = db.Column(db.Boolean, default=False)
    data_cadastro = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Animal {self.id}: {self.nome} ({self.especie})>'

   
    @property
    def foto_url(self):
        if self.foto_filename:
            
            return url_for('static', filename=f'uploads/animais/{self.foto_filename}', _external=True)
        else:
           
            return url_for('static', filename='images/placeholder_animal.png', _external=True) 
        
    def to_dict(self, include_adotante_info=False):
        animal_data = {
            'id': self.id,
            'nome': self.nome,
            'especie': self.especie,
            'raca': self.raca,
            'sexo': self.sexo,
            'idade': self.idade,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None, 
            'temperamento': self.temperamento,
            'comportamento_outros': self.comportamento_outros,
            'comportamento_criancas': self.comportamento_criancas,
            'doencas_preexistentes': self.doencas_preexistentes,
            'tratamentos': self.tratamentos,
            'cor': self.cor,
            'tamanho': self.tamanho,
            'localizacao_texto': self.localizacao,
            'descricao': self.descricao,
            'foto_url': self.foto_url, 
            'latitude': self.latitude,
            'longitude': self.longitude,
            'adotado': self.adotado
        }
        if self.adotado and self.adotante_id and include_adotante_info and self.adotante:
            animal_data['adotante'] = {
                'id': self.adotante.id,
                'nome_completo': self.adotante.nome_completo
                
            }
        return animal_data 

# --- Configuração de Upload ---
UPLOAD_FOLDER_BASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads')

UPLOAD_FOLDER_ADOTANTES = os.path.join(UPLOAD_FOLDER_BASE, 'adotantes')

app.config['UPLOAD_FOLDER_ADOTANTES'] = UPLOAD_FOLDER_ADOTANTES

os.makedirs(app.config['UPLOAD_FOLDER_ADOTANTES'], exist_ok=True)


UPLOAD_FOLDER_ANIMAIS = os.path.join(UPLOAD_FOLDER_BASE, 'animais')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_ANIMAIS 
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
    justificativa_adocao = db.Column(db.Text)
    tem_outros_animais = db.Column(db.String(3), nullable=False)
    tempo_sozinho = db.Column(db.Integer)
    quantidade_animais = db.Column(db.Integer)
    tipos_animais = db.Column(db.String(200))
    foto_pessoal_filename = db.Column(db.String(255), nullable=True)
    foto_local_filename = db.Column(db.String(255), nullable=True)
    tem_criancas = db.Column(db.String(3), nullable=True) 
    quantidade_criancas = db.Column(db.Integer, nullable=True) 
    idades_criancas = db.Column(db.Text, nullable=True) 
    restricoes_criancas = db.Column(db.Text, nullable=True) 
    data_cadastro = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
    localizacao_mapa_texto = db.Column(db.Text, nullable=True) 
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    

@property
def foto_pessoal_url(self):
    if self.foto_pessoal_filename:
        return url_for('static', filename=f'uploads/adotantes/{self.foto_pessoal_filename}', _external=True)
    return url_for('static', filename='images/placeholder_adotante.png', _external=True) 

@property
def foto_local_url(self):
    if self.foto_local_filename:
        return url_for('static', filename=f'uploads/adotantes/{self.foto_local_filename}', _external=True)
    return url_for('static', filename='images/placeholder_local.png', _external=True)   

def to_dict_public(self): 
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'foto_pessoal_url': self.foto_pessoal_url if hasattr(self, 'foto_pessoal_url') else None
        }

def to_dict_full(self):
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'rg': self.rg,
            'cpf': self.cpf,
            'endereco': self.endereco,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'cep': self.cep,
            'telefone': self.telefone,
            'email': self.email,
            'justificativa_adocao': self.justificativa_adocao,
            'tem_outros_animais': self.tem_outros_animais,
            'tempo_sozinho': self.tempo_sozinho,
            'quantidade_animais': self.quantidade_animais,
            'tipos_animais': self.tipos_animais,
            'foto_pessoal_filename': self.foto_pessoal_filename,
            'foto_local_filename': self.foto_local_filename,
            'tem_criancas': self.tem_criancas,
            'quantidade_criancas': self.quantidade_criancas,
            'idades_criancas': self.idades_criancas,
            'restricoes_criancas': self.restricoes_criancas,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'localizacao_mapa_texto': self.localizacao_mapa_texto,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'foto_pessoal_url': self.foto_pessoal_url if hasattr(self, 'foto_pessoal_url') else None,
            'foto_local_url': self.foto_local_url if hasattr(self, 'foto_local_url') else None
        }

def criar_admin():
    with app.app_context():
        
        if not Admin.query.filter_by(username="admin").first():
            hashed_password = generate_password_hash("123")
            admin = Admin(username="admin", password=hashed_password)
            db.session.add(admin)
            db.session.commit()
            print("Administrador criado com sucesso!")

def remover_arquivo_se_existe(diretorio, nome_arquivo):
    """Função auxiliar para remover um arquivo se o nome for válido e ele existir."""
   
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

app.logger.setLevel(logging.DEBUG)

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

@app.route('/listar_admins')
def listar_admins():
    if 'admin' not in session:
        return redirect(url_for('login'))
   
    try:
        admins = Admin.query.order_by(Admin.username).all()
    except Exception as e:
        flash(f"Erro ao buscar administradores: {e}", "danger")
        admins = []
   
    admin_logado = session.get('admin')
    return render_template('listar_admins.html', admins=admins, admin_logado=admin_logado)


@app.route('/registrar_admin', methods=['GET', 'POST'])
def registrar_admin():
    if 'admin' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        erros = []
        
        if not username:
            erros.append('Nome de usuário é obrigatório.')
        else:
            
            user_existente = Admin.query.filter_by(username=username).first()
            if user_existente:
                erros.append(f'O nome de usuário "{username}" já está em uso.')
        if not password:
            erros.append('Senha é obrigatória.')
        if password != confirm_password:
            erros.append('As senhas não coincidem.')

        if erros:
            for erro in erros: flash(erro, 'danger')
            return render_template('registrar_admin.html', username=username)

        
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

    
    return render_template('registrar_admin.html')

@app.route('/editar_admin/<int:admin_id>', methods=['GET'])
def editar_admin_form(admin_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    admin_a_editar = Admin.query.get_or_404(admin_id)
    
    return render_template('editar_admin.html', admin=admin_a_editar)

@app.route('/editar_admin/<int:admin_id>', methods=['POST'])
def editar_admin_submit(admin_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    admin_a_editar = Admin.query.get_or_404(admin_id)
   
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    erros = []
   
    if new_password or confirm_password:
        if not new_password:
            erros.append('Nova senha é obrigatória para alterar.')
        if new_password != confirm_password:
            erros.append('As novas senhas não coincidem.')

        if not erros:
            try:
              
                admin_a_editar.password = generate_password_hash(new_password)
                db.session.commit()
                flash(f'Senha do administrador "{admin_a_editar.username}" atualizada com sucesso!', 'success')
                return redirect(url_for('listar_admins'))
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao atualizar a senha: {e}', 'danger')
                app.logger.error(f"Erro DB Update Admin Password: {e}")
               
                return render_template('editar_admin.html', admin=admin_a_editar)
        else:
            
            for erro in erros: flash(erro, 'danger')
            return render_template('editar_admin.html', admin=admin_a_editar)
    else:
        
        flash('Nenhuma alteração de senha foi fornecida.', 'info')
        return redirect(url_for('listar_admins'))


@app.route('/excluir_admin/<int:admin_id>', methods=['POST'])
def excluir_admin(admin_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    admin_a_excluir = Admin.query.get_or_404(admin_id)
    admin_logado = session.get('admin')

 
    if admin_a_excluir.username == admin_logado:
        flash('Você não pode excluir sua própria conta de administrador.', 'danger')
        return redirect(url_for('listar_admins'))

   
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

        
        ultimos_animais = Animal.query.order_by(Animal.data_cadastro.desc()).limit(5).all()
        
        stats_status = {
            'Disponível': animais_disponiveis,
            'Adotado': animais_adotados
        }
        
        stats_especie = db.session.query(Animal.especie, func.count(Animal.especie)).group_by(Animal.especie).order_by(func.count(Animal.especie).desc()).all()
        
        dados_grafico_especie = [[especie, count] for especie, count in stats_especie]


    except Exception as e:
        flash(f"Erro ao carregar dados do dashboard: {e}", "danger")
        app.logger.error(f"Erro Dashboard Query: {e}")
        total_animais = 0
        animais_disponiveis = 0
        animais_adotados = 0
        total_adotantes = 0
        ultimos_animais = []
        stats_status = {}
        dados_grafico_especie = []


   
    return render_template('dashboard.html', 
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

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/cadastrar_animal', methods=['GET', 'POST'])
def cadastrar_animal():
  
    if 'admin' not in session:
        return redirect(url_for('login'))

   
    initial_map_coords = {'lat': -14.2350, 'lng': -51.9253} 

    if request.method == 'POST':
      
        nome = request.form.get('nome')
        especie = request.form.get('especie')
        raca = request.form.get('raca')
        sexo = request.form.get('sexo')
        idade_str = request.form.get('idade')
        descricao = request.form.get('descricao')
        temperamento = request.form.get('temperamento')
        comportamento_outros = request.form.get('comportamento_outros')
        comportamento_criancas = request.form.get('comportamento_criancas')
        doencas_preexistentes = request.form.get('doencas_preexistentes')
        tratamentos = request.form.get('tratamentos')
        cor = request.form.get('cor')
        tamanho = request.form.get('tamanho')
        localizacao_texto = request.form.get('localizacao') 
        latitude_str = request.form.get('latitude')
        longitude_str = request.form.get('longitude')

        foto = request.files.get('foto')

        erros = []

        # --- Validações de Campos Obrigatórios e Formato ---
        if not nome: erros.append('O nome do animal é obrigatório.')
        if not especie: erros.append('A espécie do animal é obrigatória.')
        if not sexo: erros.append('O sexo do animal é obrigatório.')

        # --- Conversão e Validação de Idade ---
        idade = None
        if idade_str:
            try:
                idade = int(idade_str)
                if idade < 0:
                    erros.append('A idade não pode ser negativa.')
                    idade = None
            except ValueError:
                erros.append('A idade deve ser um número inteiro válido.')
                idade = None

        # --- Conversão e Validação de Coordenadas Geográficas ---
        latitude = None
        longitude = None
        if latitude_str and longitude_str:
            try:
                latitude = float(latitude_str)
                longitude = float(longitude_str)
                if not (-90 <= latitude <= 90):
                    erros.append('Latitude inválida (deve estar entre -90 e 90 graus).')
                    latitude = None
                if not (-180 <= longitude <= 180):
                    erros.append('Longitude inválida (deve estar entre -180 e 180 graus).')
                    longitude = None
            except (ValueError, TypeError):
                erros.append('Latitude e Longitude devem ser números válidos.')
                latitude, longitude = None, None
        elif latitude_str or longitude_str:
            erros.append('Latitude e Longitude devem ser fornecidas juntas, ou ambas deixadas em branco, se o marcador não for usado.')

        if not localizacao_texto and (latitude is None or longitude is None):
            erros.append('Forneça uma localização (clicando no mapa ou digitando o endereço textual).')


        # --- Tratamento da Foto ---
        foto_filename_salvar = None
        if foto and foto.filename != '':
            if allowed_file(foto.filename):
                nome_seguro = secure_filename(f"{uuid.uuid4()}_{foto.filename}")
                caminho_foto = os.path.join(app.config['UPLOAD_FOLDER'], nome_seguro)
                try:
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    foto.save(caminho_foto)
                    foto_filename_salvar = nome_seguro
                except Exception as e:
                    erros.append(f'Erro ao salvar a foto do animal: {str(e)}')
                    app.logger.error(f'Erro ao salvar foto do animal: {str(e)}')
            else:
                extensao_foto = foto.filename.rsplit('.',1)[-1].lower() if '.' in foto.filename else 'desconhecida'
                erros.append(f'Tipo de arquivo de foto não permitido ({extensao_foto}). Use PNG, JPG, JPEG ou GIF.')

        # --- Se houver erros de validação ou upload, re-renderizar o formulário ---
        if erros:
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER'], foto_filename_salvar)

            for erro_msg in erros:
                 flash(erro_msg, 'danger')

            app.logger.warning(f'Erros no formulário de cadastro de animal: {erros}')
            current_lat = request.form.get('latitude', initial_map_coords['lat'])
            current_lng = request.form.get('longitude', initial_map_coords['lng'])
            map_coords_repopulate = {'lat': current_lat, 'lng': current_lng}

            return render_template('cadastrar_animal.html',
                                   form_data=request.form,
                                   initial_map_coords=map_coords_repopulate)

        # --- Se tudo ok (sem erros), criar e salvar o objeto Animal ---
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
            localizacao=localizacao_texto,
            descricao=descricao,
            foto_filename=foto_filename_salvar,
            latitude=latitude,
            longitude=longitude,
        )

        try:
            db.session.add(novo_animal)
            db.session.commit()
            flash(f'Animal "{novo_animal.nome}" cadastrado com sucesso!', 'success')
            app.logger.info(f'Animal cadastrado: {novo_animal.nome}, ID: {novo_animal.id}')
            return redirect(url_for('listar_animais'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro interno ao salvar o animal no banco de dados: {str(e)}', 'danger')
            app.logger.error(f'Erro ao salvar animal no banco de dados: {str(e)}')

            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER'], foto_filename_salvar)

            current_lat = request.form.get('latitude', initial_map_coords['lat'])
            current_lng = request.form.get('longitude', initial_map_coords['lng'])
            map_coords_repopulate = {'lat': current_lat, 'lng': current_lng}

            return render_template('cadastrar_animal.html',
                                   form_data=request.form,
                                   initial_map_coords=map_coords_repopulate)

    # --- Requisição GET ---
    return render_template('cadastrar_animal.html',
                           form_data=None,
                           initial_map_coords=initial_map_coords)

@app.route('/listar_animais', methods=['GET'])
def listar_animais():
    if 'admin' not in session:
        return redirect(url_for('login'))

    query = Animal.query

    filtro_nome = request.args.get('filtro_nome', '').strip()
    filtro_especie = request.args.get('filtro_especie', '').strip()
    filtro_data_inicio_str = request.args.get('filtro_data_inicio', '').strip()
    filtro_data_fim_str = request.args.get('filtro_data_fim', '').strip()

    if filtro_nome:
        query = query.filter(Animal.nome.ilike(f'%{filtro_nome}%'))
    if filtro_especie:
        query = query.filter(Animal.especie.ilike(f'%{filtro_especie}%'))

    if filtro_data_inicio_str:
        try:
            data_inicio = datetime.strptime(filtro_data_inicio_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Animal.data_cadastro) >= data_inicio)
        except ValueError:
            flash("Formato de Data de Início inválido. Use AAAA-MM-DD.", "warning")

    if filtro_data_fim_str:
        try:
            data_fim = datetime.strptime(filtro_data_fim_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Animal.data_cadastro) <= data_fim)
        except ValueError:
            flash("Formato de Data de Fim inválido. Use AAAA-MM-DD.", "warning")

    try:
        animais = query.order_by(Animal.data_cadastro.desc(), Animal.nome).all()
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
    animal = Animal.query.get_or_404(animal_id)
    return render_template('detalhes_animal.html', animal=animal)

# --- Rota para Editar (GET - Mostrar formulário preenchido) ---
@app.route('/editar_animal/<int:animal_id>', methods=['GET'])
def editar_animal_form(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    animal = Animal.query.get_or_404(animal_id)
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
    idade = animal.idade
    if idade_str:
        try:
            idade = int(idade_str)
            if idade < 0: erros.append('A idade não pode ser negativa.')
        except ValueError: erros.append('A idade deve ser um número.')

    # --- Tratamento da Foto (Substituição) ---
    foto_filename = animal.foto_filename
    if foto and foto.filename != '':
        if allowed_file(foto.filename):
            if animal.foto_filename:
                old_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], animal.foto_filename)
                if os.path.exists(old_photo_path):
                    try:
                        os.remove(old_photo_path)
                    except OSError as e:
                        app.logger.error(f"Erro ao remover foto antiga {animal.foto_filename}: {e}")
            foto_filename = secure_filename(f"{uuid.uuid4()}_{foto.filename}")
            foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto_filename)
            try:
                foto.save(foto_path)
            except Exception as e:
                erros.append(f"Erro ao salvar a nova foto: {e}")
                foto_filename = animal.foto_filename
        else:
            erros.append('Tipo de arquivo de foto não permitido.')

    # --- Se houver erros, re-renderizar o formulário de edição ---
    if erros:
        for erro in erros:
            flash(erro, 'danger')
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
    animal.foto_filename = foto_filename

    try:
        db.session.commit()
        flash(f'Animal "{animal.nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('listar_animais'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar o animal: {e}', 'danger')
        return render_template('editar_animal.html', animal=animal)


# --- Rota para Excluir ---
@app.route('/excluir_animal/<int:animal_id>', methods=['POST'])
def excluir_animal(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    animal = Animal.query.get_or_404(animal_id)

    foto_filename_to_delete = animal.foto_filename

    try:
        db.session.delete(animal)
        db.session.commit()

        if foto_filename_to_delete:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], foto_filename_to_delete)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except OSError as e:
                    app.logger.error(f"Erro ao remover arquivo de foto {foto_filename_to_delete}: {e}")
                    flash(f'Animal excluído, mas houve um erro ao remover o arquivo de foto associado.', 'warning')

        flash(f'Animal "{animal.nome}" excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir o animal: {e}', 'danger')

    return redirect(url_for('listar_animais'))


# --- Rota para Marcar como Adotado ---
@app.route('/marcar_adotado/<int:animal_id>', methods=['POST'])
def marcar_adotado(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    animal = Animal.query.get_or_404(animal_id)

    try:
        animal.adotado = True
        db.session.commit()
        flash(f'Animal "{animal.nome}" marcado como adotado!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao marcar o animal como adotado: {e}', 'danger')

    return redirect(url_for('listar_animais'))

# --- Rota para Marcar como Disponível ---

@app.route('/marcar_disponivel/<int:animal_id>', methods=['POST'])
def marcar_disponivel(animal_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    animal = Animal.query.get_or_404(animal_id)

    if not animal.adotado:
        flash(f'O animal "{animal.nome}" já está marcado como disponível.', 'info')
        return redirect(url_for('listar_animais'))

    try:
        animal.adotado = False
        animal.adotante_id = None
        db.session.commit()
        flash(f'Animal "{animal.nome}" marcado como disponível novamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao marcar o animal como disponível: {e}', 'danger')
        app.logger.error(f"Erro DB Mark Available: {e}")

    return redirect(url_for('listar_animais'))

# --- Rota para Cadastrar Adotante (GET e POST) ---
import os
import uuid
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash
)


# --- Rota para Cadastrar Adotante (GET e POST) ---
import os
import uuid
from werkzeug.utils import secure_filename
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash
)


# --- Rota para Cadastrar Adotante (GET e POST) ---
@app.route('/cadastrar_adotante', methods=['GET', 'POST'])
def cadastrar_adotante():
    if 'admin' not in session:
        return redirect(url_for('login'))

    initial_map_coords_adotante = {'lat': -14.2350, 'lng': -51.9253}

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
        animal_interesse_form = request.form.get('animal_interesse')
        tipo_animal_interesse_form = request.form.get('tipo_animal_interesse')
        justificativa_adocao = request.form.get('justificativa_adocao')
        tem_outros_animais = request.form.get('tem_outros_animais')
        tempo_sozinho_str = request.form.get('tempo_sozinho')
        quantidade_animais_str = request.form.get('quantidade_animais')
        tipos_animais = request.form.get('tipos_animais')
        foto_pessoal = request.files.get('foto_pessoal')
        foto_local = request.files.get('foto_local')
        localizacao_mapa_texto = request.form.get('localizacao_mapa_texto')
        latitude_str = request.form.get('latitude')
        longitude_str = request.form.get('longitude')
        tem_criancas = request.form.get('tem_criancas')
        quantidade_criancas_str = request.form.get('quantidade_criancas')
        idades_criancas = request.form.get('idades_criancas')
        restricoes_criancas = request.form.get('restricoes_criancas')

        erros = []
        foto_pessoal_filename_salvar = None
        foto_local_filename_salvar = None

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

        if not endereco: erros.append("Endereço (Logradouro) é obrigatório.")
        if not bairro: erros.append("Bairro é obrigatório.")
        if not cidade: erros.append("Cidade é obrigatória.")
        if not cep: erros.append("CEP é obrigatório.")
        if not telefone: erros.append("Telefone é obrigatório.")
        if not email: erros.append("Email é obrigatório.")
        if not justificativa_adocao: erros.append("Justificativa da adoção é obrigatória.")
        if not tem_outros_animais: erros.append("Informe se possui outros animais na residência.")
        if not tem_criancas: erros.append("Informe se há crianças na residência.")


        # --- Conversão e Validação de Coordenadas Geográficas (Adotante) ---
        latitude = None
        longitude = None
        if latitude_str and longitude_str:
            try:
                latitude = float(latitude_str)
                longitude = float(longitude_str)
                if not (-90 <= latitude <= 90):
                    erros.append('Latitude da residência inválida.')
                    latitude = None
                if not (-180 <= longitude <= 180):
                    erros.append('Longitude da residência inválida.')
                    longitude = None
            except (ValueError, TypeError):
                erros.append('Latitude e Longitude da residência devem ser números válidos.')
                latitude, longitude = None, None
        elif latitude_str or longitude_str:
            erros.append('Latitude e Longitude da residência devem ser fornecidas juntas ou ambas em branco.')

        if (latitude is not None and longitude is not None) and not localizacao_mapa_texto:
            erros.append("Descrição textual da localização do mapa é recomendada se coordenadas foram selecionadas.")


        # --- Processar Foto Pessoal ---
        if foto_pessoal and foto_pessoal.filename != '':
            if allowed_file(foto_pessoal.filename):
                nome_seguro_pessoal = secure_filename(f"{uuid.uuid4()}_{foto_pessoal.filename}")
                caminho_pessoal = os.path.join(app.config['UPLOAD_FOLDER_ADOTANTES'], nome_seguro_pessoal)
                try:
                    foto_pessoal.save(caminho_pessoal)
                    foto_pessoal_filename_salvar = nome_seguro_pessoal
                except Exception as e:
                    erros.append(f"Erro ao salvar foto pessoal: {e}")
                    app.logger.error(f"Erro ao salvar foto pessoal: {e}")
            else:
                ext_pessoal = foto_pessoal.filename.rsplit('.',1)[-1].lower() if '.' in foto_pessoal.filename else 'desconhecida'
                erros.append(f"Tipo de arquivo não permitido para foto pessoal: .{ext_pessoal}")

        # --- Processar Foto do Local ---
        if foto_local and foto_local.filename != '':
            if allowed_file(foto_local.filename):
                nome_seguro_local = secure_filename(f"{uuid.uuid4()}_{foto_local.filename}")
                caminho_local = os.path.join(app.config['UPLOAD_FOLDER_ADOTANTES'], nome_seguro_local)
                try:
                    foto_local.save(caminho_local)
                    foto_local_filename_salvar = nome_seguro_local
                except Exception as e:
                    erros.append(f"Erro ao salvar foto do local: {e}")
                    app.logger.error(f"Erro ao salvar foto do local: {e}")
            else:
                ext_local = foto_local.filename.rsplit('.',1)[-1].lower() if '.' in foto_local.filename else 'desconhecida'
                erros.append(f"Tipo de arquivo não permitido para foto do local: .{ext_local}")

        # --- Conversão de Tipos e Validações Condicionais (Outros Animais) ---
        tempo_sozinho = None
        if tempo_sozinho_str:
            try:
                tempo_sozinho = int(tempo_sozinho_str)
                if tempo_sozinho < 0:
                     erros.append('Tempo sozinho (horas) não pode ser negativo.')
            except ValueError:
                if "Tempo sozinho deve ser um número de horas." not in erros and "Tempo sozinho deve ser um número válido." not in erros :
                    erros.append('Tempo sozinho (horas) deve ser um número válido.')

        quantidade_animais_convertida = None
        tipos_animais_para_salvar = tipos_animais
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

        # --- Conversão de Tipos e Validações Condicionais (Crianças) ---
        quantidade_criancas_convertida = None
        idades_criancas_para_salvar = idades_criancas
        restricoes_criancas_para_salvar = restricoes_criancas
        if tem_criancas == 'Sim':
            if not quantidade_criancas_str:
                erros.append("Informe a quantidade de crianças.")
            else:
                try:
                    quantidade_criancas_convertida = int(quantidade_criancas_str)
                    if quantidade_criancas_convertida < 1:
                        erros.append('Quantidade de crianças deve ser pelo menos 1.')
                except ValueError:
                    erros.append('Quantidade de crianças deve ser um número válido.')
            if not idades_criancas_para_salvar:
                 erros.append("Informe a(s) idade(s) da(s) criança(s).")
        elif tem_criancas == 'Nao':
            quantidade_criancas_convertida = None
            idades_criancas_para_salvar = None
            restricoes_criancas_para_salvar = None


        # --- Se houver erros (de validação ou upload), re-renderizar o formulário ---
        if erros:
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_pessoal_filename_salvar)
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_local_filename_salvar)
            for erro_msg in erros:
                 flash(erro_msg, 'danger')

            current_lat_adotante = request.form.get('latitude', initial_map_coords_adotante['lat'])
            current_lng_adotante = request.form.get('longitude', initial_map_coords_adotante['lng'])
            try:
                map_coords_repopulate_adotante = {
                    'lat': float(current_lat_adotante) if current_lat_adotante else initial_map_coords_adotante['lat'],
                    'lng': float(current_lng_adotante) if current_lng_adotante else initial_map_coords_adotante['lng']
                }
            except (ValueError, TypeError):
                map_coords_repopulate_adotante = initial_map_coords_adotante

            return render_template('cadastrar_adotante.html',
                                   form_data=request.form,
                                   initial_map_coords_adotante=map_coords_repopulate_adotante)

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
            justificativa_adocao=justificativa_adocao,
            tem_outros_animais=tem_outros_animais,
            tempo_sozinho=tempo_sozinho,
            quantidade_animais=quantidade_animais_convertida,
            tipos_animais=tipos_animais_para_salvar,
            tem_criancas=tem_criancas,
            quantidade_criancas=quantidade_criancas_convertida,
            idades_criancas=idades_criancas_para_salvar,
            restricoes_criancas=restricoes_criancas_para_salvar,
            localizacao_mapa_texto=localizacao_mapa_texto,
            latitude=latitude,
            longitude=longitude,
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
            msg_erro_db = f'Erro interno ao salvar o adotante: {str(e)}'
            if "UNIQUE constraint failed" in str(e):
                if "adotante.cpf" in str(e):
                    msg_erro_db = f"Erro: O CPF '{cpf}' já está cadastrado."
                elif "adotante.rg" in str(e):
                    msg_erro_db = f"Erro: O RG '{rg}' já está cadastrado."
            flash(msg_erro_db, 'danger')
            app.logger.error(f"Erro DB Insert Adotante: {e} - Dados: {request.form}")

            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_pessoal_filename_salvar)
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_local_filename_salvar)

            current_lat_adotante = request.form.get('latitude', initial_map_coords_adotante['lat'])
            current_lng_adotante = request.form.get('longitude', initial_map_coords_adotante['lng'])
            try:
                map_coords_repopulate_adotante = {
                    'lat': float(current_lat_adotante) if current_lat_adotante else initial_map_coords_adotante['lat'],
                    'lng': float(current_lng_adotante) if current_lng_adotante else initial_map_coords_adotante['lng']
                }
            except (ValueError, TypeError):
                map_coords_repopulate_adotante = initial_map_coords_adotante

            return render_template('cadastrar_adotante.html',
                                   form_data=request.form,
                                   initial_map_coords_adotante=map_coords_repopulate_adotante)

    # --- Requisição GET ---
    return render_template('cadastrar_adotante.html',
                           form_data=None,
                           initial_map_coords_adotante=initial_map_coords_adotante)

@app.route('/listar_adotantes', methods=['GET'])
def listar_adotantes():
    if 'admin' not in session:
        return redirect(url_for('login'))

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
        query = query.filter(Adotante.cpf.like(f'{filtro_cpf_adotante}%'))

    if filtro_data_inicio_adotante_str:
        try:
            data_inicio = datetime.strptime(filtro_data_inicio_adotante_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Adotante.data_cadastro) >= data_inicio)
        except ValueError:
            flash("Formato de Data de Início (Adotante) inválido. Use AAAA-MM-DD.", "warning")

    if filtro_data_fim_adotante_str:
        try:
            data_fim = datetime.strptime(filtro_data_fim_adotante_str, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Adotante.data_cadastro) <= data_fim)
        except ValueError:
            flash("Formato de Data de Fim (Adotante) inválido. Use AAAA-MM-DD.", "warning")

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
    except Exception as e:
        flash(f"Erro ao buscar animais disponíveis: {e}", "warning")
        app.logger.error(f"Erro ao buscar animais disponíveis: {e}")
        animais_disponiveis = []

    return render_template('editar_adotante.html',
                           adotante=adotante,
                           animais_disponiveis=animais_disponiveis,
                           form_data=None)

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
    tem_criancas = request.form.get('tem_criancas')
    quantidade_criancas_str = request.form.get('quantidade_criancas')
    idades_criancas = request.form.get('idades_criancas')
    restricoes_criancas = request.form.get('restricoes_criancas')
    foto_pessoal_nova = request.files.get('foto_pessoal')
    foto_local_nova = request.files.get('foto_local')
    localizacao_mapa_texto = request.form.get('localizacao_mapa_texto')
    latitude_str = request.form.get('latitude')
    longitude_str = request.form.get('longitude')    

    erros = []
    # --- Validações ---
    if not nome_completo: erros.append("Nome completo é obrigatório.")
    if not rg: erros.append("RG é obrigatório.")
    if not cpf:
        erros.append("CPF é obrigatório.")
    else:
        cpf_existente = Adotante.query.filter(Adotante.cpf == cpf, Adotante.id != adotante_id).first()
        if cpf_existente:
            erros.append(f'O CPF "{cpf}" já está cadastrado para outro adotante ({cpf_existente.nome_completo}).')


    latitude = adotante.latitude
    longitude = adotante.longitude
    if latitude_str and longitude_str:
            try:
                latitude = float(latitude_str)
                longitude = float(longitude_str)
                if not (-90 <= latitude <= 90): erros.append('Latitude da residência inválida.'); latitude = adotante.latitude
                if not (-180 <= longitude <= 180): erros.append('Longitude da residência inválida.'); longitude = adotante.longitude
            except (ValueError, TypeError):
                erros.append('Latitude e Longitude da residência devem ser números válidos.');
                latitude, longitude = adotante.latitude, adotante.longitude
    elif latitude_str or longitude_str:
            erros.append('Latitude e Longitude da residência devem ser alteradas juntas ou ambas mantidas.')
            latitude, longitude = adotante.latitude, adotante.longitude

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
        for erro in erros: flash(erro, 'danger')
        current_lat_adotante = request.form.get('latitude', adotante.latitude if adotante.latitude is not none else -14.2350)
        current_lng_adotante = request.form.get('longitude', adotante.longitude if adotante.longitude is not none else -51.9253)
        map_coords_repopulate_adotante = {
                'lat': float(current_lat_adotante) if current_lat_adotante else -14.2350,
                'lng': float(current_lng_adotante) if current_lng_adotante else -51.9253
            }
        return render_template('editar_adotante.html',
                                   adotante=adotante,
                                   form_data=request.form,
                                   initial_map_coords_adotante=map_coords_repopulate_adotante)

    # --- Se não houver erros, atualizar os dados do objeto adotante ---
    if nova_foto_pessoal_salva:
        remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], adotante.foto_pessoal_filename)
    if nova_foto_local_salva:
         remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], adotante.foto_local_filename)

    adotante.nome_completo = nome_completo
    adotante.rg = rg
    adotante.cpf = cpf
    adotante.tem_criancas = tem_criancas
    adotante.idades_criancas = idades_criancas
    adotante.restricoes_criancas = restricoes_criancas
    adotante.foto_pessoal_filename = foto_pessoal_filename_atualizar
    adotante.foto_local_filename = foto_local_filename_atualizar
    adotante.localizacao_mapa_texto = localizacao_mapa_texto
    adotante.latitude = latitude
    adotante.longitude = longitude

    adotante.tem_criancas = tem_criancas
    if tem_criancas == 'Sim':
        adotante.quantidade_criancas = quantidade_criancas
        adotante.idades_criancas = idades_criancas
        adotante.restricoes_criancas = restricoes_criancas
    else:
        adotante.quantidade_criancas = None
        adotante.idades_criancas = None
        adotante.restricoes_criancas = None

    # --- Tenta salvar as alterações no banco de dados ---
    try:
        db.session.commit()
        flash(f'Dados de "{adotante.nome_completo}" atualizados com sucesso!', 'success')
        return redirect(url_for('listar_adotantes'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar dados do adotante no banco de dados: {e}', 'danger')
        app.logger.error(f"Erro DB Update Adotante {adotante.id}: {e}")
        if nova_foto_pessoal_salva:
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_pessoal_filename_atualizar)
        if nova_foto_local_salva:
            remover_arquivo_se_existe(app.config['UPLOAD_FOLDER_ADOTANTES'], foto_local_filename_atualizar)
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
    if animal.adotado:
        flash(f'O animal "{animal.nome}" já está marcado como adotado.', 'warning')
        return redirect(url_for('listar_animais'))

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
    adotante_id_selecionado = request.form.get('adotante_selecionado_id')

    if not adotante_id_selecionado:
        flash('Você precisa selecionar um adotante.', 'danger')
        adotantes_disponiveis = Adotante.query.order_by(Adotante.nome_completo).all()
        return render_template('registrar_adocao.html', animal=animal, adotantes=adotantes_disponiveis)

    adotante_selecionado = Adotante.query.get(adotante_id_selecionado)
    if not adotante_selecionado:
        flash('Adotante selecionado inválido ou não encontrado.', 'danger')
        adotantes_disponiveis = Adotante.query.order_by(Adotante.nome_completo).all()
        return render_template('registrar_adocao.html', animal=animal, adotantes=adotantes_disponiveis)

    if animal.adotado:
        flash(f'O animal "{animal.nome}" já foi adotado (possivelmente por outra pessoa enquanto você preenchia).', 'warning')
        return redirect(url_for('listar_animais'))

    try:
        # --- ATUALIZA O ANIMAL ---
        animal.adotado = True
        animal.adotante_id = adotante_id_selecionado

        db.session.commit()
        flash(f'Adoção do animal "{animal.nome}" por "{adotante_selecionado.nome_completo}" registrada com sucesso!', 'success')
        return redirect(url_for('listar_animais'))

    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao registrar a adoção: {e}', 'danger')
        app.logger.error(f"Erro DB Register Adoption: {e}")
        adotantes_disponiveis = Adotante.query.order_by(Adotante.nome_completo).all()
        return render_template('registrar_adocao.html', animal=animal, adotantes=adotantes_disponiveis)
        
@app.route('/teste_mapa')
def teste_mapa():
    return render_template('teste_mapa.html')        

@app.route('/api/animais', methods=['GET'])
def get_animais_api():
    try:
        query = Animal.query

        status = request.args.get('status') 
        especie_filter = request.args.get('especie')
        idade_min_filter = request.args.get('idade_min')
        idade_max_filter = request.args.get('idade_max')

        if status:
            if status.lower() == 'disponivel':
                query = query.filter(Animal.adotado == False)
            elif status.lower() == 'adotado':
                query = query.filter(Animal.adotado == True)

        if especie_filter:
            query = query.filter(Animal.especie.ilike(f'%{especie_filter}%'))

        if idade_min_filter and idade_min_filter.isdigit():
            query = query.filter(Animal.idade >= int(idade_min_filter))

        if idade_max_filter and idade_max_filter.isdigit():
            query = query.filter(Animal.idade <= int(idade_max_filter))

        # --- Paginação Opcional ---
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int) 
        paginated_animais = query.order_by(Animal.data_cadastro.desc()).paginate(page=page, per_page=per_page, error_out=False)
        
        animais_list = [animal.to_dict() for animal in paginated_animais.items]

        return jsonify({
            "animais": animais_list,
            "total_resultados": paginated_animais.total,
            "pagina_atual": paginated_animais.page,
            "total_paginas": paginated_animais.pages,
            "proxima_pagina": paginated_animais.next_num,
            "pagina_anterior": paginated_animais.prev_num
        }), 200

    except Exception as e:
        app.logger.error(f"Erro na API /api/animais: {e}")
        return jsonify({"erro": "Ocorreu um erro interno ao processar a solicitação."}), 500
    
@app.route('/api/animais/<int:animal_id>', methods=['GET'])
def get_animal_api(animal_id):
    try:
        animal = Animal.query.get(animal_id)
        if animal:
            return jsonify(animal.to_dict(include_adotante_info=True)), 200
        else:
            return jsonify({"erro": "Animal não encontrado"}), 404
    except Exception as e:
        app.logger.error(f"Erro na API /api/animais/{animal_id}: {e}")
        return jsonify({"erro": "Ocorreu um erro interno ao processar a solicitação."}), 500
    
@app.route('/api/adotantes', methods=['GET'])
def get_adotantes_api():

    if 'admin' not in session:
        return jsonify({"erro": "Acesso não autorizado"}), 401

    try:
        adotantes = Adotante.query.order_by(Adotante.nome_completo).all()
        adotantes_list = [adotante.to_dict_public() for adotante in adotantes]
        return jsonify(adotantes_list), 200
    except Exception as e:
        app.logger.error(f"Erro na API /api/adotantes: {e}")
        return jsonify({"erro": "Ocorreu um erro interno ao processar a solicitação."}), 500

@app.route('/api/adotantes/<int:adotante_id>', methods=['GET'])
def get_adotante_api(adotante_id):
    if 'admin' not in session: 
        return jsonify({"erro": "Acesso não autorizado"}), 401
        
    try:
        adotante = Adotante.query.get(adotante_id)
        if adotante:
            return jsonify(adotante.to_dict_full()), 200
        else:
            return jsonify({"erro": "Adotante não encontrado"}), 404
    except Exception as e:
        app.logger.error(f"Erro na API /api/adotantes/{adotante_id}: {e}")
        return jsonify({"erro": "Ocorreu um erro interno ao processar a solicitação."}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        criar_admin()
    app.run(debug=True)