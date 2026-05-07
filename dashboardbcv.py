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
C_FONDOC = "#235B92"
C_AZUL = "#2B5DDA"
C_TITULO = "#87CEEB"
C_NARANJA = "#FCDD9F"
C_BLANCO = "#FFFFFF"
C_CIAN = "#60CCC8"      
C_GRIS_GRID = "#222222" 
C_BARRA_INF = "#483D8B" 
C_BARRA_BASE = "#2F4F4F" 
C_BARRA_RES = "#191970"  

# ALTURAS DEFINIDAS POR FILA
ALT_SUP = 230
ALT_INF = 230
ALT_FULL = 650 

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

if "expanded_graph" not in st.session_state:
    st.session_state.expanded_graph = None

# ==========================================
# 3. ESTILOS CSS (RESTAURADOS AL ORIGINAL)
# ==========================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300..700&display=swap');

[data-testid="stHeader"], header {{ display: none !important; height: 0px !important; }}
.stApp {{ margin-top: 0px !important; background-color: {C_FONDO} !important; }}

.main .block-container {{ padding: 0px .5rem !important; max-width: 100%; overflow: hidden !important;}}
html, body, .main {{ 
    font-family: 'Quicksand', sans-serif; 
    overflow: hidden; 
    background-color: {C_FONDOC} !important; 
    color: {C_BLANCO};
}}

/* BOTÓN VOLVER */
div.stButton > button {{
    background-color: {C_AZUL} !important;
    color: white !important;
    border: none !important;
    border-radius: 5px !important;
    padding: 0.5rem 1rem !important;
}}

/* FORZAR DESCRIPCIONES COMO LINKS (SIN RECORTES) */
div[data-testid="stColumn"] div.stButton > button {{
    background-color: transparent !important;
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    color: {C_NARANJA} !important;
    font-size: 20px !important;
    font-family: 'Quicksand', sans-serif !important;
    font-weight: 400 !important;
    text-align: center !important;
    padding: 0px !important;
    width: 100% !important;
    min-height: 40px !important;
    display: block !important;
}}

div[data-testid="stColumn"] div.stButton > button:hover {{
    color: {C_NARANJA} !important;
    text-decoration: underline !important;
    background-color: transparent !important;
}}

