import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import base64
from pathlib import Path
from datetime import datetime, timedelta

# =========================================
# 1. CONFIGURACIÓN BÁSICA
# ==========================================
st.set_page_config(
    page_title="Dashboard Riesgo BCV",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Refresco cada 10 minutos
st_autorefresh(interval=600000, key="datarefresh")

C_FONDO = "#0E1117"
C_NARANJA = "#FFDEAD"
C_TITULO = "#87CEEB"

# ==========================================
# 2. ESTILOS CSS SEGUROS (SIN BLOQUEOS)
# ==========================================
st.markdown(f"""
<style>
    /* Eliminar cabeceras de Streamlit */
    [data-testid="stHeader"], header {{ display: none !important; }}
    
    /* Ajuste de contenedor principal */
    .stApp {{ 
        background-color: {C_FONDO} !important; 
    }}
    
    .main .block-container {{
        padding: 10px 2rem !important;
        max-width: 100%;
    }}

    /* Títulos legibles en TV */
    .title-main {{ 
        font-size: 2.2rem; 
        color: {C_TITULO}; 
        margin: 0; 
        font-weight: bold;
    }}
    
    .update-text {{ 
        font-size: 1rem; 
        color: {C_NARANJA}; 
        text-align: right; 
    }}

    .concepto-texto {{
        font-size: 1.1rem;
        color: {C_NARANJA};
        text-align: center;
        line-height: 1.2;
        margin-bottom: 20px;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CARGA DE DATOS (CON MANEJO DE ERRORES)
# ==========================================
@st.cache_data(ttl=600)
def cargar_datos(ruta):
    try:
        return pd.read_excel(ruta, sheet_name=None, engine='openpyxl')
    except:
        return None

dict_hojas = cargar_datos('Datos_Macroeconomicos.xlsx')

# Encabezado simple
ahora = (datetime.utcnow() - timedelta(hours=4)).strftime("%d/%m/%Y %I:%M %p")

col_h1, col_h2 = st.columns([0.8, 0.2])
with col_h1:
    st.markdown(f'<p class="title-main">UNIDAD DE RIESGO - INDICADORES BCV</p>', unsafe_allow_html=True)
with col_h2:
    st.markdown(f'<div class="update-text">Actualizado:<br><b>{ahora}</b></div>', unsafe_allow_html=True)

if dict_hojas is not None:
    # ==========================================
    # 4. FILA SUPERIOR (2 Gráficos grandes)
    # ==========================================
    c1, c2 = st.columns(2)
    
    with c1:
        try:
            df1 = dict_hojas['Tasa Overnight Diaria'].iloc[:, [0, 7]].dropna().tail(7)
            fig1 = go.Figure(go.Scatter(
                x=pd.to_datetime(df1.iloc[:, 0]).dt.strftime('%d/%m'),
                y=df1.iloc[:, 1],
                mode='lines+markers+text',
                text=[f"{v}%" for v in df1.iloc[:, 1]],
                textposition="top center",
                line=dict(color='#60CCC8', width=3)
            ))
            fig1.update_layout(title="TASA OVERNIGHT DIARIA", height=350, paper_bgcolor='rgba(0,0,0,0)', 
                              plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"),
                              margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
            st.markdown('<p class="concepto-texto">Promedio de préstamos interbancarios a un día.</p>', unsafe_allow_html=True)
        except: st.error("Error en Gráfico 1")

    with c2:
        try:
            df2 = dict_hojas['Reservas Bancarias Excedentari'].iloc[:, [0, 1]].dropna().head(7).iloc[::-1]
            fig2 = go.Figure(go.Bar(
                x=pd.to_datetime(df2.iloc[:, 0]).dt.strftime('%d/%m'),
                y=df2.iloc[:, 1]/1000,
                text=[f"{v/1000:,.2f}MM" for v in df2.iloc[:, 1]],
                textposition='outside',
                marker_color='#2b5dda'
            ))
            fig2.update_layout(title="RESERVAS EXCEDENTARIAS (MM Bs.)", height=350, paper_bgcolor='rgba(0,0,0,0)', 
                              plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"),
                              margin=dict(l=20, r=20, t=50, b=20))
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
            st.markdown('<p class="concepto-texto">Exceso de dinero de la banca sobre el encaje legal.</p>', unsafe_allow_html=True)
        except: st.error("Error en Gráfico 2")

    st.markdown("<hr style='border: 0.5px solid #444;'>", unsafe_allow_html=True)

    # ==========================================
    # 5. FILA INFERIOR (4 Gráficos pequeños)
    # ==========================================
    c3, c4, c5, c6 = st.columns(4)
    
    # Lista de configuraciones para iterar más rápido
    indicadores = [
        ('Tasa Overnight Mensual', 'OVERNIGHT MENSUAL %', '#FFDEAD', c3),
        ('Base Monetaria', 'BASE MONETARIA', '#2F4F4F', c4),
        ('Liquidez Monetaria', 'LIQUIDEZ MONETARIA', '#483D8B', c5),
        ('Resev. Internacionales $', 'RESERVAS INT. ($)', '#191970', c6)
    ]

    for hoja, titulo, color, columna in indicadores:
        with columna:
            try:
                df = dict_hojas[hoja].tail(5)
                fig = go.Figure(go.Bar(x=df.iloc[:,0], y=df.iloc[:,1], marker_color=color))
                fig.update_layout(title=titulo, height=250, paper_bgcolor='rgba(0,0,0,0)', 
                                 plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white", size=10),
                                 margin=dict(l=10, r=10, t=40, b=10), xaxis=dict(visible=False), yaxis=dict(visible=False))
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            except:
                st.write(f"Sin datos: {titulo}")
else:
    st.warning("No se pudo cargar el archivo Excel. Verifique el nombre y la ubicación.")
