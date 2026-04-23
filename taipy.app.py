import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Monitor Financiero", layout="wide", initial_sidebar_state="collapsed")
st_autorefresh(interval=300000, key="datarefresh")

# CSS: Mantenemos el tamaño que te gustó con fondo claro
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    .block-container { padding: 1rem !important; background-color: #f8f9fc; }
    .grafico-titulo { color: #2b5dda; font-family: 'Poppins'; font-size: 1.2vw; font-weight: 400; margin-bottom: 5px; }
    .chart-box { border: 1px solid #2b5dda; border-radius: 12px; background-color: white; padding: 10px; margin-bottom: 10px; height: 100%; }
    </style>
    """, unsafe_allow_html=True)

ruta = "Data_Situacional_Ejemplo.xlsx"

# CARGA DE DATOS MEJORADA
def load_data(sheet):
    try:
        df = pd.read_excel(ruta, sheet_name=sheet)
        return df.dropna(how='all').reset_index(drop=True)
    except:
        return pd.DataFrame()

# --- FILA 1: GRÁFICOS GRANDES ---
c1, c2 = st.columns(2)

with c1:
    df_raw = load_data('Liquidez Monetaria')
    
    # Verificamos que el archivo tenga datos
    if not df_raw.empty:
        # En lugar de usar índices numéricos [6], buscamos por nombre o posición real disponible
        # Asumiremos que la fecha es la col 0 y los montos están en la última o penúltima
        cols = df_raw.columns.tolist()
        
        # Limpieza: eliminamos filas donde la columna de datos principal sea NaN
        # Intentamos usar la columna 6 si existe, si no, la última columna con datos
        col_datos = cols[6] if len(cols) > 6 else cols[-1]
        df = df_raw.dropna(subset=[col_datos]).tail(6)
        
        if not df.empty:
            st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
            head_col1, head_col2, head_col3 = st.columns([1.8, 1, 1])
            
            with head_col1:
                st.markdown('<p class="grafico-titulo">Liquidez Monetaria</p>', unsafe_allow_html=True)
            
            # Valores para botones (usando la columna identificada)
            ultimo_valor = df[col_datos].iloc[-1]
            promedio_valor = df[col_datos].mean()
            
            # Variación (columna siguiente a la de datos, o calculada)
            col_var = cols[7] if len(cols) > 7 else None
            var_ultima = df[col_var].iloc[-1] if col_var else 0

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

            # GRÁFICO PLOTLY
            df['Fecha_F'] = df[cols[0]].dt.strftime('%d-%m-%Y')
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Fecha_F'], y=df[col_datos], mode='lines+markers+text',
                text=[f"{v/1e6:,.0f}MM" for v in df[col_datos]],
                textposition="top center", textfont=dict(color='black', size=12),
                line=dict(color='#2b5dda', width=1.5), marker=dict(color='#fd941c', size=10)
            ))
            
            fig.update_layout(
                plot_bgcolor='white', height=320, showlegend=False,
                margin=dict(l=10, r=10, t=10, b=10),
                yaxis=dict(showgrid=True, gridcolor='#eee', tickfont=dict(color='black', size=10), linecolor='gray', linewidth=1),
                xaxis=dict(type='category', showgrid=False, tickfont=dict(color='black', size=10), linecolor='gray', linewidth=1)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("El archivo Excel está vacío o no se pudo leer correctamente.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    df_raw = load_data('Resev. Internacionales $')
    df = df_raw.dropna(subset=[df_raw.columns[3]]).tail(6)
    
    if not df.empty:
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        head_col1, head_col2, head_col3 = st.columns([1.8, 1, 1])
        
        with head_col1:
            st.markdown('<p class="grafico-titulo">Reservas Internacionales $</p>', unsafe_allow_html=True)
        
        # --- CORRECCIÓN DEL ERROR DE ÍNDICE ---
        idx_max = df.iloc[:, 3].idxmax()
        idx_min = df.iloc[:, 3].idxmin()
        
        max_val = df.loc[idx_max, df.columns[3]]
        min_val = df.loc[idx_min, df.columns[3]]
        
        # Buscamos la variación en la columna 4 usando el índice real detectado
        var_max = df.loc[idx_max, df.columns[4]] if df.shape[1] > 4 else 0
        var_min = df.loc[idx_min, df.columns[4]] if df.shape[1] > 4 else 0
        # ---------------------------------------

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
        x_data = df['Fecha_Exacta']
        y_data = df.iloc[:, 3]
        y_var = df.iloc[:, 4] if df.shape[1] > 4 else y_data.pct_change()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_data, y=y_data, fill='tozeroy', mode='lines+markers+text',
            text=[f"{v:,.1f}MM" for v in y_data], 
            textposition="top center", textfont=dict(color='black', size=12),
            fillcolor='rgba(0,0,0,0)', line=dict(color='#6A1B9A', width=1), marker=dict(color='#6A1B9A', size=10)
        ))
        fig.add_trace(go.Scatter(
            x=x_data, y=y_var, mode='lines+markers+text',
            text=[f"{v*100:.2f}%" if pd.notnull(v) else "" for v in y_var],
            textposition="bottom center", textfont=dict(color='black', size=12),
            line=dict(color='#fd941c', width=1, dash='dot'), marker=dict(color='#fd941c', size=10),
            yaxis='y2'
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
        # VALIDACIÓN OBLIGATORIA
        df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
        x_data = df['Fecha_Exacta']
        
        y_data = df.iloc[:, 1]
        y_var = df.iloc[:, 2] if df.shape[1] > 2 else y_data.pct_change()

        fig = go.Figure()

        # 1. Trazo Principal: Barras (Montos en la MITAD en BLANCO)
        fig.add_trace(go.Bar(
            x=x_data, 
            y=y_data, 
            name='Bases Monetarias',
            marker_color='#90A4AE',
            # Texto en blanco, delgado (sin negrita), tamaño 10
            text=[f"{v/1e6:,.0f}MM" if v >= 1e6 else f"{v:,.0f}" for v in y_data],
            textposition="inside",
            insidetextanchor="middle", # Lo coloca justo en la mitad de la barra
            textfont=dict(color='white', size=10),
        ))

        # 2. Línea de Tendencia: Variación % (Cyan y Gris Dash)
        fig.add_trace(go.Scatter(
            x=x_data, 
            y=y_var, 
            mode='lines+markers+text',
            name='Variación %',
            # Montos en CYAN resaltante
            text=[f"{v*100:.2f}%" if pd.notnull(v) else "" for v in y_var],
            textposition="bottom center", 
            textfont=dict(color='#fd941c', size=12), # Cyan eléctrico para resaltar
            line=dict(color="#A9E4EE", width=1, dash='dot'), # Gris delgado y entrecortado
            marker=dict(color="#fd941c", size=8),
            yaxis='y2'
        ))

        # 3. Configuración de Ejes Negro Intenso
        fig.update_layout(
            plot_bgcolor='white', 
            height=200, 
            showlegend=False,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#eee', 
                tickfont=dict(color='black', size=10),
                linecolor='gray',
                linewidth=1,
                zeroline=False
            ),
            xaxis=dict(
                type='category',
                showgrid=False, 
                tickfont=dict(color='black', size=9),
                linecolor='gray',
                linewidth=1
            ),
            yaxis2=dict(
                overlaying='y',
                side='right',
                showgrid=False,
                showticklabels=False,
                zeroline=False
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
    
with c4:
    st.markdown('<div class="chart-box"><p class="grafico-titulo" style="font-size:0.9vw;">Reservas Bs.</p>', unsafe_allow_html=True)
    # Cargamos la hoja de Liquidez pero enfocada en Reservas Bs.
    df = load_data('Liquidez Monetaria').tail(6)
    
    if not df.empty:
        # VALIDACIÓN OBLIGATORIA: Fechas exactas del Excel
        df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
        x_data = df['Fecha_Exacta']
        
        # Asumimos que los montos de Reservas Bs. están en la columna 6
        y_data = df.iloc[:, 6]
        # Variación (Columna 7 o cálculo)
        y_var = df.iloc[:, 7] if df.shape[1] > 7 else y_data.pct_change()

        fig = go.Figure()

        # 1. Trazo Principal: Barras Verdes (Montos en la MITAD en BLANCO)
        fig.add_trace(go.Bar(
            x=x_data, 
            y=y_data, 
            name='Reservas Bs.',
            marker_color="#42698d", # Tu verde original
            # Texto blanco, delgado, tamaño 10
            text=[f"{v/1e6:,.0f}MM" if v >= 1e6 else f"{v:,.0f}" for v in y_data],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color='white', size=10),
        ))

        # 2. Línea de Tendencia: Variación % (Cyan y Gris Dash)
        fig.add_trace(go.Scatter(
            x=x_data, 
            y=y_var, 
            mode='lines+markers+text',
            name='Variación %',
            # Montos en CYAN resaltante debajo del punto
            text=[f"{v*100:.2f}%" if pd.notnull(v) else "" for v in y_var],
            textposition="bottom center", 
            textfont=dict(color='#fd941c', size=12),
            line=dict(color='#00FFFF', width=1, dash='dot'), # Gris delgado dash
            marker=dict(color='#fd941c', size=8),
            yaxis='y2'
        ))

        # 3. Configuración de Ejes Negro Intenso
        fig.update_layout(
            plot_bgcolor='white', 
            height=200, 
            showlegend=False,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#eee', 
                tickfont=dict(color='black', size=10),
                linecolor='gray', # Gris intenso
                linewidth=1,
                zeroline=False
            ),
            xaxis=dict(
                type='category',
                showgrid=False, 
                tickfont=dict(color='black', size=9),
                linecolor='gray', # Gris intenso
                linewidth=1
            ),
            yaxis2=dict(
                overlaying='y',
                side='right',
                showgrid=False,
                showticklabels=False,
                zeroline=False
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with c5:
    st.markdown('<div class="chart-box"><p class="grafico-titulo" style="font-size:0.9vw;">Overnight Diaria</p>', unsafe_allow_html=True)
    # Cargamos los últimos 10 registros
    df = load_data('Tasa Overnight Diaria').tail(10)
    
    if not df.empty:
        # VALIDACIÓN OBLIGATORIA: Columna A para el eje X (Fechas exactas)
        df['Fecha_Exacta'] = df.iloc[:, 0].dt.strftime('%d-%m-%Y')
        x_data = df['Fecha_Exacta']
        
        # OBLIGATORIO: Columna H para el eje Y (Valores de la tasa)
        # Usamos .iloc[:, 7] ya que la columna H es la octava columna (índice 7)
        y_data = df.iloc[:, 7]

        fig = go.Figure()

        # 1. Trazo Principal: Línea Azul con Valores idénticos a Columna H
        fig.add_trace(go.Scatter(
            x=x_data, 
            y=y_data, 
            mode='lines+markers+text',
            name='Tasa Overnight',
            # Se usa el valor de la columna H tal cual viene en el Excel
            text=[f"{v}%" for v in y_data],
            textposition="top center",
            textfont=dict(color='black', size=10),
            line=dict(color='#2b5dda', width=2), 
            marker=dict(color='#2b5dda', size=6)
        ))

        # 2. Configuración de Ejes NEGRO INTENSO
        fig.update_layout(
            plot_bgcolor='white', 
            height=200, 
            showlegend=False,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#eee', 
                tickfont=dict(color='black', size=10),
                linecolor='gray',
                linewidth=1,
                zeroline=False,
                # Margen dinámico para que las etiquetas de la Columna H no choquen
                range=[y_data.min() * 0.7, y_data.max() * 1.3]
            ),
            xaxis=dict(
                type='category', 
                showgrid=False, 
                tickfont=dict(color='black', size=9),
                linecolor='gray',
                linewidth=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="chart-box"><p class="grafico-titulo" style="font-size:0.9vw;">Overnight Mensual</p>', unsafe_allow_html=True)
    df = load_data('Tasa Overnight Mensual')
    
    if not df.empty:
        # 1. LIMPIEZA: Quitamos filas vacías para eliminar la columna "nan"
        df = df.dropna(subset=[df.columns[0], df.columns[1]]).tail(4)
        
        # 2. EJE X: Meses (Columna A)
        df['Fecha_Exacta'] = df.iloc[:, 0].astype(str)
        x_data = df['Fecha_Exacta']
        
        # 3. EJE Y: Montos (Columna B / Índice 1)
        y_data = pd.to_numeric(df.iloc[:, 1], errors='coerce')

        fig = go.Figure()

        # 4. Trazo Principal: Barras con montos formateados como enteros con miles
        fig.add_trace(go.Bar(
            x=x_data, 
            y=y_data, 
            marker_color='#2471A3',
            # FORMATEO: :.0f para número entero y :, para separador de miles
            text=[f"{v:,.0f}" if pd.notnull(v) else "" for v in y_data],
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color='white', size=11),
        ))

        # 5. Configuración de Ejes NEGRO INTENSO
        fig.update_layout(
            plot_bgcolor='white', 
            height=200, 
            showlegend=False,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(
                showgrid=True, 
                gridcolor='#eee', 
                tickfont=dict(color='black', size=11),
                linecolor='gray', # Gris fuerte
                linewidth=1,
                zeroline=False
            ),
            xaxis=dict(
                type='category', 
                showgrid=False, 
                tickfont=dict(color='black', size=11),
                linecolor='gray', # Gris fuerte
                linewidth=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)
