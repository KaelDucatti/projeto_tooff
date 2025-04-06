import streamlit as st

from time import sleep
from datetime import datetime, timedelta
from pandas import DataFrame
from pagina_calendario import pagina_calendario


from crud import (
    deletar_evento, 
    ler_eventos_usuario, 
    ler_todos_usuarios, 
    criar_evento,
    modificar_evento
)


def tab_gestao_usuario():
    usuarios = ler_todos_usuarios()
    eventos = ler_eventos_usuario()

    (tab_visualizar, tab_deletar_evento, 
     tab_criar_evento, tab_modificar_evento) = st.tabs(["Usuários", "Deletar Eventos", 
                                                        "Criar Eventos", "Alterar Evento"])

    with tab_visualizar:
        data_usuarios = [
            {
                "Nome": usuario.nome,
                "Email": usuario.email,
                "Id": usuario.id,
                "Acesso Gestor": usuario.acesso_gestor,
            }
            for usuario in usuarios
        ]
        st.dataframe(DataFrame(data_usuarios).set_index("Id"), width=600, height=600)

    with tab_deletar_evento:
        usuario_logado = st.session_state["usuario"]
        eventos_usuario = [
            {
                "id": evento.id,
                "Nome": evento.usuario.nome,
                "Tipo": evento.tipo_ausencia,
                "Inicio": evento.data_inicio_evento,
                "Fim": evento.data_fim_evento,
                "Dias": (datetime.strptime(evento.data_fim_evento, "%Y-%m-%d") - datetime.strptime(evento.data_inicio_evento, "%Y-%m-%d")  + timedelta(days=1)).days,
                "Descrição": evento.descricao
            }
            for evento in eventos if evento.id_usuario == usuario_logado.id
        ]
        if eventos_usuario:
            # Ordenar a lista de eventos pelo 'id' em ordem decrescente
            eventos_usuario.sort(key=lambda x: x["id"], reverse=True)

            # Criar o dataframe a partir da lista ordenada
            df_eventos = DataFrame(eventos_usuario).set_index("id")

            # Exibir o dataframe no Streamlit
            st.dataframe(df_eventos, width=800, height=400)

            evento_dict = {evento["id"]: evento for evento in eventos_usuario}
            sorted_evento_dict = dict(sorted(evento_dict.items(), key=lambda item: item[0], reverse=True))

            id_evento = st.selectbox(
                "Digite o Id do evento que deseja deletar", 
                sorted_evento_dict.keys(),
                key="id_evento_deletar_evento_usuario"
            )

            if id_evento:
                evento = evento_dict[id_evento]
                
                if st.button("Deletar", key="deletar_evento_usuario"):
                    deletar_evento(evento["id"])
                    st.success(f'O evento "{id_evento}" foi deletado com sucesso!')
                    sleep(1)
                    st.rerun()
        else:
            st.info("Está tão vazio aqui...")
    
    with tab_criar_evento:
        usuario_logado = st.session_state["usuario"]
        tipo_ausencia = st.selectbox(
            "Tipo de ausência", [
                "Plantão", 
                "Férias", 
                "Assiduidade",
                "Licença (Geral)", 
                "Evento Especial"
            ],
            key="tipo_ausencia_criar_evento_usuario"
        )
        inicio_evento = st.date_input("Data de início do evento", key="inicio_evento_criar_evento_usuario")
        fim_evento = st.date_input("Data de fim do evento", key="fim_evento_criar_evento_usuario")

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

        descricao = st.text_area("Descrição do evento (opcional)", key="descricao_criar_evento_gestor")
        total_dias = (fim_evento - inicio_evento) + timedelta(days=1)

        if tipo_ausencia in ["Férias", "Licença (Geral)", "Evento Especial"]:
            st.info(f"Foram marcados {total_dias.days} dias de {tipo_ausencia}.")

        if fim_evento < inicio_evento:
            st.info(f"Comprou um DeLorean? Tá marcando {tipo_ausencia} indo pro passado ;D")
        
        if st.button("Criar Evento", key="criar_evento_usuario"):
            criar_evento(
                id_usuario=usuario_logado.id,
                inicio_evento=inicio_evento,
                fim_evento=fim_evento,
                tipo_ausencia=tipo_ausencia,
                descricao=descricao,
                turno=turno
            )
            st.success("Evento criado com sucesso!")
            sleep(1)
            st.rerun()

    with tab_modificar_evento:
        usuario_logado = st.session_state["usuario"]
        eventos_usuario = [
            {
                "id": evento.id,
                "Nome": evento.usuario.nome,
                "Tipo": evento.tipo_ausencia,
                "Inicio": evento.data_inicio_evento,
                "Fim": evento.data_fim_evento,
                "Dias": (datetime.strptime(evento.data_fim_evento, "%Y-%m-%d") - datetime.strptime(evento.data_inicio_evento, "%Y-%m-%d") + timedelta(days=1)).days,
                "Descrição": evento.descricao,
                "Turno": evento.turno  # Adicionando o turno ao dicionário
            }
            for evento in eventos if evento.id_usuario == usuario_logado.id
        ]
        if eventos_usuario:
            # Ordenar a lista de eventos pelo 'id' em ordem decrescente
            eventos_usuario.sort(key=lambda x: x["id"], reverse=True)

            # Criar o dataframe a partir da lista ordenada
            df_eventos = DataFrame(eventos_usuario).set_index("id")

            # Exibir o dataframe no Streamlit
            st.dataframe(df_eventos, width=800, height=200)

            evento_dict = {evento["id"]: evento for evento in eventos_usuario}
            sorted_evento_dict = dict(sorted(evento_dict.items(), key=lambda item: item[0], reverse=True))

            id_evento = st.selectbox(
                "Selecione o Id do evento que deseja modificar", 
                sorted_evento_dict.keys(),
                key="id_evento_modificar_evento_usuario"
            )
            evento = evento_dict[id_evento]

            tipo_ausencia = st.selectbox(
                "Tipo de ausência", [
                    "Plantão", 
                    "Férias", 
                    "Assiduidade", 
                    "Licença (Geral)",
                    "Evento Especial"
                ],
                index=["Plantão", "Férias", "Assiduidade", "Licença (Geral)", "Evento Especial"].index(evento["Tipo"]),
                key="tipo_ausencia_modificar_evento_usuario"
            )

            inicio_evento = st.date_input(
                "Data de início do evento",
                value=datetime.strptime(evento["Inicio"], "%Y-%m-%d"), 
                key="inicio_evento_modificar_evento_usuario"
            )

            fim_evento = st.date_input(
                "Data de fim do evento", 
                value=datetime.strptime(evento["Fim"], "%Y-%m-%d"),
                key="fim_evento_modificar_evento_usuario"
            )

            if tipo_ausencia in ["Plantão", "Evento Especial"]: 
                turno = st.selectbox(
                    "Turno", [
                        "Dia",
                        "Noite",
                        "Madrugada"
                    ],
                    index=["Dia", "Noite", "Madrugada"].index(evento["Turno"]),
                    key="turno_ausencia_modificar_evento_usuario"
                )

            descricao = st.text_area(
                "Descrição do evento (opcional)",
                value=evento["Descrição"], 
                key="descricao_modificar_evento_usuario"
            )
            
            total_dias = (fim_evento - inicio_evento) + timedelta(days=1)

            if tipo_ausencia in ["Férias", "Licença (Geral)", "Evento Especial"]:
                st.info(f"Foram marcados {total_dias.days} dias de {tipo_ausencia}.")

            if fim_evento < inicio_evento:
                st.info(f"Comprou um DeLorean? Tá marcando {tipo_ausencia} indo pro passado ;D")

            if st.button("Modificar", key="alterar_evento_usuario"):
                modificar_evento(
                    id=id_evento,
                    id_usuario=usuario_logado.id,
                    data_inicio_evento=inicio_evento.strftime("%Y-%m-%d"),
                    data_fim_evento=fim_evento.strftime("%Y-%m-%d"),
                    tipo_ausencia=tipo_ausencia,
                    descricao=descricao,
                    turno=turno if tipo_ausencia in ["Plantão", "Evento Especial"] else None
                )
                st.success("Modificação executada com sucesso!")
                sleep(1)
                st.rerun()
        else:
            st.info("Nenhum evento encontrado para modificar.")


def pagina_usuario():
    with st.sidebar:
        tab_gestao_usuario()
    pagina_calendario()
