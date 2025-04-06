from typing import List, Optional
from pathlib import Path
from datetime import datetime, timedelta, date
import streamlit as st

from ldap3 import Server, Connection, ALL
from sqlalchemy import create_engine, String, Boolean, Integer, select, ForeignKey, Enum
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped, Session, relationship


# Define o caminho para o diretório atual do Script #
pasta_atual = Path(__file__).parent

# Define o caminho para o arquivo do banco de dados #
PATH_TO_BD = pasta_atual / "bd_usuarios.sqlite"

# Cria o diretório se não existir
PATH_TO_BD.parent.mkdir(parents=True, exist_ok=True)

# Verifique o caminho do arquivo
print(f"Caminho do banco de dados: {PATH_TO_BD}")

# Verifique se o arquivo existe
if not PATH_TO_BD.exists():
    print("Arquivo de banco de dados não encontrado. Será criado um novo arquivo.")
else:
    print("Arquivo de banco de dados encontrado.")

# Criando a engine do SQLAlchemy para se conectar ao banco de dados #
engine = create_engine(f"sqlite:///{PATH_TO_BD}")


# ============================ T A B E L A S ============================= #
# Definição da Classe Base declarativa do SQLAlchemy #
class Base(DeclarativeBase):
    pass


# Tabela de Usuários #
class Usuario(Base):
    TIPO_AUSENCIA_CORES = {
        "Férias": "red",
        "Assiduidade": "grey",
        "Plantão": "orange",
        "Licença Maternidade/Paternidade": "purple",
        "Evento Especial": "darkblue"
    }

    __tablename__ = "tabela_usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80))
    cod_funcional: Mapped[str] = mapped_column(String(8))
    email: Mapped[str] = mapped_column(String(60))
    acesso_gestor: Mapped[bool] = mapped_column(Boolean(), default=False)
    inicio_na_empresa: Mapped[str] = mapped_column(String(30))

    eventos_ausencias: Mapped[List["Eventos"]] = relationship(
        "Eventos", back_populates="usuario", lazy="subquery"
    )

    def __repr__(self):
        return f"Usuario({self.id!r}, {self.cod_funcional!r})"

    def verificar_senha(self, cod_funcional, senha):
        ldap_servidor = "ldap://mz-vv-dc-004.corp.bradesco.com.br:389"
        ldap_funcional_usuario = f"corp\\{cod_funcional}"
        ldap_senha = senha

        servidor = Server(ldap_servidor, get_info=ALL)
        conexao = Connection(servidor, user=ldap_funcional_usuario, password=ldap_senha)

        if conexao.bind():
            print("Conectado!")
            return True
        else:
            print("Credenciais inválidas!")
            return False

    def listar_eventos_calendario(self):
        return [
            {
                "title": f"{evento.tipo_ausencia} - {self.nome}",
                "start": evento.data_inicio_evento,
                "end": (
                    date.fromisoformat(evento.data_fim_evento) + timedelta(days=1)
                ).isoformat(),
                "resourceId": self.id,
                "color": self.TIPO_AUSENCIA_CORES.get(evento.tipo_ausencia, "grey"),
                "extendedProps": {
                    "description": evento.descricao,
                    "shift": evento.turno,
                    "event_id": evento.id
                }
            }
            for evento in self.eventos_ausencias
        ]

    def ferias_tiradas(self):
        dia_atual = datetime.now()
        inicio_na_empresa = datetime.strptime(self.inicio_na_empresa, "%Y-%m-%d")
        
        # Verifica se o funcionário completou 1 ano na empresa
        if (dia_atual - inicio_na_empresa).days < 365:
            return 0  

        dias_tirados_no_ano_atual = 0
        for evento in self.eventos_ausencias:
            if evento.tipo_ausencia == "Férias":
                data_inicio_evento = datetime.strptime(evento.data_inicio_evento, "%Y-%m-%d")
                if data_inicio_evento.year == dia_atual.year:
                    dias_tirados_no_ano_atual += evento.total_dias
        
        return dias_tirados_no_ano_atual

    def verificar_periodo_sem_ferias(self):
        dia_atual = datetime.now()
        ultimo_periodo_de_ferias = max(
            (
                datetime.strptime(evento.data_fim_evento, "%Y-%m-%d")
                for evento in self.eventos_ausencias
            ),
            default=datetime.strptime(self.inicio_na_empresa, "%Y-%m-%d"),
        )
        if (dia_atual - ultimo_periodo_de_ferias).days > 10 * 30:
            st.html(
                """
            <p style="font-size:13px; 
                background-color:#ffcccb; 
                padding:3px; 
                border-radius:5px;
                margin:0;
                display: inline-block;">
                O usuário está a mais de 10 meses sem tirar férias!
            </p>
            """
            )


