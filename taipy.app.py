import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN DE PÁGINA Y OCULTAR INTERFAZ
st.set_page_config(page_title="Monitor Financiero", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=300000, key="datarefresh")

# CSS: Títulos y ocultar menús de Streamlit (Share, Deploy, etc.)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    /* Ocultar elementos de Streamlit para modo Kiosko/TV */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .block-container { padding: 1rem !important; background-color: #f8f9fc; }
    
    /* Estilo del Título General solicitado */
    .main-title-container { text-align: center; margin-bottom: 20px; font-family: 'Poppins'; }
    .title-line1 { color: #2b5dda; font-size: 1.8vw; font-weight: 600; margin: 0; }
    .title-line2 { color: black; font-size: 1.4vw; font-weight: 400; margin: 0; }
    .title-line3 { color: black; font-size: 1.2vw; font-weight: 300; margin: 0; }
    
    .grafico-titulo { color: #2b5dda; font-family: 'Poppins'; font-size: 1.2vw; font-weight: 400; margin-bottom: 5px; }
    .chart-box { border: 1px solid #2b5dda; border-radius: 12px; background-color: white; padding: 10px; margin-bottom: 10px; height: 100%; }
    </style>
    
    <div class="main-title-container">
        <p class="title-line1">Banfanb, Banco Universal</p>
        <p class="title-line2">Indicadores Macroeconómicos Nacionales</p>
        <p class="title-line3">Unidad Administrativa Integral de Riesgo</p>
    </div>
    """, unsafe_allow_html=True)

# 2. CARGA DE DATOS (Ruta relativa para GitHub)
ruta = "Data_Situacional_Ejemplo.xlsx" 

def load_data(sheet):
    try:
        # Importante: Asegúrate de tener 'openpyxl' instalado
        df = pd.read_excel(ruta, sheet_name=sheet, engine='openpyxl')
        return df.dropna(how='all').reset_index(drop=True)
    except:
        return pd.DataFrame()

# --- FILA 1: GRÁFICOS PRINCIPALES ---
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    df_raw = load_data('Liquidez Monetaria')
    if not df_raw.empty:
        df = df_raw.dropna(subset=[df_raw.columns[6]]).tail(6)
        if not df.empty:
            head_col1, head_col2, head_col3 = st.columns([1.8, 1, 1])
            with head_col1:
                st.markdown('<p class="grafico-titulo">Liquidez Monetaria</p>', unsafe_allow_html=True)
            
            ultimo = df.iloc[-1, 6]
            promedio = df.iloc[:, 6].mean()
            var = df.iloc[-1, 7] if df.shape[1] > 7 else 0

            with head_col2:
                st.markdown(f'<div style="background:white; border:1px solid #dee2e6; border-radius:8px; padding:5px; text-align:center;"><p style="margin:0; font-size:0.8vw; color:#666;">Actual</p><p style="margin:0; font-size:1.1vw; font-weight:bold;">Bs. {ultimo:,.0f}</p><p style="margin:0; font-size:0.8vw; color:#28a745;">↑ {var*100:.2f}%</p></div>', unsafe_allow_html=True)
            with head_col3:
                st.markdown(f'<div style="background:white; border:1px solid #dee2e6; border-radius:8px; padding:5px; text-align:center;"><p style="margin:0; font-size:0.8vw; color:#666;">Promedio</p><p style="margin:0; font-size:1.1vw; font-weight:bold;">Bs. {promedio:,.0f}</p></div>', unsafe_allow_html=True)

            fig = go.Figure()
            x_ax = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
            fig.add_trace(go.Scatter(x=x_ax, y=df.iloc[:, 6], mode='lines+markers+text', text=[f"{v/1e6:,.0f}MM" for v in df.iloc[:, 6]], textposition="top center", line=dict(color='#2b5dda'), marker=dict(color='#fd941c', size=10)))
            fig.update_layout(plot_bgcolor='white', height=300, showlegend=False, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(showgrid=True, gridcolor='#eee', tickfont=dict(color='black')), xaxis=dict(linecolor='gray'))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    df_res = load_data('Resev. Internacionales $')
    if not df_res.empty:
        df = df_res.dropna(subset=[df_res.columns[3]]).tail(6)
        if not df.empty:
            st.markdown('<p class="grafico-titulo">Reservas Internacionales $</p>', unsafe_allow_html=True)
            fig = go.Figure()
            x_ax = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
            fig.add_trace(go.Scatter(x=x_ax, y=df.iloc[:, 3], mode='lines+markers+text', text=[f"{v:,.0f}MM" for v in df.iloc[:, 3]], textposition="top center", line=dict(color='#6A1B9A'), marker=dict(color='#6A1B9A', size=10)))
            fig.update_layout(plot_bgcolor='white', height=300, showlegend=False, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(showgrid=True, gridcolor='#eee', tickfont=dict(color='black')), xaxis=dict(linecolor='gray'))
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# --- FILA 2: CUADRÍCULA ---
c3, c4, c5, c6 = st.columns(4)

with c3:
    st.markdown('<div class="chart-box"><p class="grafico-titulo" style="font-size:0.9vw;">Bases Monetarias</p>', unsafe_allow_html=True)
    df = load_data('Bases Monetarias').tail(6)
    if not df.empty:
        fig = go.Figure(go.Bar(x=df.iloc[:, 0].dt.strftime('%d-%m-%Y'), y=df.iloc[:, 1], marker_color='#90A4AE', text=[f"{v/1e6:,.0f}M" for v in df.iloc[:, 1]], textposition="inside"))
        fig.update_layout(plot_bgcolor='white', height=180, showlegend=False, margin=dict(l=5, r=5, t=5, b=5), xaxis=dict(tickfont=dict(size=8)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="chart-box"><p class="grafico-titulo" style="font-size:0.9vw;">Reservas Bs.</p>', unsafe_allow_html=True)
    df = load_data('Liquidez Monetaria').tail(6)
    if not df.empty:
        fig = go.Figure(go.Bar(x=df.iloc[:, 0].dt.strftime('%d-%m-%Y'), y=df.iloc[:, 6], marker_color="#42698d", text=[f"{v/1e6:,.0f}M" for v in df.iloc[:, 6]], textposition="inside"))
        fig.update_layout(plot_bgcolor='white', height=180, showlegend=False, margin=dict(l=5, r=5, t=5, b=5), xaxis=dict(tickfont=dict(size=8)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with c5:
    st.markdown('<div class="chart-box"><p class="grafico-titulo" style="font-size:0.9vw;">Overnight Diaria</p>', unsafe_allow_html=True)
    df = load_data('Tasa Overnight Diaria').tail(10)
    if not df.empty:
        fig = go.Figure(go.Scatter(x=df.iloc[:, 0].dt.strftime('%d-%m'), y=df.iloc[:, 7], mode='lines+markers', line=dict(color='#2b5dda')))
        fig.update_layout(plot_bgcolor='white', height=180, showlegend=False, margin=dict(l=5, r=5, t=5, b=5), xaxis=dict(tickfont=dict(size=8)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="chart-box"><p class="grafico-titulo" style="font-size:0.9vw;">Overnight Mensual</p>', unsafe_allow_html=True)
    df = load_data('Tasa Overnight Mensual').tail(4)
    if not df.empty:
        fig = go.Figure(go.Bar(x=df.iloc[:, 0].astype(str), y=df.iloc[:, 1], marker_color='#2471A3', text=[f"{v:,.0f}" for v in df.iloc[:, 1]], textposition="inside"))
        fig.update_layout(plot_bgcolor='white', height=180, showlegend=False, margin=dict(l=5, r=5, t=5, b=5), xaxis=dict(tickfont=dict(size=8)))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
