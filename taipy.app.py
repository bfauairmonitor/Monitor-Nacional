import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64
from pathlib import Path
from datetime import datetime, timedelta

# =========================================
# 1. VARIABLES GLOBALES
# ==========================================
REFRESH_INT = 600000
C_FONDO = "#0E1117"
C_AZUL = "#2b5dda"
C_TITULO = "#87CEEB"
C_NARANJA = "#FFDEAD"
C_BLANCO = "#FFFFFF"
ALT_SUP = 300 
ALT_INF = 300

# ==========================================
# 2. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard Administrativo de Riesgo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Refresco optimizado
st_autorefresh(interval=REFRESH_INT, key="datarefresh")

# ==========================================
# 3. ESTILOS CSS (AJUSTADOS PARA TV)
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

/* Forzamos al navegador a usar aceleración de video */
* {{ 
    -webkit-transform: translate3d(0,0,0); 
    transform: translate3d(0,0,0);
}}

[data-testid="stHeader"], header {{ display: none !important; }}
.stApp {{ 
    margin-top: -70px !important; 
    background-color: {C_FONDO} !important; 
}}

/* Quitamos el 'hidden' para evitar que el navegador del TV corte el contenido */
html, body, .main {{ 
    font-family: 'Roboto', sans-serif; 
    background-color: {C_FONDO} !important;
    color: white;
}}

.header-container {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 5px; border-bottom: 2px solid #444; margin-bottom: 20px;
}}

