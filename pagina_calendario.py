import holidays
import streamlit as st
import json
from datetime import datetime, timedelta

from streamlit_calendar import calendar
from crud import ler_todos_usuarios


def scroll_to_element():
    st.markdown(
        """
        <script>
        function scrollToElement() {
            document.querySelector('a[href="#detalhes-do-evento"]').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        scrollToElement();
        </script>
        """,
        unsafe_allow_html=True
    )


# Função para renderizar a página do calendário no Streamlit
def pagina_calendario():
    # CSS customizado para o calendário
    customizacao_css = """
    .fc-event-past {
        opacity: 0.5;
    }
    .fc-event-title {
        font-weight: 700;
        overflow: hidden;
        white-space: nowrap;
        display: inline-block;
        position: absolute;
        width: 100%;
    }
    .fc-daygrid-event {
        position: relative;
        overflow: hidden;
        height: 1.6em;
        cursor: pointer;
    }
    .sidebar .sidebar-content {
        width: 35%; /* Defina a largura desejada em porcentagem */
    }
    """
    # Carrega as opções do calendário
    with open("opcoes_calendario.json") as file:
        opcoes_calendario = json.load(file)

    # Obtém e processa os eventos
    usuarios = ler_todos_usuarios()
    eventos_calendario = []
    eventos_agrupados = {}

    for usuario in usuarios:
        for evento in usuario.listar_eventos_calendario():
            # A chave de agrupamento utiliza o período e o tipo de evento (primeira parte do título)
            key = (evento["start"], evento["end"], evento["title"].split("-")[0])
            if key not in eventos_agrupados:
                eventos_agrupados[key] = evento
            else:
                # Caso já exista, adiciona o nome do usuário (parte após o "-") ao título
                eventos_agrupados[key]["title"] += f", {evento['title'].split('- ')[1]}"

    # Modifica o título dos eventos do tipo "Plantão"
    for evento in eventos_agrupados.values():
        if evento["title"].split(" - ")[0] == "Plantão":
            evento["title"] = "Plantão"

    eventos_calendario = list(eventos_agrupados.values())

    # Adiciona feriados
    feriados_brasil = holidays.Brazil(years=[2024, 2025, 2026])
    eventos_calendario.extend(
        [
            {"title": nome, "start": str(data), "className": "holiday"}
            for data, nome in sorted(feriados_brasil.items())
        ]
    )

    with st.container(border=True):
        tipo_ausencia_selecionado = st.selectbox(
            "**Filtrar Eventos**",
            options=[
                "Todos",
                "Férias",
                "Plantão",
                "Assiduidade",
                "Licença",
                "Evento Especial",
            ],
        )

    # Filtra os eventos com base na seleção do usuário
    if tipo_ausencia_selecionado != "Todos":
        eventos_filtrados = [
            evento
            for evento in eventos_calendario
            if tipo_ausencia_selecionado in evento["title"]
        ]
    else:
        eventos_filtrados = eventos_calendario

    # Renderiza o calendário
    calendario_widget = calendar(
        events=eventos_filtrados,
        options=opcoes_calendario,
        custom_css=customizacao_css,
    )

    # Seu código existente
    if "callback" in calendario_widget:
        if calendario_widget["callback"] == "eventClick":
            evento_clicado = calendario_widget["eventClick"]["event"]
            st.session_state["evento_selecionado"] = evento_clicado

    # Exibe o evento selecionado em um cartão
    if "evento_selecionado" in st.session_state:
        evento = st.session_state["evento_selecionado"]

        with st.container(border=True):
            try:
                dt_fim = datetime.strptime(evento.get('end'), "%Y-%m-%d")
                dt_inicio = datetime.strptime(evento.get('start'), "%Y-%m-%d")
                total_dias = (dt_fim - dt_inicio).days
                dt_fim = dt_fim - timedelta(days=1)

                st.markdown("### Detalhes do Evento")

                st.markdown(f"##### ID do evento: `{evento.get('extendedProps').get('event_id')}`")

                if evento["title"].split(" - ")[0] not in ["Plantão", "Evento Especial"]:
                    st.markdown(f"##### **Título:** `{evento.get('title', 'Sem título')}`")

                st.markdown(
                    f"##### **Período:** `{datetime.strftime(dt_inicio, '%Y-%m-%d')}` -> "
                    f"`{datetime.strftime(dt_fim, '%Y-%m-%d')}`"
                )
                st.markdown(
                    "##### **Total de dias:** "
                    f"`{total_dias}`"
                )

                # Agrupamento das informações de turno:
                # Utiliza os dados do evento clicado para identificar os eventos correspondentes
                clicked_start = evento.get("start")
                clicked_end = evento.get("end")
                clicked_tipo = evento.get("title").split(" - ")[0]

                turnos_dict = {}
                # Percorre todos os usuários e seus eventos para agrupar por turno
                for usuario in usuarios:
                    for ev in usuario.listar_eventos_calendario():
                        if (
                            ev.get("start") == clicked_start and
                            ev.get("end") == clicked_end and
                            ev.get("title").split(" - ")[0] == clicked_tipo
                        ):
                            shift = ev.get("extendedProps", {}).get("shift")
                            if shift:
                                # Extrai o nome do usuário (parte após o "-")
                                parts = ev["title"].split(" - ")
                                nome = parts[1].strip() if len(parts) > 1 else "Desconhecido"
                                if shift in turnos_dict:
                                    if nome not in turnos_dict[shift]:
                                        turnos_dict[shift].append(nome)
                                else:
                                    turnos_dict[shift] = [nome]

                # Define a ordem dos turnos
                ordem_turnos = ["Dia", "Noite", "Madrugada"]

                # Exibe os turnos agrupados se houver informações
                if turnos_dict:
                    st.markdown("##### **Turnos:**")
                    for turno in ordem_turnos:
                        if turno in turnos_dict:
                            st.markdown(f"######  - {turno}: `{', '.join(turnos_dict[turno])}`")

                # Exibe a descrição do evento, se houver
                descricao = evento.get('extendedProps', {}).get('description')
                if descricao:
                    descricao_formatada = descricao.replace('\n', '<br>')
                    st.markdown("**Descrição:**")
                    st.markdown(f"""
                        <div style="
                            padding: 10px;
                            border: 1px solid #ddd;
                            max-height: 150px;
                            overflow-y: auto;">
                            {descricao_formatada}
                        </div>
                    """, unsafe_allow_html=True)

            except TypeError:
                st.markdown("### Detalhes do Evento")
                st.markdown(f"**Título:** {evento.get('title', 'Sem título')}")

        scroll_to_element()
        
        # Limpa o estado após exibir
        del st.session_state["evento_selecionado"]
    
    # Adiciona o botão de "Sair"
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()
    