import pytest
from flask import session

def test_app_creation(app):
    """Verifica se a fixture 'app' é criada corretamente."""
    assert app is not None
    assert app.config['TESTING'] is True

def test_home_redirects_to_login(client):
    """Verifica se a rota '/' redireciona para '/login' sem sessão."""
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302
    assert response.location == '/login'

def test_dashboard_requires_login(client):
    """Verifica se o acesso ao dashboard sem login redireciona."""
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert response.location == '/login'

def test_login_page_loads(client):
    """Verifica se a página de login carrega corretamente (GET)."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'<h3>Login</h3>' in response.data
    assert b'Usu\xc3\xa1rio' in response.data
    assert b'Senha' in response.data

def test_successful_login_logout(client, db, default_admin):
    """Testa um login bem-sucedido e o logout."""
    response = client.post('/login', data={
        'username': 'testadmin',
        'password': 'password'
    }, follow_redirects=False)

    assert response.status_code == 302
    assert response.location == '/dashboard'

    with client:
         client.get('/dashboard')
         assert session.get('admin') == 'testadmin'

    response_logout = client.get('/logout', follow_redirects=False)
    assert response_logout.status_code == 302
    assert response_logout.location == '/login'

    with client:
        client.get('/')
        assert 'admin' not in session

def test_failed_login(client, db, default_admin):
    """Testa um login com credenciais inválidas."""
    response = client.post('/login', data={
        'username': 'testadmin',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Usu\xc3\xa1rio ou senha inv\xc3\xa1lidos!' in response.data
    with client:
        assert 'admin' not in session