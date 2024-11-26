import streamlit as st

from time import sleep

from crud import ler_todos_usuarios
from pagina_gestao import pagina_gestao
from pagina_calendario import pagina_calendario


st.markdown("""
    <style>
        .st-emotion-cache-1dp5vir {
            background-image: linear-gradient(90deg, rgb(255 255 255), rgb(0 255 226));
        }
        [data-testid='stHeaderActionElements'] {
            display: none;
        }
        .sidebar-content {
            transition: width 0.5s;
        }
        .fade-in {
            animation: fadeIn 0.5s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
    <script>
        function ajustarSidebar() {
            var sidebar = document.querySelector('.sidebar-content');
            if (sidebar) {
                sidebar.style.width = '40%';
            }
        }
        function prevenirScroll(event) {
            event.preventDefault();
            ajustarSidebar();
        }
        function aplicarAnimacao() {
            var conteudo = document.querySelector('.main-content');
            if (conteudo) {
                conteudo.classList.add('fade-in');
            }
        }
    </script>
    """, unsafe_allow_html=True)


def login():
    st.title("Bem-vindo ao Tô Off!")
    usuarios = ler_todos_usuarios()
    usuarios = {usuario.nome: usuario for usuario in usuarios}
    with st.container(border=True):
        st.markdown("Bem-vindo à tela de login!")
        nome_usuario = st.text_input("Digite o seu código")
        senha = st.text_input("Digite sua senha", type="password")

        if st.button("Logar"):
            usuario = usuarios[nome_usuario]

            if usuario.verificar_senha(senha):
                st.success("Login efetuado com sucesso!")
                st.session_state["usuario"] = usuario
                st.session_state["logado"] = True
                sleep(1)
                st.rerun()
            else:
                st.error("Senha incorreta")

                
def pagina_principal():
    usuario = st.session_state["usuario"]

    if usuario.acesso_gestor:
        cols = st.columns(2)

        with cols[0]:
            if st.button("Acessar Gestão de Usuários", use_container_width=True):
                st.session_state["pag_gestao_usuarios"] = True
                st.rerun()
        with cols[1]:
            if st.button("Acessar Calendário", use_container_width=True):
                st.session_state["pag_gestao_usuarios"] = False
                st.rerun()

    if st.session_state["pag_gestao_usuarios"]:
        pagina_gestao()
    else:
        pagina_calendario()


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