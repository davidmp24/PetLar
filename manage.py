# manage.py
from flask.cli import FlaskGroup
from app import app  # Importe sua instância do Flask

cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()