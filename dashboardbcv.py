import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

# =========================================
# 1. VARIABLES GLOBALES (CONTROL TOTAL)
# ==========================================
REFRESH_INT = 600 
C_FONDO = "#0E1117"
C_AZUL = "#2B5DDA"
C_TITULO = "#87CEEB"
C_NARANJA = "#FFDEAD"
C_BLANCO = "#FFFFFF"
C_CIAN = "#60CCC8"      
C_GRIS_GRID = "#222222" 
C_BARRA_INF = "#483D8B" 
C_BARRA_BASE = "#2F4F4F" 
C_BARRA_RES = "#191970"  

# ALTURAS DEFINIDAS POR FILA
ALT_SUP = 230
ALT_INF = 230

# ==========================================
# 2. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Indicadores Macro. BCV",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# ==========================================
# 3. ESTILOS CSS
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700;900&display=swap');
[data-testid="stHeader"], header {{ display: none !important; height: 0px !important; }}
.stApp {{ margin-top: 0px !important; background-color: {C_FONDO} !important; }}

.main .block-container {{ padding: 0px .5rem !important; max-width: 100%; overflow: hidden !important;}}
html, body, .main {{ 
    font-family: 'Roboto', sans-serif; 
    overflow: hidden; 
    background-color: {C_FONDO} !important;
    color: {C_BLANCO};
}}
.concepto-texto {{
    font-size: 20px;
    color: {C_NARANJA};
    text-align: center;
    min-height: 40px; 
}}
.stMainBlockContainer {{
    padding:10px 15px 0px 15px
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. FUNCIONES Y LÓGICA DE DATOS
# ==========================================

@st.cache_data(ttl=600)
def cargar_datos_excel(ruta):
    return pd.read_excel(ruta, sheet_name=None, engine='openpyxl')

if time.time() - st.session_state.last_refresh > REFRESH_INT:
    st.session_state.last_refresh = time.time()
    st.rerun()

try:
    dict_hojas = cargar_datos_excel('Datos_Macroeconomicos.xlsx')
except Exception as e:
    st.error(f"Error al cargar Excel: {e}")
    dict_hojas = {}

# ==========================================
# 5. FILA SUPERIOR (Gráficos 1, 2, 3 -> Altura: ALT_SUP)
# =========================================
col_sup_1, col_sup_2, col_sup_3 = st.columns([0.35, 0.35, 0.30])

with col_sup_1: 
    try:
        df1 = dict_hojas['Tasa Overnight Diaria'].iloc[:, [0, 7]].dropna().tail(7)
        fechas1 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df1.iloc[:, 0])]
        fig1 = go.Figure(go.Scatter(
            x=fechas1, y=df1.iloc[:, 1], mode='lines+markers+text', 
            text=[f"{val}%" for val in df1.iloc[:, 1]], textposition="top center", 
            cliponaxis=False, line=dict(color=C_CIAN, width=3), 
            marker=dict(size=10, color=C_BLANCO, line=dict(width=2, color=C_CIAN)), 
            textfont=dict(size=17, color=C_BLANCO)
        ))
        fig1.update_layout(
            title=dict(text="TASA OVERNIGHT DIARIA BCV", font=dict(color=C_BLANCO)), 
            paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False,
            height=ALT_SUP, margin=dict(l=10, r=10, t=40, b=40), 
            xaxis=dict(tickangle=-30, tickfont=dict(color=C_BLANCO, size=17)), 
            yaxis=dict(gridcolor=C_GRIS_GRID, tickfont=dict(color=C_BLANCO)), font=dict(color=C_BLANCO)
        )
        # CORRECCIÓN AQUÍ: width="stretch"
        st.plotly_chart(fig1, width="stretch", config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">TASA PROMEDIO DIARIA APLICADA A PRÉSTAMOS INTERBANCARIOS O DEPÓSITOS A MUY CORTO PLAZO (UN DIA HABIL).</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G1: {e}")
        
