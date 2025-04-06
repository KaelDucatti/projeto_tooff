from sqlalchemy import create_engine
import sqlite3
from pathlib import Path

# Define o caminho para o arquivo do banco de dados
pasta_atual = Path(__file__).parent
PATH_TO_BD = pasta_atual / "bd_usuarios.sqlite"

# Verifique o caminho do arquivo
print(f"Caminho do banco de dados: {PATH_TO_BD}")

# Verifique se o arquivo existe
if not PATH_TO_BD.exists():
    print("Arquivo de banco de dados não encontrado. Será criado um novo arquivo.")
else:
    print("Arquivo de banco de dados encontrado.")

# Criando a engine do SQLAlchemy para se conectar ao banco de dados
engine = create_engine(f"sqlite:///{PATH_TO_BD}")

# Conectar ao banco de dados SQLite diretamente
conn = sqlite3.connect(PATH_TO_BD)
cursor = conn.cursor()

# Atualizar o campo 'acesso_gestor' para true (1) para o usuário com id = 10
try:
    cursor.execute('UPDATE tabela_usuario SET acesso_gestor = 1 WHERE id = 1')
    print("Campo 'acesso_gestor' atualizado com sucesso para o usuário com id = 1.")
except sqlite3.OperationalError as e:
    print(f"Erro ao atualizar o campo 'acesso_gestor': {e}")

# Confirmar as alterações e fechar a conexão
conn.commit()
conn.close()