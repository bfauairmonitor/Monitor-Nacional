import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN DE PÁGINA Y OCULTAR MENÚS
st.set_page_config(page_title="Monitor Financiero", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=300000, key="datarefresh")

# CSS: Títulos, contenedores y ocultar elementos de la interfaz
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    /* Ocultar header y menu de Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    .block-container { padding: 1rem !important; background-color: #f8f9fc; }
    
    /* Estilo Título General */
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

# 2. RUTA RELATIVA PARA GITHUB
ruta = "Data_Situacional_Ejemplo.xlsx" 

# CARGA DE DATOS MEJORADA
def load_data(sheet):
    try:
        df = pd.read_excel(ruta, sheet_name=sheet, engine='openpyxl')
        return df.dropna(how='all').reset_index(drop=True)
    except:
        return pd.DataFrame()

# --- FILA 1: GRÁFICOS GRANDES ---
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    df_raw = load_data('Liquidez Monetaria')
    if not df_raw.empty:
        num_cols = df_raw.shape[1]
        col_idx = 6 if num_cols > 6 else num_cols - 1
        df = df_raw.dropna(subset=[df_raw.columns[col_idx]]).tail(6)
        
        if not df.empty:
            st.markdown('<div style="margin-bottom: 2px;">', unsafe_allow_html=True) 
            head_col1, head_col2, head_col3 = st.columns([1.8, 1, 1])
            with head_col1:
                st.markdown('<p class="grafico-titulo">Liquidez Monetaria</p>', unsafe_allow_html=True)
            
            ultimo_valor = df.iloc[-1, col_idx]
            var_ultima = df.iloc[-1, col_idx + 1] if num_cols > col_idx + 1 else 0
            promedio_valor = df.iloc[:, col_idx].mean()

            with head_col2:
                st.markdown(f"""
                    <div style="background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 5px; text-align: center;">
                        <p style="margin:0; font-size: 0.8vw; color: #666;">Actual</p>
                        <p style="margin:0; font-size: 1.1vw; font-weight: bold; color: #333;">Bs. {ultimo_valor:,.0f}</p>
                        <p style="margin:0; font-size: 0.8vw; color: #28a745;">↑ {var_ultima*100:.2f}%</p>
                    </div>
                """, unsafe_allow_html=True)
            with head_col3:
                st.markdown(f"""
                    <div style="background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 5px; text-align: center;">
                        <p style="margin:0; font-size: 0.8vw; color: #666;">Promedio</p>
                        <p style="margin:0; font-size: 1.1vw; font-weight: bold; color: #333;">Bs. {promedio_valor:,.0f}</p>
                        <p style="margin:0; font-size: 0.8vw; color: transparent;">-</p>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y') 
            x_data = df['Fecha_Exacta'] 
            y_data = df.iloc[:, col_idx] 
            y_var = df.iloc[:, col_idx + 1] if num_cols > col_idx + 1 else y_data.pct_change()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=x_data, y=y_data, mode='lines+markers+text',
                text=[f"{v/1e6:,.0f}MM" if v >= 1e6 else f"{v:,.0f}" for v in y_data],
                textposition="top center", textfont=dict(color='black', size=12),
                line=dict(color='#2b5dda', width=1), marker=dict(color='#fd941c', size=10)
            ))
            fig.add_trace(go.Scatter(
                x=x_data, y=y_var, mode='lines+markers+text',
                text=[f"{v*100:.2f}%" if pd.notnull(v) else "" for v in y_var],
                textposition="bottom center", textfont=dict(color='black', size=12),
                line=dict(color='#43be95', width=1, dash='dot'), marker=dict(color='#43be95', size=10),
                yaxis='y2'
            ))
            fig.update_layout(
                plot_bgcolor='white', height=320, showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(showgrid=True, gridcolor='#eee', tickfont=dict(color='black', size=10), linecolor='gray', linewidth=1, zeroline=False),
                xaxis=dict(type='category', showgrid=False, tickfont=dict(color='black', size=10), linecolor='gray', linewidth=1),
                yaxis2=dict(overlaying='y', side='right', showgrid=False, showticklabels=False, zeroline=False)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    df_raw = load_data('Resev. Internacionales $')
    if not df_raw.empty:
        df = df_raw.dropna(subset=[df_raw.columns[3]]).tail(6)
        if not df.empty:
            st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
            head_col1, head_col2, head_col3 = st.columns([1.8, 1, 1])
            with head_col1:
                st.markdown('<p class="grafico-titulo">Reservas Internacionales $</p>', unsafe_allow_html=True)
            
            idx_max, idx_min = df.iloc[:, 3].idxmax(), df.iloc[:, 3].idxmin()
            max_val, min_val = df.loc[idx_max, df.columns[3]], df.loc[idx_min, df.columns[3]]
            var_max = df.loc[idx_max, df.columns[4]] if df.shape[1] > 4 else 0
            var_min = df.loc[idx_min, df.columns[4]] if df.shape[1] > 4 else 0

            with head_col2:
                st.markdown(f"""
                    <div style="background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 5px; text-align: center;">
                        <p style="margin:0; font-size: 0.8vw; color: #666;">Máximo Detectado</p>
                        <p style="margin:0; font-size: 1.1vw; font-weight: bold; color: #333;">{max_val:,.1f} MM</p>
                        <p style="margin:0; font-size: 0.8vw; color: #dc3545;">{"↓" if var_max < 0 else "↑"} {abs(var_max*100):.2f}%</p>
                    </div>
                """, unsafe_allow_html=True)
            with head_col3:
                st.markdown(f"""
                    <div style="background: white; border: 1px solid #dee2e6; border-radius: 8px; padding: 5px; text-align: center;">
                        <p style="margin:0; font-size: 0.8vw; color: #666;">Mínimo Detectado</p>
                        <p style="margin:0; font-size: 1.1vw; font-weight: bold; color: #333;">{min_val:,.1f} MM</p>
                        <p style="margin:0; font-size: 0.8vw; color: #28a745;">{"↓" if var_min < 0 else "↑"} {abs(var_min*100):.2f}%</p>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Fecha_Exacta'], y=df.iloc[:, 3], fill='tozeroy', mode='lines+markers+text',
                text=[f"{v:,.1f}MM" for v in df.iloc[:, 3]], textposition="top center", 
                textfont=dict(color='black', size=12), fillcolor='rgba(0,0,0,0)', 
                line=dict(color='#6A1B9A', width=1), marker=dict(color='#6A1B9A', size=10)
            ))
            fig.add_trace(go.Scatter(
                x=df['Fecha_Exacta'], y=df.iloc[:, 4] if df.shape[1] > 4 else df.iloc[:, 3].pct_change(),
                mode='lines+markers+text', text=[f"{v*100:.2f}%" if pd.notnull(v) else "" for v in (df.iloc[:, 4] if df.shape[1] > 4 else df.iloc[:, 3].pct_change())],
                textposition="bottom center", textfont=dict(color='black', size=12),
                line=dict(color='#fd941c', width=1, dash='dot'), marker=dict(color='#fd941c', size=10), yaxis='y2'
            ))
            fig.update_layout(
                plot_bgcolor='white', height=320, showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(showgrid=True, gridcolor='#eee', tickfont=dict(color='black', size=11), linecolor='gray', linewidth=1, zeroline=False),
                xaxis=dict(type='category', showgrid=False, tickfont=dict(color='black', size=11), linecolor='gray', linewidth=1),
                yaxis2=dict(overlaying='y', side='right', showgrid=False, showticklabels=False, zeroline=False)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# --- FILA 2: CUADRÍCULA DE 4 ---
c3, c4, c5, c6 = st.columns(4)

with c3:
    st.markdown('<div class="chart-box"><p class="grafico-titulo" style="font-size:0.9vw;">Bases Monetarias</p>', unsafe_allow_html=True)
    df = load_data('Bases Monetarias').tail(6)
    if not df.empty:
        df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Fecha_Exacta'], y=df.iloc[:, 1], marker_color='#90A4AE',
            text=[f"{v/1e6:,.0f}MM" if v >= 1e6 else f"{v:,.0f}" for v in df.iloc[:, 1]],
            textposition="inside", insidetextanchor="middle", textfont=