with col_sup_2: 
    try:
        df2 = dict_hojas['Reservas Bancarias Excedentari'].iloc[:, [0, 1]].dropna().head(7).iloc[::-1]
        fechas2 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df2.iloc[:, 0])]
        fig2 = go.Figure(go.Bar(
            x=fechas2, y=df2.iloc[:, 1]/1000, 
            text=[f"{v/1000:,.3f}MM" for v in df2.iloc[:, 1]], 
            textposition='outside', marker_color=C_AZUL, cliponaxis=False, 
            textfont=dict(size=24, color=C_BLANCO), width=0.9
        ))
        fig2.update_layout(
            title=dict(text="RESERVAS EXCEDENTARIAS BCV", font=dict(color=C_BLANCO)), 
            paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False,
            height=ALT_SUP, margin=dict(l=10, r=10, t=40, b=40), 
            xaxis=dict(tickangle=-30, tickfont=dict(color=C_BLANCO, size=18)), 
            yaxis=dict(gridcolor=C_GRIS_GRID, tickfont=dict(color=C_BLANCO)), font=dict(color=C_BLANCO)
        )
        # CORRECCIÓN AQUÍ: width="stretch"
        st.plotly_chart(fig2, width="stretch", config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">CANTIDAD DE DINERO EXTRA QUE POSEEN LOS BANCOS EN EL BCV POR ENCIMA DE LO QUE LA LEY INDICA (ENCAJE LEGAL).</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G2: {e}")

with col_sup_3: 
    try:
        df3 = dict_hojas['Tasa Overnight Mensual'].iloc[0:5, [0, 3]]
        fig3 = go.Figure(go.Scatter(
            x=df3.iloc[:, 0], y=df3.iloc[:, 1], mode='lines+markers+text', 
            text=[f"{val}%" for val in df3.iloc[:, 1]], textposition="top center", 
            cliponaxis=False, line=dict(color=C_NARANJA, width=3), 
            textfont=dict(size=17, color=C_BLANCO)
        ))
        fig3.update_layout(
            title=dict(text="TASA OVERNIGHT (% MENSUAL) BCV", font=dict(color=C_BLANCO)), 
            paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False,
            height=ALT_SUP, margin=dict(l=25, r=10, t=40, b=40), 
            xaxis=dict(tickfont=dict(color=C_BLANCO, size=18)), 
            yaxis=dict(showticklabels=False, gridcolor=C_GRIS_GRID), font=dict(color=C_BLANCO)
        )
        # CORRECCIÓN AQUÍ: width="stretch"
        st.plotly_chart(fig3, width="stretch", config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">VALOR RESULTANTE DE PROMEDIAR LAS TASAS DE INTERÉS DIARIAS A LAS QUE SE NEGOCIARON LOS PRÉSTAMOS ENTRE BANCOS EN EL MES.</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G3: {e}")

st.markdown(f"<hr style='border: 0.5px solid {C_GRIS_GRID}; margin: 15px 0;'>", unsafe_allow_html=True)

# ==========================================
# 6. FILA INFERIOR (Gráficos 4, 5, 6 -> Altura: ALT_INF)
# ==========================================
col_inf_1, col_inf_2, col_inf_3 = st.columns([0.33, 0.33, 0.34])

with col_inf_1: 
    try:
        df5 = dict_hojas['Liquidez Monetaria'].iloc[:, [0, 6, 7]].copy()
        df5['Fecha_DT'] = pd.to_datetime(df5.iloc[:, 0])
        df_f5 = df5.sort_values('Fecha_DT').tail(4)
        fechas5, montos5, var5 = [d.strftime('%d/%m/%Y') for d in df_f5['Fecha_DT']], df_f5.iloc[:, 1] / 1000000, df_f5.iloc[:, 2]
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(x=fechas5, y=montos5, text=[f"{int(v):,}MM" for v in montos5], textposition='outside', marker_color=C_BARRA_INF, textfont=dict(color=C_BLANCO, size=24), width=0.6))
        escala5 = montos5.max() / (var5.abs().max() if var5.abs().max() != 0 else 1)
        fig5.add_trace(go.Scatter(x=fechas5, y=var5 * escala5 * 0.7, mode='lines+markers+text', text=[f"{v:.2f}%" for v in var5], textposition="top center", line=dict(color=C_NARANJA, width=3), textfont=dict(color=C_NARANJA, size=18), cliponaxis=False))
        fig5.update_layout(title=dict(text="LIQUIDÉZ MONETARIA BCV", font=dict(color=C_BLANCO)), paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False, height=ALT_INF, margin=dict(l=10, r=10, t=35, b=40), xaxis=dict(tickfont=dict(color=C_BLANCO, size=15)), yaxis=dict(showticklabels=False, range=[montos5.min()*-0.4, montos5.max()*1.4]), showlegend=False)
        # CORRECCIÓN AQUÍ: width="stretch"
        st.plotly_chart(fig5, width="stretch", config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">CANTIDAD TOTAL DE DINERO EN CIRCULACIÓN (EFECTIVO, CUENTAS CORRIENTES Y DE AHORRO) DISPONIBLES EN UNA ECONOMÍA PARA REALIZAR TRANSACCIONES.</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G5: {e}")

