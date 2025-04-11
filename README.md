# Projeto Tooff

![Python Version](https://img.shields.io/badge/python-3.11.3-blue.svg) ![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red.svg)
![License](https://img.shields.io/github/license/KaelDucatti/projeto_tooff)

Uma aplicação web interativa desenvolvida com Streamlit.

# TôOff

**TôOff** é uma aplicação web desenvolvida para facilitar a **gestão de férias em equipes corporativas**, promovendo transparência e organização. O sistema permite que membros da equipe visualizem períodos de ausência uns dos outros, evitando sobreposições e facilitando o planejamento coletivo.

## Demonstração

Acesse o sistema online em: [tooff-webapp](https://projeto-tooff-503988005307.us-central1.run.app)  

## Funcionalidades

- Login seguro com autenticação via email e senha  
- Cadastro e visualização de férias com datas de início e fim  
- Visualização em calendário para acompanhar a escala de férias da equipe  
- Sistema de permissões para controle de acesso (usuários vs admins)  
- Envio de email de confirmação de solicitação de férias (via SendGrid)  
- Interface responsiva com Streamlit  
- Gerenciamento de dados com MySQL + SQLAlchemy  
- Criptografia de senhas com Werkzeug  
- Deploy automatizado via GitHub + Google Cloud Platform (Cloud Run)  
- Logs centralizados com GCP Logging  

## Tecnologias Utilizadas

- **Frontend / Interface**: [Streamlit](https://streamlit.io)  
- **Backend / API**: Python + SQLAlchemy  
- **Banco de Dados**: MySQL (Cloud SQL)  
- **CI/CD & Deploy**: GitHub Actions, Docker, Google Cloud Run  
- **Monitoramento**: GCP Cloud Logging  
- **Envio de Emails**: SendGrid  
- **Autenticação e Criptografia**: Werkzeug  
- **Servidor Web**: Nginx (via Docker Compose)  

## Arquitetura

A arquitetura do projeto segue o padrão **Three-Tier**:

```
[ Apresentação ]
       |
[ Lógica de Negócio ]
       |
[ Camada de Dados ]
```

- **Apresentação**: Streamlit WebApp  
- **Lógica de Negócio**: Python + SQLAlchemy  
- **Dados**: MySQL (Google Cloud SQL)  



## Começando

Siga estas instruções para obter uma cópia do projeto em execução na sua máquina local.

### Pré-requisitos

* Python 3.11.3 (ou a versão que você está usando)
* Pip (gerenciador de pacotes Python)
* Git (sistema de controle de versão)
* Opcional: Um ambiente virtual (`venv` ou `virtualenv`) é fortemente recomendado.

### Instalação

1.  **Crie e Navegue até o diretório do projeto:**
    ```bash
    mkdir projeto_tooff ; cd projeto_tooff         
    ```

2.  **Inicie o Git na pasta local do projeto:**
    ```bash
    git init
    ```

3.  **Clone o repositório:**
    ```bash
    git clone https://github.com/KaelDucatti/projeto_tooff.git
    ```

4.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```
5.  **Instale as dependências:**
    Certifique-se de que seu arquivo `requirements.txt` lista `streamlit` e todas as outras bibliotecas necessárias.
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Após a instalação das dependências, você pode iniciar a aplicação Streamlit:

1.  Execute o comando a partir do diretório raiz do projeto:
    ```bash
    streamlit run webapp.py
    ```
    *(Substitua `main.py` pelo nome do seu arquivo Python principal, se for diferente)*

2.  O Streamlit iniciará um servidor local e geralmente abrirá a aplicação automaticamente no seu navegador. Caso contrário, acesse o endereço fornecido no terminal (normalmente `http://localhost:8501`).