# Tabela de Eventos #
class Eventos(Base):
    __tablename__ = "tabela_eventos"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("tabela_usuario.id"))
    usuario: Mapped["Usuario"] = relationship(lazy="subquery")
    data_inicio_evento: Mapped[str] = mapped_column(String(30))
    data_fim_evento: Mapped[str] = mapped_column(String(30))
    total_dias: Mapped[int] = mapped_column(Integer())
    descricao: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    turno: Mapped[Optional[str]] = mapped_column(
        Enum(
            "Dia",
            "Noite",
            "Madrugada",
            name="turno_evento",
        ),
        nullable=True
    )
    tipo_ausencia: Mapped[str] = mapped_column(
        Enum(
            "Férias",
            "Assiduidade",
            "Plantão",
            "Licença (Geral)",
            "Evento Especial",
            name="tipo_ausencia",
        ),
        nullable=False,
    )


# Criando as tabelas definidas nas subclasses de Base no banco de dados #
Base.metadata.create_all(bind=engine)


# =============================== C R U D =============================== #
def criar_usuario(nome, cod_funcional, email, inicio_na_empresa, **kwargs):
    with Session(bind=engine) as session:
        usuario = Usuario(
            nome=nome,
            cod_funcional=cod_funcional.strip().lower(),
            email=email,
            inicio_na_empresa=inicio_na_empresa,
            **kwargs,
        )
        session.add(usuario)
        session.commit()


def ler_todos_usuarios():
    with Session(bind=engine) as session:
        comando_sql = select(Usuario)
        usuarios = session.execute(comando_sql).fetchall()
        usuarios = [usuario[0] for usuario in usuarios]
        return usuarios


def ler_usuario_por_id(id):
    with Session(bind=engine) as session:
        comando_sql = select(Usuario).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        return usuarios[0][0]


def modificar_usuario(id, **kwargs):
    with Session(bind=engine) as session:
        comando_sql = select(Usuario).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        for usuario in usuarios:
            for key, value in kwargs.items():
                setattr(usuario[0], key, value)
        session.commit()


def deletar_usuario(id):
    with Session(bind=engine) as session:
        comando_sql = select(Usuario).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        for usuario in usuarios:
            session.delete(usuario[0])
        session.commit()


def ler_eventos_usuario():
    with Session(bind=engine) as session:
        comando_sql = select(Eventos)
        eventos = session.execute(comando_sql).fetchall()
        eventos = [evento[0] for evento in eventos]
        return eventos


def deletar_evento(id):
    with Session(bind=engine) as session:
        comando_sql = select(Eventos).filter_by(id=id)
        usuarios = session.execute(comando_sql).fetchall()
        for usuario in usuarios:
            session.delete(usuario[0])
        session.commit()


def criar_evento(id_usuario, inicio_evento, fim_evento, tipo_ausencia, descricao=None, turno=None):
    total_dias = (fim_evento - inicio_evento).days + 1

    with Session(bind=engine) as session:
        evento = Eventos(
            id_usuario=id_usuario,
            data_inicio_evento=inicio_evento,
            data_fim_evento=fim_evento,
            total_dias=total_dias,
            tipo_ausencia=tipo_ausencia,
            descricao=descricao,
            turno=turno
        )
        session.add(evento)
        session.commit()
        

def modificar_evento(id, **kwargs):
    with Session(bind=engine) as session:
        comando_sql = select(Eventos).filter_by(id=id)
        eventos = session.execute(comando_sql).fetchall()
        for evento in eventos:
            for key, value in kwargs.items():
                setattr(evento[0], key, value)
        session.commit()
