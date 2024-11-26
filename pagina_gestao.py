import streamlit as st

from pandas import DataFrame

from crud import (deletar_evento, 
                  ler_eventos_usuario, 
                  ler_todos_usuarios, 
                  criar_usuario, 
                  modificar_usuario,  
                  deletar_usuario)


def tab_gestao_usuarios():
    usuarios = ler_todos_usuarios()
    eventos = ler_eventos_usuario()

    (tab_visualizar, tab_criar, tab_modificar, tab_deletar, tab_deletar_evento) = (
        st.tabs(["Usuários", "Criar Usuário", "Alterar Usuário", "Excluir Usuário", "Excluir Evento"])
    )

    # Verifique o conteúdo de eventos_usuario
    print("Eventos do usuário:", eventos)
    
    # Verifique se eventos_usuario não está vazio e contém a coluna 'id'
    if eventos and 'id' not in eventos[0].__dict__:
        st.warning("Nenhum evento encontrado ou a coluna 'id' está ausente.")

    with tab_visualizar:
        data_usuarios = [
            {
                "nome": usuario.nome,
                "email": usuario.email,
                "acesso_gestor": usuario.acesso_gestor,
                "inicio_na_empresa": usuario.inicio_na_empresa,
            }
            for usuario in usuarios
        ]
        st.dataframe(DataFrame(data_usuarios).set_index("email"))
        
    with tab_criar:
        nome = st.text_input("Nome do usuário")
        email = st.text_input("E-mail do usuário")
        senha = st.text_input("Senha do usuário")
        acesso_gestor = st.checkbox("Tem acesso de gestor?", value=False)
        inicio_na_empresa = st.text_input("Data de início na empresa (AAAA-MM-DD)")
        if st.button("Criar"):
            criar_usuario(
                nome=nome,
                email=email,
                senha=senha,
                acesso_gestor=acesso_gestor,
                inicio_na_empresa=inicio_na_empresa,
            )
            st.rerun()

    with tab_modificar:
        usuarios_dict = {usuario.nome: usuario for usuario in usuarios}
        nome_usuario = st.selectbox(
            "Selecione o usuário para modificar", usuarios_dict.keys()
        )
        usuario = usuarios_dict[nome_usuario]

        nome = st.text_input("Nome do usuário", value=usuario.nome)
        email = st.text_input("E-mail do usário", value=usuario.email)
        senha = st.text_input("Senha do usuário", value="xxxxx")
        acesso_gestor = st.checkbox(
            "Modificar acesso de gestor?", value=usuario.acesso_gestor
        )
        inicio_na_empresa = st.text_input(
            "Data de início na emprese (AAAA-MM-DD)", value=usuario.inicio_na_empresa
        )

        if st.button("Modificar"):
            if senha == "xxxxx":
                modificar_usuario(
                    id=usuario.id,
                    nome=nome,
                    email=email,
                    acesso_gestor=acesso_gestor,
                    inicio_na_empresa=inicio_na_empresa,
                )
            else:
                modificar_usuario(
                    id=usuario.id,
                    nome=nome,
                    email=email,
                    senha=senha,
                    acesso_gestor=acesso_gestor,
                    inicio_na_empresa=inicio_na_empresa,
                )
            st.rerun()

    with tab_deletar:
        usuarios_dict = {usuario.nome: usuario for usuario in usuarios}
        nome_usuario = st.selectbox(
            "Selecione o usuário para deletar", usuarios_dict.keys()
        )

        if nome_usuario:
            usuario = usuarios_dict[nome_usuario]
            confirmacao = st.text_input(
                f'Digite "{nome_usuario}" no campo abaixo para deletar'
            )

            if confirmacao == str(nome_usuario):
                if st.button("Tem certeza?"):
                    deletar_usuario(usuario.id)
                    st.success(f"{nome_usuario} foi deletado com sucesso!")
                    st.rerun()

    with tab_deletar_evento:
        eventos_usuario = [
            {
                "id": evento.id,
                "id do usuário": evento.id_usuario,
                "data de inicio": evento.data_inicio_evento,
                "data de fim": evento.data_fim_evento,
            }
            for evento in eventos
        ]
        st.dataframe(DataFrame(eventos_usuario).set_index("id"))

        evento_dict = {evento.id: evento for evento in eventos}
        id_evento = st.selectbox(
            "Digite o Id do evento que deseja deletar", evento_dict.keys()
        )

        if id_evento:
            evento = evento_dict[id_evento]
            confirmacao = st.text_input(
                f'Digite "{id_evento}" no campo abaixo para deletar o evento'
            )

            if confirmacao == str(id_evento) and st.button("Tem certeza?"):
                deletar_evento(evento.id)
                st.success(f'O evento "{id_evento}" foi deletado com sucesso!')
                st.rerun()


def pagina_gestao():
    with st.sidebar:
        tab_gestao_usuarios()
    
    usuarios = ler_todos_usuarios()

    for usuario in usuarios:
        with st.container(border=True):
            cols = st.columns(2)
            with cols[0]:
                st.markdown(f"### {usuario.nome}")
            with cols[1]:
                ferias_a_solicitar = usuario.ferias_a_solicitar()
                st.markdown(f"##### Dias de férias a solicitar: {ferias_a_solicitar}")
