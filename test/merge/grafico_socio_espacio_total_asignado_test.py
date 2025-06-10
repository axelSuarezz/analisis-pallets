import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import locale
import numpy as np

# Localización para nombres de meses en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # Para Linux/Mac
except:
    locale.setlocale(locale.LC_TIME, 'spanish')  # Para Windows

# Configuración inicial de la página
st.set_page_config(
    layout="wide",
    page_title="Dashboard de Pallets",
    page_icon="📊"
)

# Carga de datos
@st.cache_data
def load_data():
    ruta = 'C:/Users/Sistemas/Desktop/pallets_cruzados_nuevo/test/merge/espacio_total_asignado_final.xlsx'
    df = pd.read_excel(ruta)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['mes_año'] = df['fecha'].dt.strftime('%B %Y').str.title()

        # Eliminar duplicados por socio+fecha
    df = df.drop_duplicates(subset=['id_socio', 'fecha'])
    
    
    
    return df

df = load_data()


# Sidebar con filtros
st.sidebar.header("🔍 Filtros")
comparar = st.sidebar.checkbox("🔄 Comparar dos socios")

# Función para manejar selección de socio
def get_socio_data(tipo_busqueda, valor):
    if tipo_busqueda == "Nombre del socio":
        return df[df['socio'] == valor]
    else:
        return df[df['id_socio'] == valor]

# Ordenar meses cronológicamente
meses_ordenados = sorted(df['mes_año'].unique(), key=lambda x: datetime.strptime(x, '%B %Y'))

if comparar:
    st.sidebar.markdown("**Comparar entre socios**")
    
    tipo_comparacion = st.sidebar.radio("Buscar socios por:", ["Nombre del socio", "ID del socio"], key='tipo_cmp')

    if tipo_comparacion == "Nombre del socio":
        socio_1 = st.sidebar.selectbox("Primer socio", sorted(df['socio'].unique()), key='cmp_1_nombre')
        socio_2 = st.sidebar.selectbox("Segundo socio", sorted(df['socio'].unique()), key='cmp_2_nombre')

        df_1 = df[df['socio'] == socio_1]
        df_2 = df[df['socio'] == socio_2]

    else:
        ids_float_excepciones = {11.111, 17.39, 25.63}

        def formatear_id(id_):
            return id_ if id_ in ids_float_excepciones else int(id_)

        id_options = df['id_socio'].unique()
        id_labels = {formatear_id(id_): id_ for id_ in id_options}
        id_mostrados = sorted(id_labels.keys())

        id_1 = st.sidebar.selectbox("Primer ID de socio", id_mostrados, key='cmp_1_id')
        id_2 = st.sidebar.selectbox("Segundo ID de socio", id_mostrados, key='cmp_2_id')

        socio_1 = df[df['id_socio'] == id_labels[id_1]]['socio'].iloc[0]
        socio_2 = df[df['id_socio'] == id_labels[id_2]]['socio'].iloc[0]

        df_1 = df[df['id_socio'] == id_labels[id_1]]
        df_2 = df[df['id_socio'] == id_labels[id_2]]

    mes_comparado = st.sidebar.selectbox("Mes para comparar", meses_ordenados, key='cmp_mes')
    df_1 = df_1[df_1['mes_año'] == mes_comparado].sort_values('fecha')
    df_2 = df_2[df_2['mes_año'] == mes_comparado].sort_values('fecha')

    st.subheader(f"📊 Comparativa entre {socio_1} y {socio_2} ({mes_comparado})")
    col1, col2 = st.columns(2)

    max_valor_y = max(
        df_1['pallets_iniciales'].max(), df_2['pallets_iniciales'].max(),
        df_1['espacio_total_asignado'].max(), df_2['espacio_total_asignado'].max()
    )

    def plot_comparacion(df_filtrado, socio_nombre, max_y):
        espacio = df_filtrado['espacio_total_asignado'].unique()[0]
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.barplot(data=df_filtrado, x='fecha', y='pallets_iniciales', ax=ax, color='#4C8BF5')
        ax.axhline(espacio, color='red', linestyle='--', label=f'Espacio asignado ({espacio})')
        ax.set_ylim(0, max_y)
        ax.set_title(f"{socio_nombre}", fontsize=12)
        ax.set_ylabel("Pallets")
        ax.set_xlabel("Fecha")
        ax.set_xticklabels([d.strftime('%d-%b') for d in df_filtrado['fecha']], rotation=45)
        ax.legend()
        return fig

    with col1:
        st.pyplot(plot_comparacion(df_1, socio_1, max_valor_y))
    with col2:
        st.pyplot(plot_comparacion(df_2, socio_2, max_valor_y))


