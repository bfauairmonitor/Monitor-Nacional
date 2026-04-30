import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
import time
from pathlib import Path
from datetime import datetime, timedelta

# =========================================
# 1. VARIABLES GLOBALES (CASCADA DE EDICIÓN)
# ==========================================
REFRESH_INT = 600000  # Intervalo en segundos (10 minutos)
C_FONDO = "#0E1117"
C_AZUL = "#2b5dda"
C_TITULO = "#87CEEB"
C_NARANJA = "#FFDEAD"
C_BLANCO = "#FFFFFF"
ALT_SUP = 260
ALT_INF = 280

# ==========================================
# 2. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard Administrativo de Riesgo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Lógica de refresco nativo para evitar errores de componentes en TV
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# ==========================================
# 3. ESTILOS CSS
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700;900&display=swap');
[data-testid="stHeader"], header {{ display: none !important; height: 0px !important; }}
.stApp {{ margin-top: -90px !important; background-color: {C_FONDO} !important; }}
.main .block-container {{ padding: 0px 1rem !important; max-width: 100%; }}
html, body, .main {{ 
font-family: 'Roboto', sans-serif; 
overflow: hidden; 
background-color: {C_FONDO} !important;
color: white;
}}
.header-container {{
display: flex; justify-content: space-between; align-items: center;
padding: 15px 5px; background-color: {C_FONDO}; 
border-bottom: 2px solid #444; height: auto; margin-bottom: 30px;
}}
.title-main {{ font-size: 3.1rem; margin: 0; color: {C_TITULO}; }}
.subtitle-sub {{ font-size: 2.2rem; color: #ffffff; margin: 0; }}
.update-text {{ font-size: 1rem; color: {C_NARANJA}; text-align: right; line-height: 1.1; }}
[data-testid="stVerticalBlock"] {{ gap: 0rem !important; }}
.st-emotion-cache-18kf3ut{{ margin-top:20px;}}
.stHorizontalBlock{{ margin-top:10px;}}

/* Estilo para los conceptos debajo de los gráficos */
.concepto-texto {{
    font-size: 8vw;
    color: {C_NARANJA};
    text-align: center;
    margin-top: -10px;
    font-weight: 500;
    padding:5px 20px;
}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. FUNCIONES Y LÓGICA DE DATOS
# ==========================================

@st.cache_data
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()
    except: return ""

@st.cache_data(ttl=600, show_spinner=False)
def cargar_datos_excel(ruta):
    return pd.read_excel(ruta, sheet_name=None, engine='openpyxl')

# Verificación de tiempo para refresco automático nativo
if time.time() - st.session_state.last_refresh > REFRESH_INT:
    st.session_state.last_refresh = time.time()
    st.rerun()

ahora = (datetime.utcnow() - timedelta(hours=4)).strftime("%d/%m/%Y %I:%M %p")
logo_path = Path("assets/logo.png")
logo_b64 = get_base64(logo_path)
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:3vh;">' if logo_b64 else ''

try:
    placeholder = st.empty()
    with placeholder.container():
        with st.spinner(""):
            st.markdown(f"""
                <div style="text-align: center; margin-bottom: 10px;">
                    <p style="color: {C_NARANJA}; font-size: 1.2rem; font-weight: 500;">
                        ESTAMOS ACTUALIZANDO LOS INDICADORES, POR FAVOR ESPERE...
                    </p>
                </div>
            """, unsafe_allow_html=True)
            dict_hojas = cargar_datos_excel('Datos_Macroeconomicos.xlsx')
    placeholder.empty()
except Exception as e:
    st.error(f"Error al cargar Excel: {e}")
    dict_hojas = {}

st.markdown(f"""
<div class="header-container">
<div style="display: flex; align-items: center; gap: 20px;">
{logo_html}
<div>
<p class="title-main">UNIDAD ADMINISTRATIVA INTEGRAL DE RIESGO</p>
<p class="subtitle-sub">Indicadores Macroeconómicos BCV.</p>
</div>
</div>
<div class="update-text">Última actualización:<br><b>{ahora}</b></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. FILA SUPERIOR (AJUSTE: 35% - 35% - 30%)
# =========================================
col_sup_1, col_sup_2, col_sup_3 = st.columns([0.35, 0.35, 0.30])

with col_sup_1: 
    try:
        df1 = dict_hojas['Tasa Overnight Diaria'].iloc[:, [0, 7]] 
        df1 = df1.dropna().tail(7)
        fechas1 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df1.iloc[:, 0])]
        fig1 = go.Figure(go.Scatter(
            x=fechas1, y=df1.iloc[:, 1], mode='lines+markers+text', 
            text=[f"{val}%" for val in df1.iloc[:, 1]], textposition="top center", 
            cliponaxis=False, line=dict(color='#60CCC8', width=4, shape='spline'), 
            marker=dict(size=10, color='#FFFFFF', line=dict(width=2, color='#60CCC8')), 
            textfont=dict(size=22, color="white")
        ))
        fig1.update_layout(
            title=dict(text="TASA OVERNIGHT DIARIA BCV", font=dict(color="white")), 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_SUP, margin=dict(l=10, r=10, t=40, b=40), 
            xaxis=dict(tickangle=-30, tickfont=dict(color="white", size=18)), 
            yaxis=dict(gridcolor='#222222', tickfont=dict(color="white")), font=dict(color="#ffffff")
        )
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">TASA PROMEDIO DIARIA APLICADA A PRÉSTAMOS INTERBANCARIOS O DEPÓSITOS A MUY CORTO PLAZO (UN DIA HABIL).</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G1: {e}")
        
with col_sup_2: 
    try:
        df2 = dict_hojas['Reservas Bancarias Excedentari'].iloc[:, [0, 1]]
        df2 = df2.dropna().head(7).iloc[::-1]
        fechas2 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df2.iloc[:, 0])]
        fig2 = go.Figure(go.Bar(
            x=fechas2, y=df2.iloc[:, 1]/1000, 
            text=[f"{v/1000:,.3f}MM" for v in df2.iloc[:, 1]], 
            textposition='outside', marker_color=C_AZUL, cliponaxis=False, 
            textfont=dict(size=22, color="white"),
            width=0.6  # <--- MODIFICAR ANCHO DE BARRAS AQUÍ (0.1 a 1.0)
        ))
        fig2.update_layout(
            title=dict(text="RESERVAS BANCARIAS EXCEDENTARIAS (EN BOLIVARES) BCV", font=dict(color="white")), 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_SUP, margin=dict(l=10, r=10, t=30, b=40), 
            xaxis=dict(tickangle=-30, tickfont=dict(color="white", size=18)), 
            yaxis=dict(gridcolor='#222222', tickfont=dict(color="white")), font=dict(color=C_BLANCO)
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">CANTIDAD DE DINERO EXTRA QUE POSEEN LOS BANCOS EN EL BCV POR ENCIMA DE LO QUE LA LEY INDICA (ENCAJE LEGAL).</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G2: {e}")

with col_sup_3: 
    try:
        df3 = dict_hojas['Tasa Overnight Mensual'].iloc[0:5, [0, 3]]
        fig3 = go.Figure(go.Scatter(
            x=df3.iloc[:, 0], y=df3.iloc[:, 1], mode='lines+markers+text', 
            text=[f"{val}%" for val in df3.iloc[:, 1]], textposition="top center", 
            cliponaxis=False, line=dict(color=C_NARANJA, width=3, shape='spline'), 
            textfont=dict(size=22, color="white")
        ))
        fig3.update_layout(
            title=dict(text="TASA OVERNIGHT (% MENSUAL) BCV", font=dict(color="white")), 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            height=ALT_SUP, margin=dict(l=25, r=5, t=45, b=30), 
            xaxis=dict(tickfont=dict(color="white", size=18)), 
            yaxis=dict(showticklabels=False, gridcolor='#222222'), font=dict(color='#2F4F4F')
        )
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">VALOR RESULTANTE DE PROMEDIAR LAS TASAS DE INTERÉS DIARIAS A LAS QUE SE NEGOCIARON LOS PRÉSTAMOS ENTRE BANCOS EN EL MES.</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G3: {e}")

# LÍNEA DIVISORIA ENTRE FILAS
st.markdown("<hr style='border: 0.5px solid #444; margin: 15px 0;'>", unsafe_allow_html=True)

# ==========================================
# 6. FILA INFERIOR (AJUSTE: 33% C/U - ORDEN: LIQUIDEZ, BASE, RESERVAS)
# ==========================================
col_inf_1, col_inf_2, col_inf_3 = st.columns([0.33, 0.33, 0.34])
hoy = (datetime.utcnow() - timedelta(hours=4))

with col_inf_1: 
    try:
        df5 = dict_hojas['Liquidez Monetaria'].iloc[:, [0, 6, 7]]
        df5['Fecha_DT'] = pd.to_datetime(df5.iloc[:, 0])
        df_f5 = df5[(df5['Fecha_DT'].dt.month == hoy.month) & (df5['Fecha_DT'].dt.year == hoy.year)]
        if df_f5.empty:
            m, a = (hoy.month-1, hoy.year) if hoy.month > 1 else (12, hoy.year-1)
            df_f5 = df5[(df5['Fecha_DT'].dt.month == m) & (df5['Fecha_DT'].dt.year == a)]
        df_f5 = df_f5.sort_values('Fecha_DT')
        fechas5, montos5, var5 = [d.strftime('%d/%m/%Y') for d in df_f5['Fecha_DT']], df_f5.iloc[:, 1] / 1000000, df_f5.iloc[:, 2]
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(
            x=fechas5, y=montos5, text=[f"{int(v):,}MM" for v in montos5], 
            textposition='outside', marker_color='#483D8B', 
            textfont=dict(color="white", size=22),
            width=0.4  # <--- MODIFICAR ANCHO DE BARRAS AQUÍ
        ))
        escala5 = montos5.max() / (var5.abs().max() if var5.abs().max() != 0 else 1)
        fig5.add_trace(go.Scatter(x=fechas5, y=var5 * escala5 * 0.7, mode='lines+markers+text', text=[f"{v:.2f}%" for v in var5], textposition="top center", line=dict(color=C_NARANJA, width=3), textfont=dict(color=C_NARANJA, size=18), cliponaxis=False))
        fig5.update_layout(title=dict(text="LIQUIDÉZ MONETARIA BCV", font=dict(color="white")), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=ALT_INF, margin=dict(l=5, r=10, t=35, b=40), xaxis=dict(tickfont=dict(color="white", size=15)), yaxis=dict(showticklabels=False, range=[montos5.min()*-0.4, montos5.max()*1.4]), showlegend=False)
        st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">CANTIDAD TOTAL DE DINERO EN CIRCULACIÓN (EFECTIVO, CUENTAS CORRIENTES Y DE AHORRO) DISPONIBLES EN UNA ECONOMÍA PARA REALIZAR TRANSACCIONES.</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G5: {e}")

with col_inf_2: 
    try:
        df4 = dict_hojas['Base Monetaria'].iloc[:, [0, 1, 2]]
        df4['Fecha_DT'] = pd.to_datetime(df4.iloc[:, 0])
        df_f4 = df4[(df4['Fecha_DT'].dt.month == hoy.month) & (df4['Fecha_DT'].dt.year == hoy.year)]
        if df_f4.empty:
            m, a = (hoy.month-1, hoy.year) if hoy.month > 1 else (12, hoy.year-1)
            df_f4 = df4[(df4['Fecha_DT'].dt.month == m) & (df4['Fecha_DT'].dt.year == a)]
        df_f4 = df_f4.sort_values('Fecha_DT')
        fechas4, montos4, var4 = [d.strftime('%d/%m/%Y') for d in df_f4['Fecha_DT']], df_f4.iloc[:, 1] / 1000000, df_f4.iloc[:, 2]
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=fechas4, y=montos4, text=[f"{v:,.1f}MM" for v in montos4], 
            textposition='outside', marker_color='#2F4F4F', 
            textfont=dict(color="white", size=22),
            width=0.5  # <--- MODIFICAR ANCHO DE BARRAS AQUÍ
        ))
        escala4 = montos4.max() / (var4.abs().max() if var4.abs().max() != 0 else 1)
        fig4.add_trace(go.Scatter(x=fechas4, y=var4 * escala4 * 0.7, mode='lines+markers+text', text=[f"{v:.2f}%" for v in var4], textposition="top center", line=dict(color=C_NARANJA, width=3), textfont=dict(color=C_NARANJA, size=18), cliponaxis=False))
        fig4.update_layout(title=dict(text="BASE MONETARIA BCV", font=dict(color="white")), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=ALT_INF, margin=dict(l=5, r=5, t=30, b=40), xaxis=dict(tickfont=dict(color="white", size=15)), yaxis=dict(showticklabels=False, range=[montos4.min()*-0.4, montos4.max()*1.4]), showlegend=False)
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">MONTO TOTAL DE DINERO DE CURSO LEGAL EMITIDO POR BCV (EFECTIVO + RESERVAS BANCARIAS).</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G4: {e}")

with col_inf_3: 
    try:
        df6 = dict_hojas['Resev. Internacionales $'].iloc[:, [0, 3, 4]]
        df6['Fecha_DT'] = pd.to_datetime(df6.iloc[:, 0])
        df_f6 = df6[(df6['Fecha_DT'].dt.month == hoy.month) & (df6['Fecha_DT'].dt.year == hoy.year)]
        if df_f6.empty:
            m, a = (hoy.month-1, hoy.year) if hoy.month > 1 else (12, hoy.year-1)
            df_f6 = df6[(df6['Fecha_DT'].dt.month == m) & (df6['Fecha_DT'].dt.year == a)]
        df_f6 = df_f6.sort_values('Fecha_DT')
        fechas6, montos6, var6 = [d.strftime('%d/%m/%Y') for d in df_f6['Fecha_DT']], df_f6.iloc[:, 1], df_f6.iloc[:, 2]
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            x=fechas6, y=montos6, text=[f"{int(v):,}MM" for v in montos6], 
            textposition='outside', marker_color='#191970', 
            textfont=dict(color="white", size=22),
            width=0.5  # <--- MODIFICAR ANCHO DE BARRAS AQUÍ
        ))
        escala6 = montos6.max() / (var6.abs().max() if var6.abs().max() != 0 else 1)
        fig6.add_trace(go.Scatter(x=fechas6, y=var6 * escala6 * 0.7, mode='lines+markers+text', text=[f"{v:.2f}%" for v in var6], textposition="top center", line=dict(color=C_NARANJA, width=3), textfont=dict(color=C_NARANJA, size=19), cliponaxis=False))
        fig6.update_layout(title=dict(text="RESERVAS INTERNACIONALES ($) BCV", font=dict(color="white")), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=ALT_INF, margin=dict(l=5, r=10, t=35, b=40), xaxis=dict(tickfont=dict(color="white", size=16)), yaxis=dict(showticklabels=False, range=[montos6.min()*-0.4, montos6.max()*1.4]), showlegend=False)
        st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">TOTAL EN DIVISAS QUE EL BCV TIENE EN RESGUARDO, YA SEA EN SUS PROPIAS ARCAS O EN CUENTAS DE BANCOS FUERA DE VENEZUELA.', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G6: {e}")