.stMainBlockContainer {{
    padding:10px 20px 0px 20px
}}
.concepto-texto{{
    color:{C_BLANCO};
    text-transform:uppercase;
    text-align:center;
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

content_map = {}

# ==========================================
# 5. CONSTRUCCIÓN DE GRÁFICOS 
# ==========================================

# G1
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
        title=dict(text="Tasa Overnight Diaria BCV", font=dict(color=C_BLANCO)), 
        paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False,
        height=ALT_SUP, margin=dict(l=10, r=10, t=40, b=40), 
        xaxis=dict(tickangle=-30, tickfont=dict(color=C_BLANCO, size=17)), 
        yaxis=dict(gridcolor=C_GRIS_GRID, tickfont=dict(color=C_BLANCO)), font=dict(color=C_BLANCO)
    )
    content_map['G1'] = (fig1, "Tasa promedio diaria aplicada a préstamos interbancarios o depósitos a muy corto plazo (un día hábil).")
except: pass

# G2
try:
    df2 = dict_hojas['Reservas Bancarias Excedentari'].iloc[:, [0, 1, 2]].dropna().head(7).iloc[::-1]
    fechas2 = [d.strftime('%d/%m/%Y') for d in pd.to_datetime(df2.iloc[:, 0])]
    montos2 = df2.iloc[:, 1]/1000
    var2 = df2.iloc[:, 2] 
    fig2 = go.Figure(go.Bar(
        x=fechas2, y=montos2, 
        text=[f"{v:,.3f}MM" for v in montos2], 
        textposition='outside', marker_color=C_AZUL, cliponaxis=False, 
        textfont=dict(size=24, color=C_BLANCO), width=0.9
    ))
    escala2 = montos2.max() / (var2.abs().max() if var2.abs().max() != 0 else 1)
    fig2.add_trace(go.Scatter(
        x=fechas2, y=var2 * escala2 * 0.7, mode='lines+markers+text', 
        text=[f"{v:.2f}%" for v in var2], 
        textposition="top center", line=dict(color=C_NARANJA, width=3), 
        textfont=dict(color=C_NARANJA, size=18), cliponaxis=False
    ))
    fig2.update_layout(
        title=dict(text="Reservas Excedentarias BCV", font=dict(color=C_BLANCO)), 
        paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False,
        height=ALT_SUP, margin=dict(l=10, r=10, t=40, b=40), 
        xaxis=dict(tickangle=-30, tickfont=dict(color=C_BLANCO, size=18)), 
        yaxis=dict(showticklabels=False), font=dict(color=C_BLANCO), showlegend=False
    )
    content_map['G2'] = (fig2, "Cantidad de dinero extra que poseen los bancos en el BCV por encima de lo que la ley indica (Encaje legal).")
except: pass

# G3
try:
    df3 = dict_hojas['Tasa Overnight Mensual'].iloc[0:5, [0, 3]]
    fig3 = go.Figure(go.Scatter(
        x=df3.iloc[:, 0], y=df3.iloc[:, 1], mode='lines+markers+text', 
        text=[f"{val}%" for val in df3.iloc[:, 1]], textposition="top center", 
        cliponaxis=False, line=dict(color=C_NARANJA, width=3), 
        textfont=dict(size=17, color=C_BLANCO)
    ))
    fig3.update_layout(
        title=dict(text="Tasa Overnight (% Mensual) BCV", font=dict(color=C_BLANCO)), 
        paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False,
        height=ALT_SUP, margin=dict(l=25, r=10, t=40, b=40), 
        xaxis=dict(tickfont=dict(color=C_BLANCO, size=18)), 
        yaxis=dict(showticklabels=False, gridcolor=C_GRIS_GRID), font=dict(color=C_BLANCO)
    )
    content_map['G3'] = (fig3, "Valor resultante de promediar las tasas de interés diarias a las que se negociaron los préstamos entre bancos en el mes.")
except: pass

# G5
try:
    df5 = dict_hojas['Liquidez Monetaria'].iloc[:, [0, 6, 7]].copy()
    df5['Fecha_DT'] = pd.to_datetime(df5.iloc[:, 0])
    df_f5 = df5.sort_values('Fecha_DT').tail(4)
    fechas5, montos5 = [d.strftime('%d/%m/%Y') for d in df_f5['Fecha_DT']], df_f5.iloc[:, 1] / 1000000
    var5 = df_f5.iloc[:, 2] 
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(x=fechas5, y=montos5, text=[f"{int(v):,}MM" for v in montos5], textposition='outside', marker_color=C_BARRA_INF, textfont=dict(color=C_BLANCO, size=24), width=0.6))
    escala5 = montos5.max() / (var5.abs().max() if var5.abs().max() != 0 else 1)
    fig5.add_trace(go.Scatter(x=fechas5, y=var5 * escala5 * 0.7, mode='lines+markers+text', text=[f"{v:.2f}%" for v in var5], textposition="top center", line=dict(color=C_NARANJA, width=3), textfont=dict(color=C_NARANJA, size=18), cliponaxis=False))
    fig5.update_layout(title=dict(text="Liquidez Monetaria BCV", font=dict(color=C_BLANCO)), paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False, height=ALT_INF, margin=dict(l=10, r=10, t=35, b=40), xaxis=dict(tickfont=dict(color=C_BLANCO, size=15)), yaxis=dict(showticklabels=False, range=[montos5.min()*-0.4, montos5.max()*1.4]), showlegend=False)
    content_map['G5'] = (fig5, "Cantidad total de dinero en circulación (efectivo, cuentas corrientes y de ahorro) disponibles en una economía para realizar transacciones.")
except: pass

# G4
try:
    df4 = dict_hojas['Base Monetaria'].iloc[:, [0, 1, 2]].copy()
    df4['Fecha_DT'] = pd.to_datetime(df4.iloc[:, 0])
    df_f4 = df4.sort_values('Fecha_DT').tail(4)
    fechas4, montos4 = [d.strftime('%d/%m/%Y') for d in df_f4['Fecha_DT']], df_f4.iloc[:, 1] / 1000000
    var4 = df_f4.iloc[:, 2] 
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=fechas4, y=montos4, text=[f"{v:,.1f}MM" for v in montos4], textposition='outside', marker_color=C_BARRA_BASE, textfont=dict(color=C_BLANCO, size=24), width=0.6))
    escala4 = montos4.max() / (var4.abs().max() if var4.abs().max() != 0 else 1)
    fig4.add_trace(go.Scatter(x=fechas4, y=var4 * escala4 * 0.7, mode='lines+markers+text', text=[f"{v:.2f}%" for v in var4], textposition="top center", line=dict(color=C_NARANJA, width=3), textfont=dict(color=C_NARANJA, size=18), cliponaxis=False))
    fig4.update_layout(title=dict(text="Base Monetaria BCV", font=dict(color=C_BLANCO)), paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False, height=ALT_INF, margin=dict(l=10, r=10, t=35, b=40), xaxis=dict(tickfont=dict(color=C_BLANCO, size=15)), yaxis=dict(showticklabels=False, range=[montos4.min()*-0.4, montos4.max()*1.4]), showlegend=False)
    content_map['G4'] = (fig4, "Monto total de dinero de curso legal emitido por BCV (efectivo + reservas bancarias).")
