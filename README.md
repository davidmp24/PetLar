🐾 PetLar – Sistema de Adoção de Animais
PetLar é um sistema web desenvolvido como parte do Projeto Integrador da UNIVESP com o objetivo de otimizar o processo de adoção de animais de uma ONG local. A aplicação busca substituir fichas físicas por uma solução digital segura, padronizada e acessível, facilitando o cadastro, organização e acompanhamento de animais e adotantes.

 Funcionalidades
✅ Cadastro completo de animais com foto, características, comportamento e status de adoção.

✅ Cadastro de adotantes com validações, imagem e informações comportamentais.

✅ Autenticação de administradores (login seguro).

✅ Dashboard administrativo com gráficos estatísticos.

✅ Listagem de animais e adotantes com filtros de busca.

✅ Histórico de adoções com rastreabilidade.

✅ Upload de imagens de animais e adotantes.

✅ Interface responsiva com HTML, CSS e JavaScript.

✅ Banco de dados relacional com SQLite.

🧱 Estrutura do Projeto:

PetLar/
├── app/
│   ├── static/
│   │   ├── css/
│   │   └── images/
│   ├── templates/
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── cadastrar_animal.html
│   │   └── ...
│   ├── models/
│   │   └── models.py
│   ├── routes/
│   │   └── views.py
│   ├── forms.py
│   └── __init__.py
├── database/
│   └── petlar.db
├── tests/
│   └── test_app.py
├── requirements.txt
└── run.py

🔧 Tecnologias Utilizadas

   • Python 3.11

   • Flask

   • SQLite

   • SQLAlchemy

   • HTML/CSS/JS (Bootstrap)

   • Pytest para testes

   • GitHub para versionamento
   
   • Gráficos com Chart.js

   