.title-main {{ font-size: 2.5rem; margin: 0; color: {C_TITULO}; font-weight: 700; }}
.subtitle-sub {{ font-size: 1.8rem; color: #ffffff; margin: 0; }}
.update-text {{ font-size: 1rem; color: {C_NARANJA}; text-align: right; }}

.concepto-texto {{
    font-size: 1.4rem;
    color: {C_NARANJA};
    text-align: center;
    margin-top: -5px;
    font-weight: 400;
    line-height: 1.2;
}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. LÓGICA DE DATOS
# ==========================================
@st.cache_data(ttl=600, show_spinner=False)
def cargar_datos_excel(ruta):
    return pd.read_excel(ruta, sheet_name=None, engine='openpyxl')

try:
    dict_hojas = cargar_datos_excel('Datos_Macroeconomicos.xlsx')
except:
    dict_hojas = {}

ahora = (datetime.utcnow() - timedelta(hours=4)).strftime("%d/%m/%Y %I:%M %p")

st.markdown(f"""
<div class="header-container">
    <div>
        <p class="title-main">UNIDAD ADMINISTRATIVA INTEGRAL DE RIESGO</p>
        <p class="subtitle-sub">Indicadores Macroeconómicos BCV.</p>
    </div>
    <div class="update-text">Última actualización:<br><b>{ahora}</b></div>
</div>
""", unsafe_allow_html=True)

# CONFIGURACIÓN DE GRÁFICOS PARA TV (Estáticos para ahorrar RAM)
config_tv = {'displayModeBar': False, 'staticPlot': False}

# ==========================================
# 5. FILA SUPERIOR
# =========================================
col_sup_izq, col_sup_der = st.columns(2)

with col_sup_izq: 
    try:
        df1 = dict_hojas['Tasa Overnight Diaria'].iloc[:, [0, 7]].dropna().tail(7)
        fechas1 = [d.strftime('%d/%m') for d in pd.to_datetime(df1.iloc[:, 0])]
        fig1 = go.Figure(go.Scatter(
            x=fechas1, y=df1.iloc[:, 1], mode='lines+markers+text', 
            text=[f"{val}%" for val in df1.iloc[:, 1]], textposition="top center", 
            line=dict(color='#60CCC8', width=4),
            textfont=dict(size=18, color="white")
        ))
        fig1.update_layout(
            title="TASA OVERNIGHT DIARIA BCV", 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_SUP, margin=dict(l=10, r=10, t=40, b=20),
            xaxis=dict(tickfont=dict(color="white", size=14)),
            yaxis=dict(gridcolor='#333', tickfont=dict(color="white")),
            font=dict(color="white"),
            hovermode=False # Desactivar hover para ahorrar memoria
        )
        st.plotly_chart(fig1, use_container_width=True, config=config_tv)
        st.markdown('<p class="concepto-texto">TASA PROMEDIO DIARIA APLICADA A PRÉSTAMOS INTERBANCARIOS.</p>', unsafe_allow_html=True)
    except: st.error("Error G1")

with col_sup_der: 
    try:
        df2 = dict_hojas['Reservas Bancarias Excedentari'].iloc[:, [0, 1]].dropna().head(7).iloc[::-1]
        fechas2 = [d.strftime('%d/%m') for d in pd.to_datetime(df2.iloc[:, 0])]
        fig2 = go.Figure(go.Bar(
            x=fechas2, y=df2.iloc[:, 1]/1000, 
            text=[f"{v/1000:,.2f}MM" for v in df2.iloc[:, 1]], 
            textposition='outside', marker_color=C_AZUL,
            textfont=dict(size=18, color="white")
        ))
        fig2.update_layout(
            title="RESERVAS BANCARIAS EXCEDENTARIAS BCV", 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_SUP, margin=dict(l=10, r=10, t=40, b=20),
            xaxis=dict(tickfont=dict(color="white", size=14)),
            yaxis=dict(gridcolor='#333', tickfont=dict(color="white")),
            font=dict(color="white"),
            hovermode=False
        )
        st.plotly_chart(fig2, use_container_width=True, config=config_tv)
        st.markdown('<p class="concepto-texto">DINERO EXTRA DE LOS BANCOS EN EL BCV.</p>', unsafe_allow_html=True)
    except: st.error("Error G2")

st.markdown("<hr style='border: 0.5px solid #444; margin: 10px 0;'>", unsafe_allow_html=True)

# ==========================================
# 6. FILA INFERIOR (Simplificada para RAM)
# ==========================================
col_inf_1, col_inf_2, col_inf_3, col_inf_4 = st.columns(4)

with col_inf_1: 
    try:
        df3 = dict_hojas['Tasa Overnight Mensual'].iloc[0:5, [0, 3]]
        fig3 = go.Figure(go.Scatter(x=df3.iloc[:, 0], y=df3.iloc[:, 1], mode='lines+markers+text', 
                                    text=[f"{v}%" for v in df3.iloc[:, 1]], textposition="top center",
                                    line=dict(color=C_NARANJA, width=3)))
        fig3.update_layout(title="OVERNIGHT %", height=ALT_INF, paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=5,r=5,t=30,b=5),
                          xaxis=dict(tickfont=dict(size=12, color="white")), yaxis=dict(visible=False), hovermode=False)
        st.plotly_chart(fig3, use_container_width=True, config=config_tv)
    except: st.write("---")

with col_inf_2:
    try:
        # Simplificación de lógica para evitar cuelgues
        df4 = dict_hojas['Base Monetaria'].tail(5)
        fig4 = go.Figure(go.Bar(x=df4.iloc[:, 0], y=df4.iloc[:, 1], marker_color='#2F4F4F'))
        fig4.update_layout(title="BASE MONETARIA", height=ALT_INF, paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=5,r=5,t=30,b=5),
                          xaxis=dict(visible=False), yaxis=dict(visible=False), hovermode=False)
        st.plotly_chart(fig4, use_container_width=True, config=config_tv)
    except: st.write("---")

with col_inf_3:
    try:
        df5 = dict_hojas['Liquidez Monetaria'].tail(5)
        fig5 = go.Figure(go.Bar(x=df5.iloc[:, 0], y=df5.iloc[:, 1], marker_color='#483D8B'))
        fig5.update_layout(title="LIQUIDEZ", height=ALT_INF, paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=5,r=5,t=30,b=5),
                          xaxis=dict(visible=False), yaxis=dict(visible=False), hovermode=False)
        st.plotly_chart(fig5, use_container_width=True, config=config_tv)
    except: st.write("---")

with col_inf_4:
    try:
        df6 = dict_hojas['Resev. Internacionales $'].tail(5)
        fig6 = go.Figure(go.Bar(x=df6.iloc[:, 0], y=df6.iloc[:, 1], marker_color='#191970'))
        fig6.update_layout(title="RESERVAS $", height=ALT_INF, paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=5,r=5,t=30,b=5),
                          xaxis=dict(visible=False), yaxis=dict(visible=False), hovermode=False)
        st.plotly_chart(fig6, use_container_width=True, config=config_tv)
    except: st.write("---")
