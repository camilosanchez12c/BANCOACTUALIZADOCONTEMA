"""
Dashboard de Prediccion de Tasas de Credito de Consumo
Entidades Bancarias Colombianas (2023-2026)
Con interactividad tipo Power BI y crossfiltering
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data import (
    get_predicciones_df,
    get_metricas_df,
    get_criterio_df,
    get_historico_df,
    get_historico_total_df,
    get_ranking_df,
    get_bancos,
    get_rangos,
    get_meses,
    get_niveles,
    get_kpis,
    get_mejores_modelos_df,
)

# =============================================================================
# CONFIGURACION DE PAGINA
# =============================================================================
st.set_page_config(
    page_title="📊 Prediccion Tasas de Credito - Colombia",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# ESTILOS CSS PERSONALIZADOS
# =============================================================================
st.markdown("""
<style>
    /* Fondo oscuro */
    .stApp {
        background-color: #0a0a0f;
    }
    
    /* Cards KPI */
    .kpi-card {
        background: linear-gradient(135deg, rgba(20, 20, 35, 0.9) 0%, rgba(15, 15, 25, 0.95) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 1.25rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
        text-align: center;
    }
    
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .kpi-value-green {
        font-size: 2rem;
        font-weight: 700;
        color: #22c55e;
        margin: 0;
    }
    
    .kpi-value-red {
        font-size: 2rem;
        font-weight: 700;
        color: #ef4444;
        margin: 0;
    }
    
    .kpi-value-green {
        font-size: 2rem;
        font-weight: 700;
        color: #22c55e;
        margin: 0;
    }
    
    .kpi-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.5rem;
    }
    
    /* Titulo principal */
    .main-title {
        font-size: 2.25rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f8fafc 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    
    .subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    .badge-green {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
        margin-left: 1rem;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
        border-right: 1px solid rgba(56, 189, 248, 0.1);
    }
    
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #e2e8f0 !important;
        font-weight: 500;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(15, 15, 25, 0.5);
        border-radius: 12px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: #94a3b8;
        padding: 12px 24px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(129, 140, 248, 0.2) 100%);
        color: #f8fafc;
    }
    
    /* Section headers */
    .section-header {
        color: #f8fafc;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(56, 189, 248, 0.3);
    }
    
    /* Ranking cards */
    .ranking-card {
        background: linear-gradient(135deg, rgba(20, 20, 35, 0.9) 0%, rgba(15, 15, 25, 0.95) 100%);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .ranking-card:hover {
        border-color: rgba(56, 189, 248, 0.5);
        transform: translateY(-2px);
    }
    
    .ranking-position {
        font-size: 0.7rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .ranking-banco {
        font-size: 0.9rem;
        font-weight: 600;
        color: #f8fafc;
        margin: 0.5rem 0;
    }
    
    .ranking-tasa {
        font-size: 1.25rem;
        font-weight: 700;
        color: #38bdf8;
    }
    
    /* Info box */
    .info-box {
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 8px;
        padding: 1rem;
        color: #94a3b8;
        font-size: 0.85rem;
    }
    
    /* Criterio cards */
    .criterio-card {
        background: linear-gradient(135deg, rgba(20, 20, 35, 0.9) 0%, rgba(15, 15, 25, 0.95) 100%);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .criterio-nivel {
        font-size: 0.75rem;
        color: #22c55e;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }
    
    .criterio-modelo {
        font-size: 1rem;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 0.25rem;
    }
    
    .criterio-metricas {
        font-size: 0.85rem;
        color: #94a3b8;
    }
    
    /* Filtros activos */
    .filtro-activo {
        background: rgba(129, 140, 248, 0.2);
        color: #818cf8;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        margin: 0.25rem 0;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# CARGA DE DATOS
# =============================================================================
@st.cache_data
def load_data():
    predicciones = get_predicciones_df()
    metricas = get_metricas_df()
    criterio = get_criterio_df()
    historico = get_historico_df()
    historico_total = get_historico_total_df()
    ranking = get_ranking_df()
    bancos = get_bancos()
    rangos = get_rangos()
    meses = get_meses()
    niveles = get_niveles()
    kpis = get_kpis()
    mejores_modelos = get_mejores_modelos_df()
    return predicciones, metricas, criterio, historico, historico_total, ranking, bancos, rangos, meses, niveles, kpis, mejores_modelos


predicciones_df, metricas_df, criterio_df, historico_df, historico_total_df, ranking_df, BANCOS, RANGOS_MONTO, MESES, NIVELES, KPIS, mejores_modelos_df = load_data()


# =============================================================================
# INICIALIZAR SESSION STATE
# =============================================================================
if "selected_banco" not in st.session_state:
    st.session_state.selected_banco = "Todos"
if "selected_rango" not in st.session_state:
    st.session_state.selected_rango = "Todos"
if "selected_mes" not in st.session_state:
    st.session_state.selected_mes = "Todos"


# =============================================================================
# SIDEBAR - FILTROS
# =============================================================================
with st.sidebar:
    st.markdown("### Filtros")
    st.markdown("---")

    # Boton limpiar filtros - usa callback para resetear
    if st.button("Limpiar Filtros", use_container_width=True, key="btn_limpiar"):
        st.session_state["banco_filter"] = "Todos"
        st.session_state["rango_filter"] = "Todos"
        st.session_state["mes_filter"] = "Todos"
        st.session_state.selected_banco = "Todos"
        st.session_state.selected_rango = "Todos"
        st.session_state.selected_mes = "Todos"
        st.rerun()

    st.markdown("")

    # Filtro Banco
    bancos_opts = ["Todos"] + BANCOS
    banco_sel = st.selectbox(
        "Seleccionar Entidad Bancaria", 
        bancos_opts, 
        index=bancos_opts.index(st.session_state.selected_banco) if st.session_state.selected_banco in bancos_opts else 0,
        key="banco_filter"
    )
    st.session_state.selected_banco = banco_sel

    # Filtro Rango
    rangos_opts = ["Todos"] + RANGOS_MONTO
    rango_sel = st.selectbox(
        "Seleccionar Rango de Monto", 
        rangos_opts, 
        index=rangos_opts.index(st.session_state.selected_rango) if st.session_state.selected_rango in rangos_opts else 0,
        key="rango_filter"
    )
    st.session_state.selected_rango = rango_sel

    # Filtro Mes (para historico)
    meses_opts = ["Todos"] + MESES
    mes_sel = st.selectbox(
        "Seleccionar Mes (Historico)", 
        meses_opts, 
        index=meses_opts.index(st.session_state.selected_mes) if st.session_state.selected_mes in meses_opts else 0,
        key="mes_filter"
    )
    st.session_state.selected_mes = mes_sel

    st.markdown("---")

    # Filtros activos
    st.markdown("### Filtros Activos")
    filtros_activos = []
    if banco_sel != "Todos":
        filtros_activos.append(f"Banco: {banco_sel}")
    if rango_sel != "Todos":
        filtros_activos.append(f"Rango: {rango_sel[:30]}")
    if mes_sel != "Todos":
        filtros_activos.append(f"Mes: {mes_sel}")

    if filtros_activos:
        for f in filtros_activos:
            st.markdown(f'<span class="filtro-activo">{f}</span>', unsafe_allow_html=True)
    else:
        st.markdown("*Ninguno - mostrando todos los datos*")

    st.markdown("---")
    periodo = KPIS.get("periodo", "Oct 2023 - Feb 2026")
    st.markdown(f"""
    <div class="info-box">
    Dashboard de prediccion de tasas de credito de consumo en Colombia.<br><br>
    <strong>Datos:</strong> Superfinanciera<br>
    <strong>Periodo:</strong> {periodo}<br>
    <strong>Prediccion:</strong> Mayo 2026 (T+3)
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# APLICAR FILTROS
# =============================================================================
pred_filtradas = predicciones_df.copy()

if banco_sel != "Todos":
    pred_filtradas = pred_filtradas[pred_filtradas["banco"] == banco_sel]
if rango_sel != "Todos":
    pred_filtradas = pred_filtradas[pred_filtradas["rango_monto"] == rango_sel]

# Filtro mes aplicado al historico
hist_filtrado = historico_df.copy()
hist_total_filtrado = historico_total_df.copy()
if banco_sel != "Todos":
    hist_filtrado = hist_filtrado[hist_filtrado["banco"] == banco_sel]
if mes_sel != "Todos":
    hist_filtrado = hist_filtrado[hist_filtrado["mes"] == mes_sel]
    hist_total_filtrado = hist_total_filtrado[hist_total_filtrado["mes"] == mes_sel]


# =============================================================================
# HEADER PRINCIPAL
# =============================================================================
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.markdown('<h1 class="main-title">Predicción de Tasas de Credito de Consumo</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analisis y prediccion de tasas efectivas mensuales en entidades bancarias colombianas (2023-2026) <span class="badge-green">● Datos: Superfinanciera de Colombia</span></p>', unsafe_allow_html=True)


# =============================================================================
# KPIs PRINCIPALES
# =============================================================================
n_pred = len(pred_filtradas)
tasa_prom = pred_filtradas["prediccion_tasa_t3"].mean() if n_pred > 0 else 0
tasa_min = pred_filtradas["prediccion_tasa_t3"].min() if n_pred > 0 else 0
tasa_max = pred_filtradas["prediccion_tasa_t3"].max() if n_pred > 0 else 0
total_cred = pred_filtradas["total_creditos_base"].sum() if n_pred > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value">{n_pred}</p>
        <p class="kpi-label">Predicciones</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value">{tasa_prom:.2f}%</p>
        <p class="kpi-label">Tasa Promedio</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value-green">{tasa_min:.2f}%</p>
        <p class="kpi-label">Tasa Minima</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value-red">{tasa_max:.2f}%</p>
        <p class="kpi-label">Tasa Maxima</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value">{total_cred:,.0f}</p>
        <p class="kpi-label">Total Creditos</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# =============================================================================
# TABS PRINCIPALES
# =============================================================================
tab1, tab3, tab4 = st.tabs([
    "🏆 Ranking de Bancos",
    "🔬 Comparacion de Modelos",
    "📋 Datos y Estadisticas"
])


# =============================================================================
# TAB 1: RANKING DE BANCOS
# =============================================================================
with tab1:
    st.markdown('<div class="section-header">Ranking de Bancos por Tasa Predicha (Mayo 2026)</div>', unsafe_allow_html=True)
    
    # Opciones de ordenamiento
    col_ord1, col_ord2 = st.columns([3, 1])
    with col_ord2:
        orden = st.selectbox("Ordenar", ["Ascendente (menor tasa)", "Descendente (mayor tasa)"], key="orden_rank")
    
    ascending = orden == "Ascendente (menor tasa)"
    
    # Calcular ranking
    rank_calc = pred_filtradas.groupby("banco").agg({
        "prediccion_tasa_t3": "mean",
        "total_creditos_base": "sum",
        "tasa_base": "mean"
    }).reset_index()
    rank_calc = rank_calc.sort_values("prediccion_tasa_t3", ascending=ascending).reset_index(drop=True)
    rank_calc["posicion"] = range(1, len(rank_calc) + 1)
    
    # Top 4 cards
    if len(rank_calc) >= 4:
        cols = st.columns(4)
        medals = ["🥇", "🥈", "🥉", "4️⃣"]
        for i, row in rank_calc.head(4).iterrows():
            with cols[i]:
                st.markdown(f"""
                <div class="ranking-card">
                    <div class="ranking-position">{medals[i]} #{row['posicion']}</div>
                    <div class="ranking-banco">{row['banco']}</div>
                    <div class="ranking-tasa">{row['prediccion_tasa_t3']:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grafico de barras horizontales
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("#### Tasa Promedio Predicha por Banco")
        
        # Color por rango de tasa
        def get_color(tasa):
            if tasa < 19:
                return "#22c55e"  # verde
            elif tasa < 22:
                return "#fbbf24"  # amarillo
            elif tasa < 24:
                return "#f97316"  # naranja
            else:
                return "#ef4444"  # rojo
        
        rank_calc["color"] = rank_calc["prediccion_tasa_t3"].apply(get_color)
        
        fig_rank = go.Figure()
        fig_rank.add_trace(go.Bar(
            x=rank_calc["prediccion_tasa_t3"],
            y=rank_calc["banco"],
            orientation="h",
            marker_color=rank_calc["color"],
            text=rank_calc["prediccion_tasa_t3"].apply(lambda x: f"{x:.2f}%"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Tasa: %{x:.2f}%<extra></extra>"
        ))
        fig_rank.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            height=500,
            margin=dict(l=0, r=50, t=10, b=0),
            xaxis=dict(title="Tasa Predicha (%)", gridcolor="rgba(148, 163, 184, 0.1)"),
            yaxis=dict(categoryorder="total ascending" if ascending else "total descending"),
        )
        
        clicked = st.plotly_chart(fig_rank, use_container_width=True, key="rank_chart", on_select="rerun")
        
        if clicked and clicked.selection and clicked.selection.points:
            point = clicked.selection.points[0]
            if "y" in point:
                clicked_banco = point["y"]
                if clicked_banco != st.session_state.selected_banco:
                    st.session_state.selected_banco = clicked_banco
                    st.rerun()
    
    with col_g2:
        st.markdown("#### Volumen de Creditos por Banco")
        
        fig_vol = px.bar(
            rank_calc.sort_values("total_creditos_base", ascending=True),
            x="total_creditos_base",
            y="banco",
            orientation="h",
            color="total_creditos_base",
            color_continuous_scale=["#818cf8", "#38bdf8", "#22c55e"],
        )
        fig_vol.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            height=500,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(title="Total Creditos", gridcolor="rgba(148, 163, 184, 0.1)"),
        )
        st.plotly_chart(fig_vol, use_container_width=True)
    
    # Comparacion Tasa Base vs Predicha
    st.markdown("#### Comparacion: Tasa Base vs Tasa Predicha")
    
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name="Tasa Base (Feb 2026)", x=rank_calc["banco"], y=rank_calc["tasa_base"], marker_color="#64748b"))
    fig_comp.add_trace(go.Bar(name="Tasa Predicha (May 2026)", x=rank_calc["banco"], y=rank_calc["prediccion_tasa_t3"], marker_color="#38bdf8"))
    fig_comp.update_layout(
        barmode="group",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(tickangle=-45, gridcolor="rgba(148, 163, 184, 0.1)"),
        yaxis=dict(title="Tasa (%)", gridcolor="rgba(148, 163, 184, 0.1)"),
        margin=dict(l=0, r=0, t=30, b=100)
    )
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Distribucion por Rango de Monto
    st.markdown("#### Distribucion por Rango de Monto")
    
    rango_agg = pred_filtradas.groupby("rango_monto").agg({
        "prediccion_tasa_t3": "mean",
        "total_creditos_base": "sum"
    }).reset_index()
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        fig_rango = px.bar(
            rango_agg.sort_values("prediccion_tasa_t3"),
            x="rango_monto",
            y="prediccion_tasa_t3",
            color="prediccion_tasa_t3",
            color_continuous_scale=["#22c55e", "#fbbf24", "#ef4444"],
            title="Tasa Promedio por Rango"
        )
        fig_rango.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            height=300,
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_tickangle=-45,
            margin=dict(l=0, r=0, t=40, b=100)
        )
        
        clicked_rango = st.plotly_chart(fig_rango, use_container_width=True, key="rango_chart", on_select="rerun")
        
        if clicked_rango and clicked_rango.selection and clicked_rango.selection.points:
            point = clicked_rango.selection.points[0]
            if "x" in point:
                clicked_rango_val = point["x"]
                if clicked_rango_val != st.session_state.selected_rango:
                    st.session_state.selected_rango = clicked_rango_val
                    st.rerun()
    
    with col_r2:
        fig_pie = px.pie(
            rango_agg,
            values="total_creditos_base",
            names="rango_monto",
            title="Distribucion de Creditos",
            color_discrete_sequence=["#38bdf8", "#818cf8", "#c084fc", "#f472b6", "#22c55e", "#fbbf24"]
        )
        fig_pie.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            height=300,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Tabla de predicciones
    st.markdown("#### Tabla de Predicciones")
    
    col_sort, col_order = st.columns([2, 1])
    with col_sort:
        sort_col = st.selectbox("Ordenar por", ["prediccion_tasa_t3", "banco", "rango_monto", "total_creditos_base", "variacion"], key="sort_pred")
    with col_order:
        sort_order = st.selectbox("Orden", ["Ascendente", "Descendente"], key="order_pred")
    
    tabla = pred_filtradas[["banco", "rango_monto", "tasa_base", "prediccion_tasa_t3", "variacion", "nivel_usado", "total_creditos_base"]].copy()
    
    # Mapeo de columnas originales a nombres de display
    col_map = {
        "prediccion_tasa_t3": "Prediccion",
        "banco": "Banco",
        "rango_monto": "Rango de Monto",
        "total_creditos_base": "Creditos",
        "variacion": "Variacion (pp)",
        "tasa_base": "Tasa Base",
        "nivel_usado": "Nivel"
    }
    
    # Ordenar antes de renombrar
    sort_col_real = sort_col if sort_col in tabla.columns else "prediccion_tasa_t3"
    tabla = tabla.sort_values(sort_col_real, ascending=(sort_order == "Ascendente"))
    
    # Ahora renombrar para display
    tabla.columns = ["Banco", "Rango de Monto", "Tasa Base", "Prediccion", "Variacion (pp)", "Nivel", "Creditos"]
    
    st.dataframe(tabla, use_container_width=True, height=400)

#este por ahora no se va a usar poqruqe al momento de subir los cambios 
#a git hub es demasiado pesado los 2 archivos que tienen la data cruda


# =============================================================================
# TAB 3: COMPARACION DE MODELOS
# =============================================================================
with tab3:
    st.markdown('<div class="section-header">Comparacion de Modelos</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <strong>Que significa esto?</strong> Probamos diferentes modelos de prediccion y comparamos su precision.
    <br><strong>R2</strong> = Que tan bien predice el modelo (1.0 = perfecto, 0 = malo)
    <br><strong>MAE</strong> = Error promedio en puntos porcentuales (menor es mejor)
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Resumen simple: Mejor modelo general
    mejor_modelo = criterio_df.loc[criterio_df["r2_recomendado"].idxmax()]
    
    st.markdown("#### Mejor Modelo General")
    st.markdown(f"""
    <div class="kpi-card" style="text-align: center; padding: 20px;">
        <p style="font-size: 1.5rem; color: #38bdf8; margin: 0;">{mejor_modelo['modelo_recomendado']}</p>
        <p style="font-size: 0.9rem; color: #94a3b8; margin: 5px 0;">Precision (R2): {mejor_modelo['r2_recomendado']:.2%}</p>
        <p style="font-size: 0.9rem; color: #94a3b8; margin: 0;">Error promedio: {mejor_modelo['mae_recomendado']:.2f} puntos</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grafico simple: Comparacion de R2 de modelos
    st.markdown("#### Precision de los Modelos (R2)")
    
    col_m1, col_m2 = st.columns([3, 1])
    with col_m2:
        orden_r2 = st.selectbox("Ordenar", ["Mayor a menor", "Menor a mayor"], key="orden_r2")
    
    # Agrupar por modelo y calcular R2 promedio
    modelo_resumen = metricas_df.groupby("modelo").agg({"r2": "mean", "mae": "mean"}).reset_index()
    modelo_resumen = modelo_resumen.sort_values("r2", ascending=(orden_r2 == "Menor a mayor"))
    
    fig_r2 = px.bar(
        modelo_resumen,
        x="modelo",
        y="r2",
        color_discrete_sequence=["#38bdf8"]
    )
    fig_r2.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        height=350,
        showlegend=False,
        xaxis=dict(title="Modelo", gridcolor="rgba(148, 163, 184, 0.1)", tickangle=-45),
        yaxis=dict(title="Precision (R2)", gridcolor="rgba(148, 163, 184, 0.1)"),
        margin=dict(l=0, r=0, t=10, b=100)
    )
    st.plotly_chart(fig_r2, use_container_width=True)
    
    # Grafico MAE por modelo (simplificado)
    st.markdown("#### Error de los Modelos (MAE)")
    st.markdown("*Menor error = mejor modelo*")
    
    col_m3, col_m4 = st.columns([3, 1])
    with col_m4:
        orden_mae = st.selectbox("Ordenar", ["Menor a mayor", "Mayor a menor"], key="orden_mae")
    
    # Usar el mismo resumen de modelos
    modelo_resumen_mae = modelo_resumen.sort_values("mae", ascending=(orden_mae == "Menor a mayor"))
    
    fig_mae = px.bar(
        modelo_resumen_mae,
        x="modelo",
        y="mae",
        color_discrete_sequence=["#f472b6"]
    )
    fig_mae.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8",
        height=350,
        showlegend=False,
        xaxis=dict(title="Modelo", gridcolor="rgba(148, 163, 184, 0.1)", tickangle=-45),
        yaxis=dict(title="Error (MAE)", gridcolor="rgba(148, 163, 184, 0.1)"),
        margin=dict(l=0, r=0, t=10, b=100)
    )
    st.plotly_chart(fig_mae, use_container_width=True)
    
    # Tabla simplificada
    st.markdown("#### Resumen de Modelos")
    
    tabla_simple = modelo_resumen.copy()
    tabla_simple["r2"] = tabla_simple["r2"].apply(lambda x: f"{x:.2%}")
    tabla_simple["mae"] = tabla_simple["mae"].apply(lambda x: f"{x:.2f}")
    tabla_simple.columns = ["Modelo", "Precision (R2)", "Error (MAE)"]
    tabla_simple = tabla_simple.sort_values("Precision (R2)", ascending=False)
    
    st.dataframe(tabla_simple, use_container_width=True, height=300)


# =============================================================================
# TAB 4: DATOS Y ESTADISTICAS
# =============================================================================
with tab4:
    st.markdown('<div class="section-header">Datos y Estadisticas</div>', unsafe_allow_html=True)
    
    # Mostrar filtros activos
    if banco_sel != "Todos" or rango_sel != "Todos":
        st.markdown(f"**Filtros aplicados:** {'Banco: ' + banco_sel if banco_sel != 'Todos' else ''} {'| Rango: ' + rango_sel[:30] if rango_sel != 'Todos' else ''}")
    
    # Resumen estadistico
    st.markdown("#### Resumen Estadistico de Predicciones")
    
    if len(pred_filtradas) > 0:
        stats = pred_filtradas[["tasa_base", "prediccion_tasa_t3", "variacion", "total_creditos_base"]].describe()
        st.dataframe(stats, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
    
    # Histograma
    st.markdown("#### Distribucion de Tasas Predichas")
    
    if len(pred_filtradas) > 0:
        fig_hist = px.histogram(
            pred_filtradas,
            x="prediccion_tasa_t3",
            nbins=20,
            color_discrete_sequence=["#38bdf8"]
        )
        fig_hist.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            height=300,
            xaxis=dict(title="Tasa Predicha (%)", gridcolor="rgba(148, 163, 184, 0.1)"),
            yaxis=dict(title="Frecuencia", gridcolor="rgba(148, 163, 184, 0.1)"),
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Box plot por banco
    st.markdown("#### Box Plot de Tasas por Banco")
    
    if len(pred_filtradas) > 0:
        fig_box = px.box(
            pred_filtradas,
            x="banco",
            y="prediccion_tasa_t3",
            color="banco",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_box.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            height=400,
            showlegend=False,
            xaxis=dict(tickangle=-45, gridcolor="rgba(148, 163, 184, 0.1)"),
            yaxis=dict(title="Tasa Predicha (%)", gridcolor="rgba(148, 163, 184, 0.1)"),
            margin=dict(l=0, r=0, t=10, b=100)
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Scatter Tasa Base vs Predicha
    st.markdown("#### Tasa Base vs Tasa Predicha")
    
    if len(pred_filtradas) > 0:
        fig_scatter = px.scatter(
            pred_filtradas,
            x="tasa_base",
            y="prediccion_tasa_t3",
            color="banco",
            hover_data=["rango_monto"],
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        # Linea diagonal de referencia
        min_val = min(pred_filtradas["tasa_base"].min(), pred_filtradas["prediccion_tasa_t3"].min())
        max_val = max(pred_filtradas["tasa_base"].max(), pred_filtradas["prediccion_tasa_t3"].max())
        fig_scatter.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode="lines",
            name="Sin Cambio",
            line=dict(color="#64748b", dash="dash")
        ))
        fig_scatter.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            height=500,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
            xaxis=dict(title="Tasa Base (%)", gridcolor="rgba(148, 163, 184, 0.1)"),
            yaxis=dict(title="Tasa Predicha (%)", gridcolor="rgba(148, 163, 184, 0.1)"),
            margin=dict(l=0, r=150, t=10, b=0)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Criterio de seleccion
    st.markdown("#### Criterio de Seleccion de Modelos")
    
    for _, row in criterio_df.iterrows():
        with st.expander(f"Nivel: {row['nivel'].upper()}"):
            st.markdown(f"""
            - **Baseline de referencia:** {row['baseline_referencia']}
            - **R2 baseline:** {row['r2_baseline']:.4f}
            - **MAE baseline:** {row['mae_baseline']:.4f}
            - **Modelo recomendado:** {row['modelo_recomendado']}
            - **R2 recomendado:** {row['r2_recomendado']:.4f}
            - **MAE recomendado:** {row['mae_recomendado']:.4f}
            - **Criterio:** {row['criterio']}
            """)


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.8rem;">
    Dashboard de Prediccion de Tasas de Credito de Consumo | Datos: Superfinanciera de Colombia | 
    Periodo: Oct 2023 - Feb 2026 | Prediccion: Mayo 2026 (T+3)
</div>
""", unsafe_allow_html=True)
