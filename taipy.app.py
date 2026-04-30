import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# 1. Configuración de pantalla completa
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=600000, key="datarefresh")

# 2. Tu Estilo Original (Recuperado)
C_FONDO = "#0E1117"
C_AZUL = "#2b5dda"
C_TITULO = "#87CEEB"
C_NARANJA = "#FFDEAD"

st.markdown(f"""
<style>
    [data-testid="stHeader"], header {{ display: none !important; }}
    .stApp {{ margin-top: -70px !important; background-color: {C_FONDO} !important; }}
    .title-main {{ font-size: 3.1rem; color: {C_TITULO}; font-weight: 700; margin: 0; }}
    .subtitle-sub {{ font-size: 2.2rem; color: #ffffff; margin: 0; }}
    .concepto-texto {{ font-size: 1.8rem; color: {C_NARANJA}; text-align: center; margin-top: -10px; }}
</style>
""", unsafe_allow_html=True)

# 3. Carga de Datos
@st.cache_data(ttl=600)
def cargar_datos():
    return pd.read_excel('Datos_Macroeconomicos.xlsx', sheet_name=None)

dict_hojas = cargar_datos()
ahora = (datetime.utcnow() - timedelta(hours=4)).strftime("%d/%m/%Y %I:%M %p")

# Encabezado
st.markdown(f"""
<div style="display: flex; justify-content: space-between; border-bottom: 2px solid #444; padding-bottom:10px;">
    <div>
        <p class="title-main">UNIDAD ADMINISTRATIVA INTEGRAL DE RIESGO</p>
        <p class="subtitle-sub">Indicadores Macroeconómicos BCV.</p>
    </div>
    <div style="color: {C_NARANJA}; text-align: right;">Última actualización:<br><b>{ahora}</b></div>
</div>
""", unsafe_allow_html=True)

# 4. Gráficos con tu Estilo y Renderizado Directo
col1, col2 = st.columns(2)

with col1:
    df1 = dict_hojas['Tasa Overnight Diaria'].iloc[:, [0, 7]].dropna().tail(7)
    fig1 = go.Figure(go.Scatter(
        x=pd.to_datetime(df1.iloc[:, 0]).dt.strftime('%d/%m'),
        y=df1.iloc[:, 1],
        mode='lines+markers+text',
        text=[f"{v}%" for v in df1.iloc[:, 1]],
        textposition="top center",
        line=dict(color='#60CCC8', width=4),
        textfont=dict(size=20, color="white")
    ))
    fig1.update_layout(title="TASA OVERNIGHT DIARIA BCV", height=350, paper_bgcolor='rgba(0,0,0,0)', 
                      plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
    # El secreto está en render_mode='webgl' para que el TV no sufra
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
    st.markdown('<p class="concepto-texto">TASA PROMEDIO DIARIA APLICADA A PRÉSTAMOS INTERBANCARIOS.</p>', unsafe_allow_html=True)

with col2:
    df2 = dict_hojas['Reservas Bancarias Excedentari'].iloc[:, [0, 1]].dropna().head(7).iloc[::-1]
    fig2 = go.Figure(go.Bar(
        x=pd.to_datetime(df2.iloc[:, 0]).dt.strftime('%d/%m'),
        y=df2.iloc[:, 1]/1000,
        text=[f"{v/1000:,.2f}MM" for v in df2.iloc[:, 1]],
        textposition='outside',
        marker_color=C_AZUL,
        textfont=dict(size=20, color="white")
    ))
    fig2.update_layout(title="RESERVAS BANCARIAS EXCEDENTARIAS BCV", height=350, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
    st.markdown('<p class="concepto-texto">DINERO EXTRA QUE POSEEN LOS BANCOS EN EL BCV.</p>', unsafe_allow_html=True)
