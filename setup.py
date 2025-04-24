# setup.py
from setuptools import setup, find_packages

setup(
    name='petlar',
    version='0.1.0',
    packages=find_packages(), # Encontra automaticamente seu pacote 'app' (se estruturado como pacote)
    # Se 'app.py' está na raiz, pode precisar ajustar ou reestruturar
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        Flask==2.2.2
        Flask-SQLAlchemy==2.5.1
        Flask-WTF==1.0.0
        Flask-Login==0.5.0
        requests==2.26.0
        Werkzeug==2.2.3
        SQLAlchemy<2.0
        pytest
        pytest-flask
        pytest-cov
        # ou leia do arquivo
    ],
)