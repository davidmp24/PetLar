# tests/conftest.py
import pytest
import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# AGORA você pode importar do seu módulo app
from app import app as flask_app, db as sqlalchemy_db

TEST_DATABASE_URI = 'sqlite:///:memory:'
# Ou: TEST_DATABASE_URI = 'sqlite:///test_petlar.db' # Usar arquivo para testes (permite inspecionar depois)

@pytest.fixture(scope='session')
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URI,
        "SECRET_KEY": "pytest-secret-key",
        "WTF_CSRF_ENABLED": False,
        "LOGIN_DISABLED": False,
    })
    yield flask_app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db(app):
    with app.app_context():
        sqlalchemy_db.create_all()
        yield sqlalchemy_db
        sqlalchemy_db.session.remove()
        sqlalchemy_db.drop_all()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def default_admin(db):
    from app import Admin # Mover import para dentro se necessário
    from werkzeug.security import generate_password_hash
    admin_user = Admin(username="testadmin", password=generate_password_hash("password"))
    db.session.add(admin_user)
    db.session.commit()
    return admin_user