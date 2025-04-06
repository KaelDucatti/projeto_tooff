import streamlit as st
from pandas import DataFrame
from datetime import datetime, timedelta, date
from time import sleep

from pagina_calendario import pagina_calendario
from crud import (
    deletar_evento,
    ler_eventos_usuario,
    ler_todos_usuarios,
    criar_usuario,
    modificar_usuario,
    deletar_usuario,
    criar_evento,
    modificar_evento
)

def tab_gestao_usuarios():
    usuarios = ler_todos_usuarios()
    eventos = ler_eventos_usuario()

    (tab_criar_evento, tab_modificar_evento, tab_deletar_evento, tab_criar, tab_modificar, tab_deletar) = (
        st.tabs(
            [
                "Criar Eventos",
                "Alterar Evento",
                "Deletar Eventos",
                "Criar Usuário",
                "Alterar Usuário",
                "Deletar Usuário"
            ]
        )
    )

    # Verifique se eventos_usuario não está vazio e contém a coluna 'id'
    if eventos and "id" not in eventos[0].__dict__:
        st.warning("Nenhum evento encontrado ou a coluna 'id' está ausente.")

    with tab_criar:
        nome = st.text_input("Nome do usuário", key="nome_usuario_criar_usario_gestor")
        email = st.text_input("E-mail do usuário", key="email_usuario_criar_usuario_gestor")
        senha = st.text_input("Senha", key="senha_criar_usuario_gestor")
        acesso_gestor = st.checkbox("Tem acesso de gestor?", value=False, key="acesso_gestor_criar_usuario_gestor")
        # Usando valor padrão como data atual
        inicio_na_empresa = st.date_input("Data de início na empresa", value=date.today(), key="data_inicio_criar_usuario_gestor")
        if st.button("Criar", key="criar_usuario_gestor"):
            criar_usuario(
                nome=nome,
                email=email,
                senha=senha,
                acesso_gestor=acesso_gestor,
                inicio_na_empresa=inicio_na_empresa,
            )
            st.success("Usuário adicionado com sucesso!")
            sleep(1)
            st.rerun()

    with tab_modificar:
        data_usuarios = [
            {
                "Id": usuario.id,
                "Nome": usuario.nome,
                "Email": usuario.email,
                "Acesso Gestor": usuario.acesso_gestor,
            } 
            for usuario in usuarios
        ]
        st.dataframe(DataFrame(data_usuarios).set_index("Id"), width=500, height=200)

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
        
        # Convertendo a string da data para objeto date, se necessário
        if isinstance(usuario.inicio_na_empresa, str):
            try:
                data_inicio = datetime.strptime(usuario.inicio_na_empresa, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                data_inicio = date.today()
        elif isinstance(usuario.inicio_na_empresa, (date, datetime)):
            data_inicio = usuario.inicio_na_empresa.date() if isinstance(usuario.inicio_na_empresa, datetime) else usuario.inicio_na_empresa
        else:
            data_inicio = date.today()
            
        inicio_na_empresa = st.date_input(
            "Data de início do evento", 
            value=data_inicio,
            key="inicio_empresa_modificar_usuario_gestor"
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
        data_usuarios = [
            {
                "Id": usuario.id,
                "Nome": usuario.nome,
                "Email": usuario.email,
                "Acesso Gestor": usuario.acesso_gestor,
            } 
            for usuario in usuarios
        ]
        st.dataframe(DataFrame(data_usuarios).set_index("Id"), width=500, height=300)

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

    with tab_criar_evento:
        usuarios_dict = {usuario.nome: usuario for usuario in usuarios}
        nome_usuario = st.selectbox(
            "Selecione o usuário para criar o evento", 
            usuarios_dict.keys(), 
            key="nome_usuario_criar_evento_gestor"
        )

        usuario = usuarios_dict[nome_usuario]
        tipo_ausencia = st.selectbox(
            "Tipo de ausência", [
                "Plantão", 
                "Férias", 
                "Assiduidade", 
                "Licença (Geral)",
                "Evento Especial"
            ],
            key="tipo_ausencia_criar_evento_gestor"
        )

        inicio_evento = st.date_input(
            "Data de início do evento", 
            value=date.today(),
            key="inicio_evento_criar_evento_gestor"
        )

        fim_evento = st.date_input(
            "Data de fim do evento", 
            value=date.today(),
            key="fim_evento_criar_evento_gestor"
        )

        turno = None
        if tipo_ausencia in ["Plantão", "Evento Especial"]: 
            turno = st.selectbox(
                "Turno", [
                    "Dia",
                    "Noite",
                    "Madrugada"
                ],
                key="turno_ausencia_criar_evento_gestor"
            )

        descricao = st.text_area(
            "Descrição do evento (opcional)", 
            key="descricao_criar_evento_gestor"
        )
        
        total_dias = (fim_evento - inicio_evento) + timedelta(days=1)

        if tipo_ausencia in ["Férias", "Licença (Geral)", "Evento Especial"]:
            st.info(f"Foram marcados {total_dias.days} dias de {tipo_ausencia}.")

        if fim_evento < inicio_evento:
            st.info(f"Comprou um DeLorean? Tá marcando {tipo_ausencia} indo pro passado ;D")

        elif st.button("Criar Evento", key="criar_evento_gestor"):
            criar_evento(
                id_usuario=usuario.id,
                inicio_evento=inicio_evento,
                fim_evento=fim_evento,
                tipo_ausencia=tipo_ausencia,
                descricao=descricao,
                turno=turno
            )
            st.success(f"Evento criado com sucesso para {nome_usuario}!")
            sleep(1)
            st.rerun()

    with tab_deletar_evento:
        eventos_usuario = [
            {
                "id": evento.id,
                "Nome": evento.usuario.nome,
                "Tipo": evento.tipo_ausencia,
                "Inicio": evento.data_inicio_evento,
                "Fim": evento.data_fim_evento,
                "Dias": (datetime.strptime(evento.data_fim_evento, "%Y-%m-%d") - datetime.strptime(evento.data_inicio_evento, "%Y-%m-%d")  + timedelta(days=1)).days
            }
            for evento in eventos
        ]
        # Ordenar a lista de eventos pelo 'id' em ordem decrescente
        eventos_usuario.sort(key=lambda x: x["id"], reverse=True)

        # Criar o dataframe a partir da lista ordenada
        df_eventos = DataFrame(eventos_usuario).set_index("id")

        # Exibir o dataframe no Streamlit
        st.dataframe(df_eventos, width=500, height=300)

        evento_dict = {evento.id: evento for evento in eventos}
        sorted_evento_dict = dict(sorted(evento_dict.items(), key=lambda item: item[0], reverse=True))

        id_evento = st.selectbox(
            "Digite o Id do evento que deseja deletar", 
            sorted_evento_dict.keys(),
            key="id_evento_deletar_evento_gestor"
        )

        if id_evento:
            evento = evento_dict[id_evento]
            if st.button("Deletar", key="deletar_evento_gestor"):
                deletar_evento(evento.id)
                st.success(f'O evento "{id_evento}" foi deletado com sucesso!')
                sleep(1)
                st.rerun()

    with tab_modificar_evento:
        eventos_usuario = [
            {
                "id": evento.id,
                "Nome": evento.usuario.nome,
                "Tipo": evento.tipo_ausencia,
                "Inicio": evento.data_inicio_evento,
                "Fim": evento.data_fim_evento,
                "Dias": (datetime.strptime(evento.data_fim_evento, "%Y-%m-%d") - datetime.strptime(evento.data_inicio_evento, "%Y-%m-%d") + timedelta(days=1)).days
            }
            for evento in eventos
        ]
        # Ordenar a lista de eventos pelo 'id' em ordem decrescente
        eventos_usuario.sort(key=lambda x: x["id"], reverse=True)

        # Criar o dataframe a partir da lista ordenada
        df_eventos = DataFrame(eventos_usuario).set_index("id")

        # Exibir o dataframe no Streamlit
        st.dataframe(df_eventos, width=500, height=200)

        usuarios_dict = {usuario.nome: usuario for usuario in usuarios}

        evento_dict = {evento.id: evento for evento in eventos}
        sorted_evento_dict = dict(sorted(evento_dict.items(), key=lambda item: item[0], reverse=True))

        id_evento = st.selectbox(
            "Selecione o Id do evento que deseja modificar", 
            sorted_evento_dict.keys(),
            key="id_evento_modificar_evento_gestor"
        )
        evento = evento_dict[id_evento]

        nome_usuario = st.selectbox(
            "Selecione o usuário para modificar o evento", 
            usuarios_dict.keys(), 
            index=list(usuarios_dict.keys()).index(evento.usuario.nome),
            key="nome_usuario_modificar_evento_gestor"
        )

        tipo_ausencia = st.selectbox(
            "Tipo de ausência", [
                "Plantão", 
                "Férias", 
                "Assiduidade", 
                "Licença (Geral)",
                "Evento Especial"
            ],
            index=["Plantão", "Férias", "Assiduidade", "Licença (Geral)", "Evento Especial"].index(evento.tipo_ausencia),
            key="tipo_ausencia_modificar_evento_gestor"
        )

        # Convertendo a string da data para objeto date
        data_inicio = datetime.strptime(evento.data_inicio_evento, "%Y-%m-%d").date()
        data_fim = datetime.strptime(evento.data_fim_evento, "%Y-%m-%d").date()

        inicio_evento = st.date_input(
            "Data de início do evento",
            value=data_inicio, 
            key="inicio_evento_modificar_evento_gestor"
        )

        fim_evento = st.date_input(
            "Data de fim do evento", 
            value=data_fim,
            key="fim_evento_modificar_evento_gestor"
        )

        turno = None
        if tipo_ausencia in ["Plantão", "Evento Especial"]: 
            turno = st.selectbox(
                "Turno", [
                    "Dia",
                    "Noite",
                    "Madrugada"
                ],
                index=["Dia", "Noite", "Madrugada"].index(evento.turno) if evento.turno in ["Dia", "Noite", "Madrugada"] else 0,
                key="turno_ausencia_modificar_evento_gestor"
            )

        descricao = st.text_area(
            "Descrição do evento (opcional)",
            value=evento.descricao, 
            key="descricao_modificar_evento_gestor"
        )
        
        total_dias = (fim_evento - inicio_evento) + timedelta(days=1)

        if tipo_ausencia in ["Férias", "Licença (Geral)", "Evento Especial"]:
            st.info(f"Foram marcados {total_dias.days} dias de {tipo_ausencia}.")

        if fim_evento < inicio_evento:
            st.info(f"Comprou um DeLorean? Tá marcando {tipo_ausencia} indo pro passado ;D")

        if st.button("Modificar", key="alterar_evento_gestor"):
            modificar_evento(
                id=id_evento,
                id_usuario=usuarios_dict[nome_usuario].id,
                data_inicio_evento=inicio_evento.strftime("%Y-%m-%d"),
                data_fim_evento=fim_evento.strftime("%Y-%m-%d"),
                tipo_ausencia=tipo_ausencia,
                descricao=descricao,
                turno=turno if tipo_ausencia in ["Plantão", "Evento Especial"] else None
            )
            st.success("Modificação executada com sucesso!")
            sleep(1)
            st.rerun()


def pagina_gestao():
    with st.sidebar:
        tab_gestao_usuarios()
    pagina_calendario()