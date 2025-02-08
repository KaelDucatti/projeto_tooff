import holidays
import streamlit as st

from json import load
from datetime import datetime
from itertools import chain
from streamlit_calendar import calendar

from crud import ler_todos_usuarios


def verificar_e_adicionar_evento(inicio_evento, fim_evento, tipo_evento):
    usuario = st.session_state["usuario"]

    total_dias = (
        datetime.strptime(fim_evento, "%Y-%m-%d")
        - datetime.strptime(inicio_evento, "%Y-%m-%d")
    ).days + 1

    ferias_tiradas = usuario.ferias_tiradas()

    if tipo_evento == "Férias":
        if total_dias < 10:
            st.error("Quantidade de dias inferior a 10")
            return
        
        elif total_dias > (30 - ferias_tiradas):
            st.error(f"Usuário solicitou {total_dias} dias, mas tem apenas {30 - ferias_tiradas} para solicitar.")
            return
        
    usuario.adicionar_evento(inicio_evento, fim_evento, tipo_evento)
    limpar_datas()


def limpar_datas():
    del st.session_state["data_inicial"]

    if "data_final" in st.session_state:
        del st.session_state["data_final"]


CUSTOM_CSS = """
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 1.5rem;
    }
    .holiday {
        background-color: darkyellow !important; 
        color: white !important; 
        border: 3px solid lightblue;
    }
"""

# Carregar opções do calendário uma única vez
with open("opcoes_calendario.json") as file:
    OPCOES_CALENDARIO = load(file)

# Pré-calcular feriados
FERIADOS_BRASIL = holidays.Brazil(years=[2024, 2025])

def pagina_calendario():
    # Ler todos os usuários
    usuarios = ler_todos_usuarios()

    # Gerar eventos do calendário usando itertools.chain para evitar listas intermediárias
    eventos_calendario = list(chain.from_iterable(
        usuario.listar_eventos_calendario() for usuario in usuarios
    ))

    # Adicionar feriados ao calendário
    eventos_calendario.extend(
        {"title": nome, "start": str(data), "className": "holiday"}
        for data, nome in FERIADOS_BRASIL.items()
    )

    # Selecionar tipo de ausência
    usuario = st.session_state.get("usuario")
    with st.container(border=True):
        tipo_ausencia_selecionado = st.selectbox(
            "*Tipo de Evento*",
            options=[
                "Férias",
                "Assiduidade",
                "Plantão",
                "Licença Maternidade/Paternidade",
            ],
        )

    # Exibir o calendário
    calendario_widget = calendar(
        events=eventos_calendario,
        options=OPCOES_CALENDARIO,
        custom_css=CUSTOM_CSS
    )

    if "callback" in calendario_widget and calendario_widget["callback"] == "dateClick":
        data_base = calendario_widget["dateClick"]["date"]

        if data_base != st.session_state.get("ultimo_clique"):
            st.session_state["ultimo_clique"] = data_base
            data = data_base.split("T")[0]

            if "data_inicial" not in st.session_state:
                st.session_state["data_inicial"] = data

                cols = st.columns([0.7, 0.3])
                with cols[0]:
                    st.warning(f"Data inicial de férias selecionada: {data}")
                with cols[1]:
                    st.button("Limpar", use_container_width=True, on_click=limpar_datas)

            else:
                st.session_state["data_final"] = data
                data_inicial = st.session_state["data_inicial"]

                cols = st.columns([0.7, 0.3])
                with cols[0]:
                    st.warning(f"Data inicial de férias selecionada: {data_inicial}")
                with cols[1]:
                    st.button("Limpar", use_container_width=True, on_click=limpar_datas)

                cols = st.columns([0.7, 0.3])
                with cols[0]:
                    st.warning(f"Data final de férias selecionada: {data}")
                with cols[1]:
                    st.button(
                        "Adicionar Evento", 
                        use_container_width=True,
                        on_click=verificar_e_adicionar_evento,
                        args=(data_inicial, data, tipo_ausencia_selecionado)
                        )
                        
                            
                        