with col_inf_2: 
    try:
        df4 = dict_hojas['Base Monetaria'].iloc[:, [0, 1, 2]].copy()
        df4['Fecha_DT'] = pd.to_datetime(df4.iloc[:, 0])
        df_f4 = df4.sort_values('Fecha_DT').tail(4)
        fechas4, montos4, var4 = [d.strftime('%d/%m/%Y') for d in df_f4['Fecha_DT']], df_f4.iloc[:, 1] / 1000000, df_f4.iloc[:, 2]
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=fechas4, y=montos4, text=[f"{v:,.1f}MM" for v in montos4], textposition='outside', marker_color=C_BARRA_BASE, textfont=dict(color=C_BLANCO, size=24), width=0.6))
        escala4 = montos4.max() / (var4.abs().max() if var4.abs().max() != 0 else 1)
        fig4.add_trace(go.Scatter(x=fechas4, y=var4 * escala4 * 0.7, mode='lines+markers+text', text=[f"{v:.2f}%" for v in var4], textposition="top center", line=dict(color=C_NARANJA, width=3), textfont=dict(color=C_NARANJA, size=18), cliponaxis=False))
        fig4.update_layout(title=dict(text="BASE MONETARIA BCV", font=dict(color=C_BLANCO)), paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False, height=ALT_INF, margin=dict(l=10, r=10, t=35, b=40), xaxis=dict(tickfont=dict(color=C_BLANCO, size=15)), yaxis=dict(showticklabels=False, range=[montos4.min()*-0.4, montos4.max()*1.4]), showlegend=False)
        # CORRECCIÓN AQUÍ: width="stretch"
        st.plotly_chart(fig4, width="stretch", config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">MONTO TOTAL DE DINERO DE CURSO LEGAL EMITIDO POR BCV (EFECTIVO + RESERVAS BANCARIAS).</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G4: {e}")

with col_inf_3: 
    try:
        df6 = dict_hojas['Resev. Internacionales $'].iloc[:, [0, 3, 4]].copy()
        df6['Fecha_DT'] = pd.to_datetime(df6.iloc[:, 0])
        df_f6 = df6.sort_values('Fecha_DT').tail(4)
        fechas6, montos6, var6 = [d.strftime('%d/%m/%Y') for d in df_f6['Fecha_DT']], df_f6.iloc[:, 1], df_f6.iloc[:, 2]
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(x=fechas6, y=montos6, text=[f"{int(v):,}MM" for v in montos6], textposition='outside', marker_color=C_BARRA_RES, textfont=dict(color=C_BLANCO, size=24), width=0.6))
        escala6 = montos6.max() / (var6.abs().max() if var6.abs().max() != 0 else 1)
        fig6.add_trace(go.Scatter(x=fechas6, y=var6 * escala6 * 0.7, mode='lines+markers+text', text=[f"{v:.2f}%" for v in var6], textposition="top center", line=dict(color=C_NARANJA, width=3), textfont=dict(color=C_NARANJA, size=19), cliponaxis=False))
        fig6.update_layout(title=dict(text="RESERVAS INTERNACIONALES BCV", font=dict(color=C_BLANCO)), paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False, height=ALT_INF, margin=dict(l=10, r=10, t=35, b=40), xaxis=dict(tickfont=dict(color=C_BLANCO, size=16)), yaxis=dict(showticklabels=False, range=[montos6.min()*-0.4, montos6.max()*1.4]), showlegend=False)
        # CORRECCIÓN AQUÍ: width="stretch"
        st.plotly_chart(fig6, width="stretch", config={'displayModeBar': False})
        st.markdown('<p class="concepto-texto">TOTAL EN DIVISAS QUE EL BCV TIENE EN RESGUARDO, YA SEA EN SUS PROPIAS ARCAS O EN CUENTAS DE BANCOS FUERA DE VENEZUELA.</p>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error G6: {e}")
