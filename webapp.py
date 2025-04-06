import streamlit as st
from time import sleep
from crud import ler_todos_usuarios
from pagina_gestao import pagina_gestao
from pagina_usuario import pagina_usuario
from pagina_chat import pagina_chat

st.set_page_config(
    page_title="Tô Off",
    page_icon="images/favicon.jpg",  
    initial_sidebar_state="expanded",
    layout="centered",
)

# Função para adicionar JavaScript para ajustar o zoom
def set_zoom():
    st.markdown(
        """
        <script>
        document.body.style.zoom = "80%";
        </script>
        """,
        unsafe_allow_html=True
    )

# Chame a função para ajustar o zoom
set_zoom()

def login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.image("images/logo.png")
    usuarios = ler_todos_usuarios()
    usuarios = {usuario.nome: usuario for usuario in usuarios}
    with st.container(border=True):
        try:
            st.markdown("Bem-vindo à tela de login!")
            nome_usuario = st.text_input("Digite o seu nome")
            senha = st.text_input("Digite sua senha", type="password")

            if st.button("Logar"):
                usuario = usuarios[nome_usuario]

                if usuario.verificar_senha(senha.strip()):
                    st.success("Login efetuado com sucesso!")
                    st.session_state["usuario"] = usuario
                    st.session_state["logado"] = True
                    sleep(1)
                    st.rerun()
                else:
                    st.error("Senha incorreta")
        except KeyError:
            st.error("Algo errado não está correto..")


def pagina_principal():
    usuario = st.session_state["usuario"]

    cols = st.columns(2)
    with cols[0]:
        if st.button("Calendario", use_container_width=True):
            st.session_state["pag_gestao_usuarios"] = False
            st.rerun()
    with cols[1]:
        if st.button("Chat com OA", use_container_width=True):
            st.session_state["pag_gestao_usuarios"] = True
            st.rerun()

    if usuario.acesso_gestor:
        if st.session_state["pag_gestao_usuarios"]:
            pagina_chat()
        else:
            pagina_gestao()

    else:
        if st.session_state["pag_gestao_usuarios"]:
            pagina_chat()
        else:
            pagina_usuario()


def main():
    if "logado" not in st.session_state:
        st.session_state["logado"] = False
    if "pag_gestao_usuarios" not in st.session_state:
        st.session_state["pag_gestao_usuarios"] = False
    if "ultimo_clique" not in st.session_state:
        st.session_state["ultimo_clique"] = ""

    if not st.session_state["logado"]:
        login()
    else:
        pagina_principal()

if __name__ == "__main__":
    main()