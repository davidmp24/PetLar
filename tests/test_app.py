# tests/test_app.py
import pytest
from flask import session

def test_app_creation(app):
    """Verifica se a fixture 'app' é criada corretamente."""
    assert app is not None
    assert app.config['TESTING'] is True

def test_home_redirects_to_login(client):
    """Verifica se a rota '/' redireciona para '/login' sem sessão."""
    response = client.get('/', follow_redirects=False) # Não seguir redirecionamentos
    assert response.status_code == 302 # 302 Found (Redirect)
    assert response.location == '/login' # Verifica se redireciona para a página de login

def test_dashboard_requires_login(client):
    """Verifica se o acesso ao dashboard sem login redireciona."""
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert response.location == '/login'

def test_login_page_loads(client):
    """Verifica se a página de login carrega corretamente (GET)."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'<h3>Login</h3>' in response.data # Verifica se um elemento esperado está no HTML
    assert b'Usu\xc3\xa1rio' in response.data # Testa string com acento (usuário)
    assert b'Senha' in response.data

def test_successful_login_logout(client, db, default_admin): # Usa a fixture db e default_admin
    """Testa um login bem-sucedido e o logout."""
    # Tenta logar com as credenciais do default_admin
    response = client.post('/login', data={
        'username': 'testadmin',
        'password': 'password'
    }, follow_redirects=False) # Post para a rota de login

    assert response.status_code == 302 # Espera redirecionamento após login
    assert response.location == '/dashboard' # Espera redirecionamento para o dashboard

    # Para verificar se a sessão foi criada, fazemos uma nova requisição
    # e vemos se a sessão existe ou se a página carregada é a esperada.
    # Alternativamente, podemos usar o contexto do cliente para inspecionar a sessão.
    with client: # Entra no contexto do cliente para acessar a sessão
         client.get('/dashboard') # Acessa uma página protegida
         assert session.get('admin') == 'testadmin' # Verifica se a chave 'admin' foi definida na sessão

    # Testa o logout
    response_logout = client.get('/logout', follow_redirects=False)
    assert response_logout.status_code == 302
    assert response_logout.location == '/login'

    # Verifica se a sessão foi removida após o logout
    with client:
        client.get('/') # Acessa uma página que redireciona se não logado
        assert 'admin' not in session

def test_failed_login(client, db, default_admin):
    """Testa um login com credenciais inválidas."""
    response = client.post('/login', data={
        'username': 'testadmin',
        'password': 'wrongpassword'
    }, follow_redirects=True) # Seguir redirecionamentos aqui pode ser útil para ver a página final

    assert response.status_code == 200 # Deve permanecer na página de login (200 OK)
    assert b'Usu\xc3\xa1rio ou senha inv\xc3\xa1lidos!' in response.data # Verifica a mensagem de erro
    with client:
        assert 'admin' not in session # Garante que a sessão não foi criada