except: pass

# G6
try:
    df6 = dict_hojas['Resev. Internacionales $'].iloc[:, [0, 3, 4]].copy()
    df6['Fecha_DT'] = pd.to_datetime(df6.iloc[:, 0])
    df_f6 = df6.sort_values('Fecha_DT').tail(4)
    fechas6, montos6 = [d.strftime('%d/%m/%Y') for d in df_f6['Fecha_DT']], df_f6.iloc[:, 1]
    var6 = df_f6.iloc[:, 2] 
    fig6 = go.Figure()
    fig6.add_trace(go.Bar(x=fechas6, y=montos6, text=[f"{int(v):,}MM" for v in montos6], textposition='outside', marker_color=C_BARRA_RES, textfont=dict(color=C_BLANCO, size=24), width=0.6))
    escala6 = montos6.max() / (var6.abs().max() if var6.abs().max() != 0 else 1)
    fig6.add_trace(go.Scatter(x=fechas6, y=var6 * escala6 * 0.7, mode='lines+markers+text', text=[f"{v:.2f}%" for v in var6], textposition="top center", line=dict(color=C_NARANJA, width=3), textfont=dict(color=C_NARANJA, size=19), cliponaxis=False))
    fig6.update_layout(title=dict(text="Reservas Internacionales BCV", font=dict(color=C_BLANCO)), paper_bgcolor=C_FONDO, plot_bgcolor=C_FONDO, hovermode=False, height=ALT_INF, margin=dict(l=10, r=10, t=35, b=40), xaxis=dict(tickfont=dict(color=C_BLANCO, size=16)), yaxis=dict(showticklabels=False, range=[montos6.min()*-0.4, montos6.max()*1.4]), showlegend=False)
    content_map['G6'] = (fig6, "Total en divisas que el BCV tiene en resguardo, ya sea en sus propias arcas o en cuentas de bancos fuera de Venezuela.")
except: pass

# ==========================================
# 6. RENDERIZADO LÓGICO
# ==========================================

if st.session_state.expanded_graph:
    id_g = st.session_state.expanded_graph
    fig_full, desc_full = content_map[id_g]
    if st.button("VOLVER"):
        st.session_state.expanded_graph = None
        st.rerun()
    fig_full.update_layout(height=ALT_FULL)
    st.plotly_chart(fig_full, use_container_width=True, config={'displayModeBar': False})
    st.markdown(f'<p class="concepto-texto">{desc_full}</p>', unsafe_allow_html=True)
else:
    col_sup_1, col_sup_2, col_sup_3 = st.columns([0.35, 0.35, 0.30])
    with col_sup_1:
        if 'G1' in content_map:
            st.plotly_chart(content_map['G1'][0], use_container_width=True, config={'displayModeBar': False})
            if st.button(content_map['G1'][1], key="btn_g1"):
                st.session_state.expanded_graph = 'G1'
                st.rerun()
    with col_sup_2:
        if 'G2' in content_map:
            st.plotly_chart(content_map['G2'][0], use_container_width=True, config={'displayModeBar': False})
            if st.button(content_map['G2'][1], key="btn_g2"):
                st.session_state.expanded_graph = 'G2'
                st.rerun()
    with col_sup_3:
        if 'G3' in content_map:
            st.plotly_chart(content_map['G3'][0], use_container_width=True, config={'displayModeBar': False})
            if st.button(content_map['G3'][1], key="btn_g3"):
                st.session_state.expanded_graph = 'G3'
                st.rerun()

    st.markdown(f"<hr style='border: 0.5px solid {C_GRIS_GRID}; margin: 15px 0;'>", unsafe_allow_html=True)

    col_inf_1, col_inf_2, col_inf_3 = st.columns([0.33, 0.33, 0.34])
    with col_inf_1:
        if 'G5' in content_map:
            st.plotly_chart(content_map['G5'][0], use_container_width=True, config={'displayModeBar': False})
            if st.button(content_map['G5'][1], key="btn_g5"):
                st.session_state.expanded_graph = 'G5'
                st.rerun()
    with col_inf_2:
        if 'G4' in content_map:
            st.plotly_chart(content_map['G4'][0], use_container_width=True, config={'displayModeBar': False})
            if st.button(content_map['G4'][1], key="btn_g4"):
                st.session_state.expanded_graph = 'G4'
                st.rerun()
    with col_inf_3:
        if 'G6' in content_map:
            st.plotly_chart(content_map['G6'][0], use_container_width=True, config={'displayModeBar': False})
            if st.button(content_map['G6'][1], key="btn_g6"):
                st.session_state.expanded_graph = 'G6'
                st.rerun()
