import pytest
from app import Admin, Animal, Adotante
from werkzeug.security import check_password_hash

def test_admin_model(db):
    """Testa a criação e recuperação de um Admin."""
    from werkzeug.security import generate_password_hash
    password = "securepassword"
    hashed_password = generate_password_hash(password)
    admin = Admin(username="testuser", password=hashed_password)

    db.session.add(admin)
    db.session.commit()

    retrieved_admin = Admin.query.filter_by(username="testuser").first()
    assert retrieved_admin is not None
    assert retrieved_admin.username == "testuser"
    assert check_password_hash(retrieved_admin.password, password)

def test_animal_model(db):
    """Testa a criação e recuperação de um Animal."""
    animal = Animal(nome="Buddy", especie="Cachorro", idade=3)
    db.session.add(animal)
    db.session.commit()

    retrieved_animal = Animal.query.filter_by(nome="Buddy").first()
    assert retrieved_animal is not None
    assert retrieved_animal.especie == "Cachorro"
    assert retrieved_animal.idade == 3
    assert retrieved_animal.adotado is False

def test_adotante_model(db):
    """Testa a criação e recuperação de um Adotante."""
    adotante = Adotante(
        nome_completo="Maria Silva",
        rg="123456789",
        cpf="11122233344",
        endereco="Rua Teste, 123",
        bairro="Centro",
        cidade="TesteCity",
        cep="12345-678",
        telefone="99999-8888",
        email="maria.silva@email.com",
        animal_interesse="Buddy",
        tipo_animal_interesse="Cachorro",
        tem_outros_animais="Nao"
    )
    db.session.add(adotante)
    db.session.commit()

    retrieved_adotante = Adotante.query.filter_by(cpf="11122233344").first()
    assert retrieved_adotante is not None
    assert retrieved_adotante.nome_completo == "Maria Silva"
    assert retrieved_adotante.email == "maria.silva@email.com"