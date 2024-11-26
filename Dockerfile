# Usando a imagem base do Python 3.12
FROM python:3.12

# Definindo o diretório de trabalho dentro do container
WORKDIR /app

# Copiando todos os arquivos para dentro do container
COPY . ./

# Instalando as dependências do projeto
RUN pip3 install -r requirements.txt

# Definindo a variável de ambiente PORT (o Streamlit usará isso)
ENV PORT=8080

# Expondo a porta que o Streamlit vai escutar
EXPOSE 8080

# Definindo o comando para iniciar o Streamlit
CMD ["streamlit", "run", "webapp.py", "--server.port", "8080", "--server.headless", "true"]
