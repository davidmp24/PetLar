🐾 PetLar – Sistema de Adoção de Animais

PetLar é um sistema web desenvolvido como parte do Projeto Integrador da UNIVESP com o objetivo de otimizar o processo de adoção de animais de uma ONG local. A aplicação busca substituir fichas físicas por uma solução digital segura, padronizada e acessível, facilitando o cadastro, organização e acompanhamento de animais e adotantes.

 
 ### Funcionalidades ###
 
✅ Cadastro completo de animais com foto, características, comportamento e status de adoção.

✅ Cadastro de adotantes com validações, imagem e informações comportamentais.

✅ Autenticação de administradores (login seguro).

✅ Dashboard administrativo com gráficos estatísticos.

✅ Listagem de animais e adotantes com filtros de busca.

✅ Histórico de adoções com rastreabilidade.

✅ Upload de imagens de animais e adotantes.

✅ Interface responsiva com HTML, CSS e JavaScript.

✅ Banco de dados relacional com SQLite.

### Tela de Login
![Tela de Login](images/login.png)

### Dashboard
![Dashboard](images/dashboard.png)
   
### Cadastro de Animal
![Cadastro de Animal](images/cad-animal.png)

### Lista de Animais
![Lista de Animais](images/lista-animais.png)

### Detalhes do Animal
![Detalhes do Animal](images/detalhes-animal.png)


###🧱 Estrutura do Projeto: ###

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

###🔧 Tecnologias Utilizadas ###

   • Python 3.11

   • Flask

   • SQLite

   • SQLAlchemy

   • HTML/CSS/JS (Bootstrap)

   • Pytest para testes

   • GitHub para versionamento
   
   • Gráficos com Chart.js


### 📄 API RESTful do PetLar ###

O sistema PetLar fornece uma API RESTful para permitir a consulta de dados de animais e, com restrições, de adotantes. Os endpoints retornam dados no formato JSON.

#### Endpoints de Animais

1.  **`GET /api/animais`**: Lista animais cadastrados.
    *   **Método:** `GET`
    *   **Query Parameters Opcionais:**
        *   `status`: Filtra por status de adoção. Valores possíveis: `disponivel`, `adotado`.
            *   Exemplo: `/api/animais?status=disponivel`
        *   `especie`: Filtra por espécie (busca parcial, case-insensitive).
            *   Exemplo: `/api/animais?especie=gato`
        *   `idade_min`: Filtra por idade mínima (inteiro).
            *   Exemplo: `/api/animais?idade_min=2`
        *   `idade_max`: Filtra por idade máxima (inteiro).
            *   Exemplo: `/api/animais?idade_max=5`
        *   `page`: Número da página para paginação (padrão: 1).
            *   Exemplo: `/api/animais?page=2`
        *   `per_page`: Número de itens por página (padrão: 10).
            *   Exemplo: `/api/animais?per_page=5`
    *   **Resposta de Sucesso (200 OK):**
        ```json
        {
          "animais": [
            {
              "id": 1,
              "nome": "Rex",
              "especie": "Cachorro",
              "raca": "Vira-lata",
              "sexo": "Macho",
              "idade": 3,
              "data_cadastro": "2023-10-26T10:00:00",
              "temperamento": "Brincalhão",
              "comportamento_outros": "Sociável",
              "comportamento_criancas": "Bom",
              "doencas_preexistentes": "Nenhuma",
              "tratamentos": "Vermifugado",
              "cor": "Caramelo",
              "tamanho": "Médio",
              "localizacao_texto": "Encontrado perto do Parque Central",
              "descricao": "Muito dócil e adora correr.",
              "foto_url": "http://127.0.0.1:5000/static/uploads/animais/foto_rex.jpg",
              "latitude": -23.550520,
              "longitude": -46.633308,
              "adotado": false
            }
         
          ],
          "total_resultados": 20,
          "pagina_atual": 1,
          "total_paginas": 2,
          "proxima_pagina": 2,
          "pagina_anterior": null
        }
        ```

2.  **`GET /api/animais/<int:animal_id>`**: Retorna os detalhes de um animal específico.
    *   **Método:** `GET`
    *   **Parâmetro de URL:** `animal_id` (inteiro, ID do animal)
    *   **Resposta de Sucesso (200 OK):**
        ```json
        {
          "id": 1,
          "nome": "Rex",
       
          "adotado": true,
          "adotante": { 
            "id": 5,
            "nome_completo": "Maria Silva"
          }
        }
        ```
    *   **Resposta de Erro (404 Not Found):**
        ```json
        {
          "erro": "Animal não encontrado"
        }
        ```

#### Endpoints de Adotantes (Requer Autenticação de Administrador)

*Atenção: O acesso a estes endpoints requer que o usuário esteja logado como administrador no sistema web.*

1.  **`GET /api/adotantes`**: Lista todos os adotantes cadastrados (versão pública com dados limitados).
    *   **Método:** `GET`
    *   **Autenticação:** Sessão de administrador ativa.
    *   **Resposta de Sucesso (200 OK):**
        ```json
        [
          {
            "id": 5,
            "nome_completo": "Maria Silva",
            "foto_pessoal_url": "http://127.0.0.1:5000/static/uploads/adotantes/foto_maria.jpg"
          }
       
        ]
        ```
    *   **Resposta de Erro (401 Unauthorized):**
        ```json
        {
          "erro": "Acesso não autorizado"
        }
        ```

2.  **`GET /api/adotantes/<int:adotante_id>`**: Retorna os detalhes completos de um adotante específico.
    *   **Método:** `GET`
    *   **Parâmetro de URL:** `adotante_id` (inteiro, ID do adotante)
    *   **Autenticação:** Sessão de administrador ativa.
    *   **Resposta de Sucesso (200 OK):**
        ```json
        {
          "id": 5,
          "nome_completo": "Maria Silva",
          "rg": "123456789",
          "cpf": "11122233344",
          
          "foto_pessoal_url": "http://127.0.0.1:5000/static/uploads/adotantes/foto_maria.jpg",
          "foto_local_url": "http://127.0.0.1:5000/static/uploads/adotantes/local_maria.jpg"
        }
        ```
    *   **Resposta de Erro (404 Not Found):**
        ```json
        {
          "erro": "Adotante não encontrado"
        }
        ```
    *   **Resposta de Erro (401 Unauthorized):**
        ```json
        {
          "erro": "Acesso não autorizado"
        }
        ```