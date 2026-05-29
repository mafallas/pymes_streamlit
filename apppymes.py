import streamlit as st
import pandas as pd
import pyodbc
from streamlit_echarts import st_echarts

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================
st.set_page_config(
    page_title="Dashboard PYMES",
    layout="wide"
)

st.title("📊 Dashboard PYMES")
st.markdown("Visualización de resultados desde tabla consolidada")

# =====================================================
# CONEXIÓN Y CARGA DE DATOS
# =====================================================
@st.cache_data(ttl=3600)  # refresca cada hora
def get_data():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=CRIVBCOCREBD.cri.CORP.REDBAC.com,3025;"
        "DATABASE=MiBase;"
        "Trusted_Connection=yes;"
    )

    query = """
        SELECT
            TipoBase,
            Cantidad,
            Ofrecimiento
        FROM MiBase.dbo.ResultadoFinal
        ORDER BY TipoBase
    """

    df = pd.read_sql(query, conn)
    return df


df = get_data()

# =====================================================
# SIDEBAR – FILTROS
# =====================================================
st.sidebar.header("🔎 Filtros")

tipos_base = st.sidebar.multiselect(
    "Tipo Base",
    options=df["TipoBase"].unique(),
    default=df["TipoBase"].unique()
)

df_filtered = df[df["TipoBase"].isin(tipos_base)]

# =====================================================
# KPIs (TARJETAS SUPERIORES)
# =====================================================
total_registros = int(df_filtered["Cantidad"].sum())
total_ofrecimiento = round(df_filtered["Ofrecimiento"].sum(), 2)
total_tipos = df_filtered["TipoBase"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("Total Registros", total_registros)
col2.metric("Ofrecimiento (MM)", total_ofrecimiento)
col3.metric("Tipos de Base", total_tipos)

st.markdown("---")

# =====================================================
# GRÁFICO 1 – CANTIDAD POR TIPO BASE
# =====================================================
st.subheader("📌 Cantidad por Tipo Base")

option_cantidad = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category",
        "data": df_filtered["TipoBase"].tolist(),
        "axisLabel": {"rotate": 40}
    },
    "yAxis": {"type": "value"},
    "series": [
        {
            "data": df_filtered["Cantidad"].tolist(),
            "type": "bar",
            "itemStyle": {"color": "#5470C6"}
        }
    ]
}

st_echarts(option_cantidad, height="400px")

# =====================================================
# GRÁFICO 2 – OFRECIMIENTO POR TIPO BASE
# =====================================================
st.subheader("💰 Ofrecimiento por Tipo Base (MM)")

option_ofrecimiento = {
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category",
        "data": df_filtered["TipoBase"].tolist(),
        "axisLabel": {"rotate": 40}
    },
    "yAxis": {"type": "value"},
    "series": [
        {
            "data": df_filtered["Ofrecimiento"].tolist(),
            "type": "bar",
            "itemStyle": {"color": "#91CC75"}
        }
    ]
}

st_echarts(option_ofrecimiento, height="400px")

# =====================================================
# GRÁFICO 3 – PARTICIPACIÓN (PIE)
# =====================================================
st.subheader("📊 Participación por Tipo Base")

pie_data = [
    {"value": v, "name": k}
    for k, v in zip(df_filtered["Cantidad"], df_filtered["TipoBase"])
]

option_pie = {
    "tooltip": {"trigger": "item"},
    "series": [
        {
            "type": "pie",
            "radius": "60%",
            "data": pie_data,
            "emphasis": {
                "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                }
            }
        }
    ]
}

st_echarts(option_pie, height="400px")

# =====================================================
# TABLA DETALLE
# =====================================================
st.subheader("📋 Detalle de Resultados")

st.dataframe(df_filtered, use_container_width=True)