from typing import List
from pathlib import Path
from datetime import datetime, timedelta, date
import streamlit as st
from sqlalchemy import create_engine, String, Boolean, Integer, select, ForeignKey, Enum
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped, Session, relationship
from werkzeug.security import generate_password_hash, check_password_hash



# Define o caminho para o diretório atual do Script
pasta_atual = Path(__file__).parent

# Define o caminho para o arquivo do banco de dados
PATH_TO_BD = pasta_atual / "bd_usuarios.sqlite"

# Cria o diretório se não existir
PATH_TO_BD.parent.mkdir(parents=True, exist_ok=True)

# Criando a engine do SQLAlchemy para se conectar ao banco de dados
engine = create_engine(f"sqlite:///{PATH_TO_BD}")


# ============================ T A B E L A S ============================= #
# Definição da Classe Base declarativa do SQLAlchemy
class Base(DeclarativeBase):
    pass


# Tabela de Usuários
class Usuario(Base):
    TIPO_AUSENCIA_CORES = {
        "Férias": "green",
        "Assiduidade": "red",
        "Plantão": "brown",
        "Licença Maternidade/Paternidade": "purple"
    }

    __tablename__ = "tabela_usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80))
    senha: Mapped[str] = mapped_column(String(128))
    email: Mapped[str] = mapped_column(String(60))
    acesso_gestor: Mapped[bool] = mapped_column(Boolean(), default=False)
    inicio_na_empresa: Mapped[str] = mapped_column(String(30))
    eventos_ausencias: Mapped[List["Eventos"]] = relationship(
        "Eventos", back_populates="usuario", lazy="subquery"
    )

    def _repr_(self):
        return f"Usuario(id={self.id}, nome={self.nome})"

    def definir_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha, senha)

    def listar_eventos_calendario(self):
        return [
            {
                "title": f"{evento.tipo_ausencia}: {self.nome}",
                "start": evento.data_inicio_evento,
                "end": (
                    date.fromisoformat(evento.data_fim_evento) + timedelta(days=1)
                ).isoformat(),
                "resourceId": self.id,
                "color": self.TIPO_AUSENCIA_CORES.get(evento.tipo_ausencia, "grey")
            }
            for evento in self.eventos_ausencias
        ]

    def adicionar_evento(self, inicio_evento, fim_evento, tipo_ausencia):
        data_inicio = datetime.strptime(inicio_evento, "%Y-%m-%d")
        data_fim = datetime.strptime(fim_evento, "%Y-%m-%d")

        total_dias = (data_fim - data_inicio).days + 1

        with Session(bind=engine) as session:
            ausencias = Eventos(
                id_usuario=self.id,
                data_inicio_evento=inicio_evento,
                data_fim_evento=fim_evento,
                total_dias=total_dias,
                tipo_ausencia=tipo_ausencia
            )
            session.add(ausencias)
            session.commit()

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
                if evento.tipo_ausencia == "Férias"
            ),
            default=datetime.strptime(self.inicio_na_empresa, "%Y-%m-%d")
        )

        if (dia_atual - ultimo_periodo_de_ferias).days > 10 * 30:
            st.html("""
            <p style="font-size:13px; 
                background-color:#ffcccb; 
                padding:3px; 
                border-radius:5px;
                margin:0;
                display: inline-block;">
                O usuário está a mais de 10 meses sem tirar férias!
            </p>
            """)


# Tabela de Eventos
class Eventos(Base):
    __tablename__ = "tabela_eventos"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("tabela_usuario.id"))
    usuario: Mapped["Usuario"] = relationship(lazy="subquery")
    data_inicio_evento: Mapped[str] = mapped_column(String(30))
    data_fim_evento: Mapped[str] = mapped_column(String(30))
    total_dias: Mapped[int] = mapped_column(Integer())
    tipo_ausencia: Mapped[str] = mapped_column(Enum("Férias", "Assiduidade", "Plantão", "Licença Maternidade/Paternidade", name="tipo_ausencia"), nullable=False)

# Criando as tabelas definidas nas subclasses de Base no banco de dados
Base.metadata.create_all(bind=engine)


# =============================== C R U D =============================== #
def criar_usuario(nome, senha, email, inicio_na_empresa, **kwargs):
    with Session(bind=engine) as session:
        usuario = Usuario(nome=nome, email=email, senha=senha, inicio_na_empresa=inicio_na_empresa, **kwargs)
        usuario.definir_senha(senha)
        session.add(usuario)
        session.commit()


def ler_todos_usuarios():
    with Session(bind=engine) as session:
        comando_sql = select(Usuario)
        usuarios = session.scalars(comando_sql).all()
        return usuarios


def ler_usuario_por_id(id):
    with Session(bind=engine) as session:
        usuario = session.get(Usuario, id)
        return usuario


def modificar_usuario(id, **kwargs):
    with Session(bind=engine) as session:
        usuario = session.get(Usuario, id)
        if usuario:
            for key, value in kwargs.items():
                if key == "senha":
                    usuario.definir_senha(value)
                else:
                    setattr(usuario, key, value)
            session.commit()


def deletar_usuario(id):
    with Session(bind=engine) as session:
        usuario = session.get(Usuario, id)
        if usuario:
            session.delete(usuario)
            session.commit()


def ler_eventos_usuario():
    with Session(bind=engine) as session:
        comando_sql = select(Eventos)
        eventos = session.scalars(comando_sql).all()
        return eventos


def deletar_evento(id):
    with Session(bind=engine) as session:
        evento = session.get(Eventos, id)
        if evento:
            session.delete(evento)
            session.commit()

if __name__ == "__main__":
    criar_usuario(
        nome="Gestor",
        email="gestor@gmail.com",
        senha="gestor",
        inicio_na_empresa="2022-02-01",
        acesso_gestor=True
    )
