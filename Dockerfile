# Use uma imagem base oficial do Python
FROM python:3.12-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas os arquivos necessários para instalar as dependências primeiro
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Exponha a porta que o Streamlit vai rodar (padrão é 8501, mas ajustamos para 8080 conforme sua configuração)
EXPOSE 8501

# Configura o healthcheck para a Google Cloud Run
HEALTHCHECK --interval=30s --timeout=3s CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Define o comando para iniciar o Streamlit
CMD ["streamlit", "run", "webapp.py", "--server.port=8501", "--server.address=0.0.0.0"]