else:
    # Sólo mostrar si NO se está comparando
    tipo_busqueda = st.sidebar.radio("Buscar por:", ["Nombre del socio", "ID del socio"])

    if tipo_busqueda == "Nombre del socio":
        valor_seleccionado = st.sidebar.selectbox(
            "Seleccionar socio", 
            sorted(df['socio'].unique()),
            key='socio_select'
        )
        socio_sel = valor_seleccionado.strip().title()
        ids_relacionados = df.loc[df['socio'] == socio_sel, 'id_socio'].unique()
        df_filtrado_base = df[df['id_socio'].isin(ids_relacionados)]
    else:
        ids_float_excepciones = {11.111, 17.39, 25.63}
        def formatear_id(id_):
            return id_ if id_ in ids_float_excepciones else int(id_)

        id_options = df['id_socio'].unique()
        id_labels = {formatear_id(id_): id_ for id_ in id_options}
        id_mostrados = sorted(id_labels.keys())

        id_mostrado = st.sidebar.selectbox("Seleccionar ID de socio", id_mostrados, key='id_select')
        valor_seleccionado = id_labels[id_mostrado]
        df_filtrado_base = df[df['id_socio'] == valor_seleccionado]

    mes_seleccionado = st.sidebar.selectbox("Seleccionar mes", meses_ordenados, key='mes_select')
    df_filtrado = df_filtrado_base[df_filtrado_base['mes_año'] == mes_seleccionado].drop_duplicates(subset=['id_socio', 'fecha']).sort_values(by='fecha')

    espacio_total = df_filtrado['espacio_total_asignado'].mode()
    if espacio_total.empty:
        espacio_total = 0
    else:
        espacio_total = espacio_total[0]

    # Con este bloque seguro:
    espacio_total_values = df_filtrado['espacio_total_asignado'].unique()
    if len(espacio_total_values) == 0:
        st.error("No hay datos de espacio asignado para este socio/mes")
        st.stop()
    elif len(espacio_total_values) > 1:
        st.warning(f"Multiples valores de espacio encontrados. Usando el promedio: {np.mean(espacio_total_values):.0f}")
    espacio_total = espacio_total_values[0] if len(espacio_total_values) == 1 else espacio_total_values.mean()

    socio_nombre = df_filtrado['socio'].iloc[0] if not df_filtrado.empty else "Desconocido"
    st.title(f"📦 Gestión de Pallets - {socio_nombre}")
    st.markdown(f"**Mes seleccionado:** {mes_seleccionado}")

    # Métricas clave
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Espacio total asignado", f"{espacio_total} pallets")
    with col2:
        avg_pallets = df_filtrado['pallets_iniciales'].mean()
        st.metric("Promedio diario de pallets", f"{avg_pallets:.1f}")

    # Gráfico principal
    st.subheader("📈 Evolución diaria de pallets vs espacio asignado")

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.set_style("whitegrid")
    sns.barplot(data=df_filtrado, x='fecha', y='pallets_iniciales', ax=ax, color='#4C8BF5', alpha=0.8)
    ax.axhline(espacio_total, color='#FF4B4B', linestyle='--', linewidth=2,
               label=f"Espacio asignado ({espacio_total} pallets)")
    ax.set_ylabel("Cantidad de Pallets", fontsize=12)
    ax.set_xlabel("Fecha", fontsize=12)
    ax.set_title(f"Pallets diarios vs Espacio Asignado - {socio_nombre} ({mes_seleccionado})", fontsize=14, pad=20)
    ax.set_xticklabels([date.strftime('%d-%b') for date in df_filtrado['fecha']])
    plt.xticks(rotation=45)
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())}", 
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', 
                    xytext=(0, 5), textcoords='offset points', fontsize=9)
    ax.legend(loc='upper right', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)

    # Detalles adicionales
    st.markdown("### 📋 Detalles adicionales")
    df_mostrar = (
        df_filtrado[['fecha', 'pallets_iniciales', 'espacio_total_asignado']]
        .copy()
        .assign(fecha=lambda x: x['fecha'].dt.date)
        .reset_index(drop=True)
    )
    st.dataframe(
        df_mostrar.rename(columns={
            'fecha': '📅 Fecha',
            'pallets_iniciales': '📦 Pallets Iniciales',
            'espacio_total_asignado': '🚀 Espacio Asignado'
        }).style.format({
            '📦 Pallets Iniciales': '{:.0f}',
            '🚀 Espacio Asignado': '{:.0f}'
        }),
        height=300
    )

# CSS para centrar las columnas
st.markdown("""
<style>
    .dataframe th {font-weight: bold !important; text-align: center !important;}
    .dataframe td {text-align: center !important;}
</style>
""", unsafe_allow_html=True)
