import holidays
import streamlit as st

from json import load
from datetime import datetime
from streamlit_calendar import calendar

from crud import ler_todos_usuarios


def verificar_e_adicionar_evento(inicio_evento, fim_evento, tipo_evento):
    usuario = st.session_state["usuario"]

    total_dias = (
        datetime.strptime(fim_evento, "%Y-%m-%d")
        - datetime.strptime(inicio_evento, "%Y-%m-%d")
    ).days + 1

    dias_a_solicitar = usuario.ferias_a_solicitar()

    if tipo_evento == "Férias":
        if total_dias < 5:
            st.error("Quantidade de dias inferior a 5")
            return
        elif dias_a_solicitar < total_dias:
            st.error(f"Usuário solicitou {total_dias} dias, mas tem apenas {dias_a_solicitar} para solicitar.")
            return
        
    usuario.adicionar_evento(inicio_evento, fim_evento, tipo_evento)
    limpar_datas()


def limpar_datas():
    del st.session_state["data_inicial"]
    del st.session_state["data_final"]


def pagina_calendario():
    customizacao_css = """
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
    
    with open("opcoes_calendario.json") as file:
        opcoes_calendario = load(file)

    usuarios = ler_todos_usuarios()
    eventos_calendario = [
        evento
        for usuario in usuarios
        for evento in usuario.listar_eventos_calendario()
    ]
   
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

    feriados_brasil = holidays.Brazil(years=[2024, 2025])
    eventos_calendario.extend([
        {"title": nome, "start": str(data), "className": "holiday"}
        for data, nome in sorted(feriados_brasil.items())
    ])

    calendario_widget = calendar(
        events=eventos_calendario,
        options=opcoes_calendario,
        custom_css=customizacao_css
    )

    if "callback" in calendario_widget and calendario_widget["callback"] == "dateClick":
        data_base = calendario_widget["dateClick"]["date"]

        if data_base != st.session_state.get("ultimo_clique"):
            st.session_state["ultimo_clique"] = data_base
            data = data_base.split("T")[0]

            if "data_inicial" not in st.session_state:
                st.session_state["data_inicial"] = data
                st.warning(f"Data inicial de férias selecionada: {data}")

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
                        
                            
                        
