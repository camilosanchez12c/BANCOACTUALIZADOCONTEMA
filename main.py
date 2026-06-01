"""
Dashboard de Prediccion de Tasas de Credito de Consumo
Entidades Bancarias Colombianas (2023-2026)
Con interactividad tipo Power BI y crossfiltering
"""
import streamlit as st
import pandas as pd
import numpy as np
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
    page_title="Prediccion Tasas de Credito - Colombia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# INICIALIZAR SESSION STATE
# =============================================================================
if "selected_banco" not in st.session_state:
    st.session_state.selected_banco = "Todos"
if "selected_rango" not in st.session_state:
    st.session_state.selected_rango = "Todos"

# =============================================================================
# ESTILOS CSS - TEMA CLARO PROFESIONAL
# =============================================================================
st.markdown("""
<style>
    .stApp { background-color: #F8FAFC !important; }
    .main .block-container { background-color: #F8FAFC !important; }
    
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px; padding: 1.25rem; margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06); text-align: center;
    }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #1E40AF; margin: 0; }
    .kpi-value-green { font-size: 2rem; font-weight: 700; color: #059669; margin: 0; }
    .kpi-value-red { font-size: 2rem; font-weight: 700; color: #DC2626; margin: 0; }
    .kpi-label { font-size: 0.75rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.5rem; }
    
    .main-title { font-size: 2.25rem; font-weight: 700; color: #1E293B; margin-bottom: 0.25rem; }
    .subtitle { color: #64748B; font-size: 0.95rem; margin-bottom: 1.5rem; }
    .badge-green { background: #DCFCE7; color: #166534; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 500; display: inline-block; margin-left: 1rem; }
    
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #1E40AF 0%, #1E3A8A 100%) !important; border-right: 1px solid #3B82F6; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stMarkdown { color: #FFFFFF !important; }
    section[data-testid="stSidebar"] .stSelectbox > div > div { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 8px !important; }
    section[data-testid="stSidebar"] .stSelectbox > div > div > div, section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] span { color: #1E293B !important; }
    section[data-testid="stSidebar"] .stSelectbox svg { fill: #1E293B !important; }
    section[data-testid="stSidebar"] button { background-color: #FFFFFF !important; color: #1E40AF !important; border: 2px solid #1E40AF !important; font-weight: 600 !important; padding: 0.5rem 1rem !important; border-radius: 8px !important; }
    section[data-testid="stSidebar"] button p, section[data-testid="stSidebar"] button span, section[data-testid="stSidebar"] button div { color: #1E40AF !important; }
    section[data-testid="stSidebar"] button:hover { background-color: #EFF6FF !important; }
    section[data-testid="stSidebar"] .stButton > button { background-color: #FFFFFF !important; color: #1E40AF !important; width: 100% !important; }
    section[data-testid="stSidebar"] .stButton > button > div { color: #1E40AF !important; }
    section[data-testid="stSidebar"] .info-box { background: rgba(255, 255, 255, 0.15) !important; border: 1px solid rgba(255, 255, 255, 0.3) !important; color: #FFFFFF !important; }
    
    [data-baseweb="popover"] { background-color: #FFFFFF !important; }
    [data-baseweb="popover"] li { color: #1E293B !important; }
    [data-baseweb="popover"] li:hover { background-color: #EFF6FF !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: #F1F5F9; border-radius: 12px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 8px; color: #64748B; padding: 12px 24px; }
    .stTabs [aria-selected="true"] { background: #FFFFFF; color: #1E40AF; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
    
    .section-header { color: #1E293B; font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 2px solid #3B82F6; }
    
    .ranking-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem; text-align: center; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04); }
    .ranking-card:hover { border-color: #3B82F6; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15); transform: translateY(-2px); }
    .ranking-position { font-size: 0.7rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.1em; }
    .ranking-banco { font-size: 0.9rem; font-weight: 600; color: #1E293B; margin: 0.5rem 0; }
    .ranking-tasa { font-size: 1.25rem; font-weight: 700; color: #1E40AF; }
    
    .info-box { background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 1rem; color: #1E40AF; font-size: 0.85rem; }
    .criterio-card { background: #FFFFFF; border: 1px solid #BBF7D0; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04); }
    .criterio-nivel { font-size: 0.75rem; color: #166534; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; }
    .criterio-modelo { font-size: 1rem; font-weight: 600; color: #1E293B; margin-bottom: 0.25rem; }
    .criterio-metricas { font-size: 0.85rem; color: #64748B; }
    .filtro-activo { background: #DBEAFE; color: #1E40AF; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin: 0.25rem 0; display: inline-block; }
    
    /* TARJETA DE GRAFICO ELEGANTE */
    .chart-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        transition: all 0.3s ease;
    }
    .chart-container:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
    }
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #F1F5F9;
    }
    .chart-title-section {
        flex: 1;
    }
    .chart-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1E293B;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .chart-subtitle {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 4px;
    }
    
    /* BARRA DE ICONOS PARA GRAFICOS */
    .chart-toolbar {
        display: flex;
        gap: 4px;
        align-items: center;
    }
    .icon-btn {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        background: #F8FAFC;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
        color: #64748B;
    }
    .icon-btn:hover {
        background: #EFF6FF;
        border-color: #3B82F6;
        color: #2563EB;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.15);
    }
    .icon-btn.active {
        background: #2563EB;
        border-color: #2563EB;
        color: white;
    }
    .icon-btn svg {
        width: 18px;
        height: 18px;
    }
    .icon-btn-tooltip {
        position: relative;
    }
    .icon-btn-tooltip::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: -28px;
        left: 50%;
        transform: translateX(-50%);
        background: #1E293B;
        color: white;
        font-size: 0.7rem;
        padding: 4px 8px;
        border-radius: 4px;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s;
    }
    .icon-btn-tooltip:hover::after {
        opacity: 1;
    }
    
    /* PANEL DE INFO DEL GRAFICO */
    .chart-info-panel {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 1px solid #BBF7D0;
        border-left: 4px solid #22C55E;
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 12px;
        animation: slideDown 0.3s ease;
    }
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chart-info-panel.info-blue {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-color: #93C5FD;
        border-left-color: #3B82F6;
    }
    .chart-info-panel.info-amber {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-color: #FCD34D;
        border-left-color: #F59E0B;
    }
    .chart-info-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #166534;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .chart-info-panel.info-blue .chart-info-title { color: #1E40AF; }
    .chart-info-panel.info-amber .chart-info-title { color: #92400E; }
    .chart-info-text {
        font-size: 0.85rem;
        color: #374151;
        line-height: 1.7;
    }
    .chart-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 12px;
        padding: 12px;
        background: #F8FAFC;
        border-radius: 8px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        color: #64748B;
    }
    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 3px;
    }
    
    /* Estilos para expanders de informacion */
    div[data-testid="stExpander"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    div[data-testid="stExpander"] summary {
        font-size: 0.85rem;
        color: #64748B;
        padding: 10px 16px;
        font-weight: 500;
    }
    div[data-testid="stExpander"] summary:hover {
        color: #2563EB;
        background: #F8FAFC;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        padding: 12px 16px;
        background: #F8FAFC;
        border-top: 1px solid #E2E8F0;
        color: #475569;
        font-size: 0.88rem;
        line-height: 1.7;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] strong,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] b {
        color: #1E40AF;
    }
    
    /* Contenedor de graficos con sombra elegante */
    .stPlotlyChart {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        border: 1px solid #F1F5F9;
    }
    
    /* NUEVOS ESTILOS INTERACTIVOS */
    .help-btn {
        background: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        color: #1E40AF;
        cursor: pointer;
        margin-left: 8px;
        transition: all 0.2s;
    }
    .help-btn:hover {
        background: #DBEAFE;
        transform: scale(1.1);
    }
    
    .tooltip-box {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border: 1px solid #E2E8F0;
        border-left: 4px solid #3B82F6;
        border-radius: 8px;
        padding: 16px 20px;
        color: #334155;
        font-size: 0.9rem;
        line-height: 1.8;
        margin: 12px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .tooltip-box p {
        margin: 8px 0;
        color: #475569;
    }
    .tooltip-box strong {
        color: #1E40AF;
        font-weight: 600;
    }
    
    .interactive-card {
        background: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .interactive-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
        transform: translateY(-4px);
    }
    
    .result-highlight {
        background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%);
        border: 2px solid #22C55E;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin: 16px 0;
    }
    .result-highlight .big-number {
        font-size: 3rem;
        font-weight: 800;
        color: #166534;
        line-height: 1;
    }
    .result-highlight .label {
        font-size: 1rem;
        color: #15803D;
        margin-top: 8px;
    }
    
    .comparison-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 4px;
    }
    .badge-mejor { background: #DCFCE7; color: #166534; }
    .badge-peor { background: #FEE2E2; color: #991B1B; }
    .badge-neutral { background: #F1F5F9; color: #475569; }
    
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 8px 0;
    }
    .step-number {
        background: #1E40AF;
        color: #FFFFFF;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .step-text {
        color: #475569;
        font-size: 0.9rem;
    }
    
    .download-btn {
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s;
    }
    .download-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.4);
    }
    
    .metric-explanation {
        background: #FFFBEB;
        border-left: 4px solid #F59E0B;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.85rem;
        color: #92400E;
    }
    
    .banco-compare-card {
        background: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        min-height: 180px;
    }
    .banco-compare-card.selected {
        border-color: #3B82F6;
        background: #EFF6FF;
    }
    .banco-name { font-weight: 700; color: #1E293B; font-size: 1.1rem; margin-bottom: 8px; }
    .banco-tasa { font-size: 2rem; font-weight: 800; color: #1E40AF; }
    .banco-diff { font-size: 0.85rem; margin-top: 8px; }
    .banco-diff.positive { color: #DC2626; }
    .banco-diff.negative { color: #059669; }
    
    h1, h2, h3, h4, h5, h6, p, span, div { color: #1E293B; }
    .stSelectbox > div > div { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# CARGA DE DATOS
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
# EXCLUIR BANCO SANTANDER (datos con error)
# =============================================================================
BANCO_EXCLUIDO = "Banco Santander"

# Filtrar de todos los dataframes
if "banco" in predicciones_df.columns:
    predicciones_df = predicciones_df[predicciones_df["banco"] != BANCO_EXCLUIDO]
if "banco" in metricas_df.columns:
    metricas_df = metricas_df[metricas_df["banco"] != BANCO_EXCLUIDO]
if "banco" in historico_df.columns:
    historico_df = historico_df[historico_df["banco"] != BANCO_EXCLUIDO]
if "banco" in ranking_df.columns:
    ranking_df = ranking_df[ranking_df["banco"] != BANCO_EXCLUIDO]

# Quitar de la lista de bancos
BANCOS = [b for b in BANCOS if b != BANCO_EXCLUIDO]


# =============================================================================
# ICONOS SVG PARA LA BARRA DE HERRAMIENTAS
# =============================================================================
ICON_INFO = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>'''

ICON_EXPAND = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6"/><path d="M9 21H3v-6"/><path d="M21 3l-7 7"/><path d="M3 21l7-7"/></svg>'''

ICON_DOWNLOAD = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>'''

ICON_CHART = "📊"


def render_chart_header_with_sort(title, subtitle=None, chart_key="", show_sort=True, sort_options=None):
    """
    Renderiza un header de grafico con titulo, subtitulo y opcion de ordenamiento.
    Retorna el valor del ordenamiento seleccionado.
    """
    if sort_options is None:
        sort_options = ["Mayor a menor", "Menor a mayor"]
    
    col_title, col_sort = st.columns([3, 1])
    
    with col_title:
        st.markdown(f'''
        <div style="margin-bottom: 4px;">
            <h4 style="margin:0; padding:0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">
                {ICON_CHART} {title}
            </h4>
            {f'<p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #64748B;">{subtitle}</p>' if subtitle else ''}
        </div>
        ''', unsafe_allow_html=True)
    
    sort_value = sort_options[0]
    if show_sort:
        with col_sort:
            sort_value = st.selectbox(
                "Ordenar",
                sort_options,
                key=f"sort_{chart_key}",
                label_visibility="collapsed"
            )
    
    return sort_value


def render_chart_header(title, subtitle=None, chart_key=""):
    """
    Renderiza un header de grafico elegante con titulo y subtitulo (sin ordenamiento).
    """
    st.markdown(f'''
    <div style="margin-bottom: 8px;">
        <h4 style="margin:0; padding:0; font-size: 1.1rem; font-weight: 600; color: #1E293B;">
            {ICON_CHART} {title}
        </h4>
        {f'<p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #64748B;">{subtitle}</p>' if subtitle else ''}
    </div>
    ''', unsafe_allow_html=True)


def render_chart_info(content, info_type="green", chart_key=""):
    """Renderiza el panel de informacion del grafico usando un expander."""
    icon = "💡"
    titulo = "Como interpretar este grafico"
    
    if info_type == "blue":
        icon = "📈"
        titulo = "Que muestra este grafico"
    elif info_type == "amber":
        icon = "⚡"
        titulo = "Tip importante"
    
    # Convertir tags HTML a markdown
    content_md = content.replace("<strong>", "**").replace("</strong>", "**")
    content_md = content_md.replace("<br>", "  \n").replace("<br/>", "  \n")
    content_md = content_md.replace("<em>", "*").replace("</em>", "*")
    content_md = content_md.replace("&lt;", "<").replace("&gt;", ">")
    
    with st.expander(f"{icon} {titulo}", expanded=False):
        st.markdown(content_md)


# =============================================================================
# INICIALIZAR SESSION STATE
# =============================================================================
if "selected_banco" not in st.session_state:
    st.session_state.selected_banco = "Todos"
if "selected_rango" not in st.session_state:
    st.session_state.selected_rango = "Todos"


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
        st.session_state.selected_banco = "Todos"
        st.session_state.selected_rango = "Todos"
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

    st.markdown("---")

    # Filtros activos
    st.markdown("### Filtros Activos")
    filtros_activos = []
    if banco_sel != "Todos":
        filtros_activos.append(f"Banco: {banco_sel}")
    if rango_sel != "Todos":
        filtros_activos.append(f"Rango: {rango_sel[:30]}")

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
    <strong>Prediccion:</strong> Junio 2026 (T+3)
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

# Filtro historico solo por banco
hist_filtrado = historico_df.copy()
hist_total_filtrado = historico_total_df.copy()
if banco_sel != "Todos":
    hist_filtrado = hist_filtrado[hist_filtrado["banco"] == banco_sel]

# Filtro de metricas por banco y rango para Tab 3
metricas_filtradas = metricas_df.copy()
if banco_sel != "Todos" and "banco" in metricas_filtradas.columns:
    metricas_filtradas = metricas_filtradas[metricas_filtradas["banco"] == banco_sel]
if rango_sel != "Todos" and "rango_monto" in metricas_filtradas.columns:
    metricas_filtradas = metricas_filtradas[metricas_filtradas["rango_monto"] == rango_sel]

# Filtro de criterio por banco/rango (si aplica)
criterio_filtrado = criterio_df.copy()


# =============================================================================
# COLORES PARA GRAFICOS - TEMA CLARO FIJO
# =============================================================================
PLOT_BG = "#FFFFFF"
PAPER_BG = "#FFFFFF"
FONT_COLOR = "#000000"  # Negro para mejor visibilidad
GRID_COLOR = "#E2E8F0"
BAR_COLOR_1 = "#2563EB"  # Azul vibrante
BAR_COLOR_2 = "#64748B"  # Gris
COLOR_SCALE = ["#3B82F6", "#2563EB", "#1E40AF"]  # Escala de azules
PIE_COLORS = ["#1E40AF", "#2563EB", "#3B82F6", "#60A5FA", "#10B981", "#F59E0B"]


# =============================================================================
# HEADER PRINCIPAL
# =============================================================================
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.markdown('<h1 class="main-title">Predicción de Tasas de Interes para Creditos de Consumo en Colombia</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análisis y predicción mensual de tasas efectivas promedio en entidades bancarias colombianas, utilizando información histórica del período 2023–2026 <span class="badge-green">● Datos: Superfinanciera de Colombia</span></p>', unsafe_allow_html=True)


# =============================================================================
# KPIs PRINCIPALES
# =============================================================================
st.markdown("""
<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
    <span style="font-size: 1.1rem; font-weight: 600; color: #1E293B;">Metricas Principales</span>
</div>
""", unsafe_allow_html=True)

# Tooltip de ayuda para KPIs
with st.expander("Que significan estas metricas? - Haz clic para ver explicacion", expanded=False):
    st.markdown("""
    <div class="tooltip-box">
        <p><strong>Predicciones:</strong> Numero total de combinaciones banco-rango analizadas</p>
        <p><strong>Tasa Promedio:</strong> La tasa de interes promedio predicha para Junio 2026</p>
        <p><strong>Tasa Minima:</strong> La tasa mas baja disponible (en verde = buena opcion)</p>
        <p><strong>Tasa Maxima:</strong> La tasa mas alta predicha (en rojo = opcion costosa)</p>
        <p><strong>Total Creditos:</strong> Cantidad de creditos historicos usados como base</p>
    </div>
    """, unsafe_allow_html=True)

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
    st.markdown('<div class="section-header">Ranking de Bancos por Tasa Predicha (Junio 2026)</div>', unsafe_allow_html=True)
    
    # Guia interactiva - formato claro y legible
    with st.expander("Como usar esta seccion - Haz clic para ver instrucciones", expanded=False):
        st.markdown("""
        <div style="background: #FFFFFF; border: 2px solid #2563EB; border-radius: 12px; padding: 20px;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <span style="background: #2563EB; color: white; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700;">1</span>
                <span style="color: #1E293B;">Selecciona un <strong style="color: #2563EB;">rango de monto</strong> en el sidebar izquierdo</span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <span style="background: #2563EB; color: white; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700;">2</span>
                <span style="color: #1E293B;">Observa el <strong style="color: #2563EB;">ranking de bancos</strong> ordenados de menor a mayor tasa</span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <span style="background: #2563EB; color: white; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700;">3</span>
                <span style="color: #1E293B;">El banco en <strong style="color: #2563EB;">posicion #1</strong> te ofrece la tasa mas baja</span>
            </div>
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="background: #2563EB; color: white; width: 28px; height: 28px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: 700;">4</span>
                <span style="color: #1E293B;">Usa el <strong style="color: #2563EB;">comparador</strong> para ver diferencias entre bancos</span>
            </div>
        </div>
        <div style="background: #DCFCE7; border: 1px solid #22C55E; border-radius: 8px; padding: 12px; margin-top: 12px; color: #166534;">
            <strong>Tip:</strong> El resultado destacado en verde te muestra automaticamente la mejor opcion y cuanto puedes ahorrar.
        </div>
        """, unsafe_allow_html=True)
    
    # Titulo de seccion con ordenamiento global
    st.markdown("<br>", unsafe_allow_html=True)
    col_ord1, col_ord2 = st.columns([2, 1])
    with col_ord1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.2rem; font-weight: 700; color: #1E293B;">Ranking de Bancos</span>
            <span style="background: #EFF6FF; color: #2563EB; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">Interactivo</span>
        </div>
        """, unsafe_allow_html=True)
    with col_ord2:
        orden = st.selectbox("Orden global", ["Menor tasa primero", "Mayor tasa primero"], key="orden_rank", label_visibility="collapsed")
    
    ascending = orden == "Menor tasa primero"
    
    # Calcular ranking
    rank_calc = pred_filtradas.groupby("banco").agg({
        "prediccion_tasa_t3": "mean",
        "total_creditos_base": "sum",
        "tasa_base": "mean"
    }).reset_index()
    rank_calc = rank_calc.sort_values("prediccion_tasa_t3", ascending=ascending).reset_index(drop=True)
    rank_calc["posicion"] = range(1, len(rank_calc) + 1)
    
    # Calcular diferencia con el promedio
    tasa_promedio_general = rank_calc["prediccion_tasa_t3"].mean()
    rank_calc["diferencia_promedio"] = rank_calc["prediccion_tasa_t3"] - tasa_promedio_general
    
    # Resultado destacado
    if len(rank_calc) > 0:
        mejor_banco = rank_calc.iloc[0]
        peor_banco = rank_calc.iloc[-1]
        ahorro_potencial = peor_banco["prediccion_tasa_t3"] - mejor_banco["prediccion_tasa_t3"]
        
        st.markdown(f"""
        <div class="result-highlight">
            <div class="big-number">{mejor_banco['banco']}</div>
            <div class="label">Ofrece la tasa mas baja: <strong>{mejor_banco['prediccion_tasa_t3']:.2f}%</strong></div>
            <div style="margin-top: 12px; font-size: 0.9rem; color: #166534;">
                Eligiendo este banco en vez de {peor_banco['banco']} podrias ahorrar hasta <strong>{ahorro_potencial:.2f} puntos porcentuales</strong> en tu tasa de interes
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Top 4 cards mejorados
    if len(rank_calc) >= 4:
        cols = st.columns(4)
        medals = ["#1", "#2", "#3", "#4"]
        medal_colors = ["#FFD700", "#C0C0C0", "#CD7F32", "#64748B"]
        for i, (_, row) in enumerate(rank_calc.head(4).iterrows()):
            with cols[i]:
                diff_text = ""
                if row["diferencia_promedio"] < 0:
                    diff_text = f'<div class="banco-diff negative">{row["diferencia_promedio"]:.2f}% vs promedio</div>'
                else:
                    diff_text = f'<div class="banco-diff positive">+{row["diferencia_promedio"]:.2f}% vs promedio</div>'
                
                st.markdown(f"""
                <div class="interactive-card">
                    <div style="background: {medal_colors[i]}; color: white; border-radius: 50%; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-weight: 700; margin: 0 auto 8px auto;">{medals[i]}</div>
                    <div class="banco-name">{row['banco']}</div>
                    <div class="banco-tasa">{row['prediccion_tasa_t3']:.2f}%</div>
                    {diff_text}
                    <div style="font-size: 0.75rem; color: #64748B; margin-top: 8px;">{row['total_creditos_base']:,.0f} creditos</div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Comparador de bancos
    st.markdown("#### Comparador de Bancos")
    st.markdown("""
    <div class="metric-explanation">
        Selecciona dos bancos para comparar sus tasas predichas y ver la diferencia.
    </div>
    """, unsafe_allow_html=True)
    
    col_comp1, col_comp2 = st.columns(2)
    bancos_disponibles = rank_calc["banco"].tolist()
    
    with col_comp1:
        banco_a = st.selectbox("Banco A", bancos_disponibles, index=0, key="comp_banco_a")
    with col_comp2:
        banco_b = st.selectbox("Banco B", bancos_disponibles, index=min(1, len(bancos_disponibles)-1), key="comp_banco_b")
    
    if banco_a and banco_b:
        data_a = rank_calc[rank_calc["banco"] == banco_a].iloc[0]
        data_b = rank_calc[rank_calc["banco"] == banco_b].iloc[0]
        diferencia = data_a["prediccion_tasa_t3"] - data_b["prediccion_tasa_t3"]
        
        col_res1, col_res2, col_res3 = st.columns([2, 1, 2])
        
        with col_res1:
            badge_a = "badge-mejor" if diferencia < 0 else "badge-peor" if diferencia > 0 else "badge-neutral"
            st.markdown(f"""
            <div class="banco-compare-card {'selected' if diferencia < 0 else ''}">
                <div class="banco-name">{banco_a}</div>
                <div class="banco-tasa">{data_a['prediccion_tasa_t3']:.2f}%</div>
                <span class="comparison-badge {badge_a}">{'Mejor opcion' if diferencia < 0 else 'Mayor tasa' if diferencia > 0 else 'Igual'}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col_res2:
            st.markdown(f"""
            <div style="text-align: center; padding: 20px;">
                <div style="font-size: 2rem; font-weight: 800; color: {'#059669' if diferencia < 0 else '#DC2626' if diferencia > 0 else '#64748B'};">
                    {'+' if diferencia > 0 else ''}{diferencia:.2f}%
                </div>
                <div style="font-size: 0.8rem; color: #64748B;">Diferencia</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_res3:
            badge_b = "badge-mejor" if diferencia > 0 else "badge-peor" if diferencia < 0 else "badge-neutral"
            st.markdown(f"""
            <div class="banco-compare-card {'selected' if diferencia > 0 else ''}">
                <div class="banco-name">{banco_b}</div>
                <div class="banco-tasa">{data_b['prediccion_tasa_t3']:.2f}%</div>
                <span class="comparison-badge {badge_b}">{'Mejor opcion' if diferencia > 0 else 'Mayor tasa' if diferencia < 0 else 'Igual'}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grafico de barras horizontales
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Header con ordenamiento
        sort_tasa = render_chart_header_with_sort(
            "Tasa Predicha por Banco", 
            "Junio 2026 - Colores por nivel de tasa",
            "tasa_banco",
            sort_options=["Menor a mayor", "Mayor a menor"]
        )
        
        render_chart_info('''
            <strong>Verde</strong> = Tasa baja (&lt;19%) - Excelente opcion<br>
            <strong>Amarillo</strong> = Tasa media (19-22%) - Aceptable<br>
            <strong>Naranja</strong> = Tasa alta (22-24%) - Considerar otras<br>
            <strong>Rojo</strong> = Tasa muy alta (&gt;24%) - Evitar<br><br>
            <em>Tip: Busca bancos con barras verdes para la mejor tasa.</em>
        ''', "green", "tasa_banco")
        
        # Ordenar datos segun seleccion
        rank_sorted = rank_calc.sort_values("prediccion_tasa_t3", ascending=(sort_tasa == "Menor a mayor"))
        
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
        
        rank_sorted["color"] = rank_sorted["prediccion_tasa_t3"].apply(get_color)
        
        fig_rank = go.Figure()
        fig_rank.add_trace(go.Bar(
            x=rank_sorted["prediccion_tasa_t3"],
            y=rank_sorted["banco"],
            orientation="h",
            marker_color=rank_sorted["color"],
            text=rank_sorted["prediccion_tasa_t3"].apply(lambda x: f"{x:.2f}%"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Tasa: %{x:.2f}%<extra></extra>"
        ))
        fig_rank.update_layout(
            plot_bgcolor=PLOT_BG,
            paper_bgcolor=PAPER_BG,
            font_color=FONT_COLOR,
            height=500,
            margin=dict(l=0, r=50, t=10, b=0),
            xaxis=dict(title=dict(text="Tasa Predicha (%)", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
            yaxis=dict(tickfont=dict(color="#000000"), categoryorder="array", categoryarray=rank_sorted["banco"].tolist()),
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
        # Header con ordenamiento
        sort_vol = render_chart_header_with_sort(
            "Volumen de Creditos", 
            "Total historico por banco",
            "vol_banco",
            sort_options=["Mayor a menor", "Menor a mayor"]
        )
        
        render_chart_info('''
            Muestra la <strong>cantidad total de creditos</strong> que cada banco ha otorgado.<br><br>
            Bancos con mayor volumen tienen mas experiencia en el mercado de creditos de consumo.
        ''', "blue", "vol_banco")
        
        # Ordenar segun seleccion
        vol_sorted = rank_calc.sort_values("total_creditos_base", ascending=(sort_vol == "Menor a mayor"))
        
        fig_vol = px.bar(
            vol_sorted,
            x="total_creditos_base",
            y="banco",
            orientation="h",
            color="total_creditos_base",
            color_continuous_scale=COLOR_SCALE,
        )
        fig_vol.update_layout(
            plot_bgcolor=PLOT_BG,
            paper_bgcolor=PAPER_BG,
            font_color=FONT_COLOR,
            height=500,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(title=dict(text="Total Creditos", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
            yaxis=dict(tickfont=dict(color="#000000")),
        )
        st.plotly_chart(fig_vol, use_container_width=True, key="vol_chart_rank")
    
    # Comparacion Tasa Base vs Predicha
    sort_comp = render_chart_header_with_sort(
        "Tasa Base vs Predicha", 
        "Comparacion Marzo vs Junio 2026",
        "comp_tasa",
        sort_options=["Por tasa predicha (menor)", "Por tasa predicha (mayor)", "Por tasa base (menor)", "Por tasa base (mayor)"]
    )
    
    render_chart_info('''
        <strong>Barra gris:</strong> Tasa actual (Marzo 2026)<br>
        <strong>Barra azul:</strong> Tasa predicha (Junio 2026)<br><br>
        Si la barra azul es <strong>mas baja</strong> = La tasa bajara (bueno para ti)<br>
        Si la barra azul es <strong>mas alta</strong> = La tasa subira (malo para ti)
    ''', "blue", "comp_tasa")
    
    # Ordenar datos de comparacion
    if "predicha (menor)" in sort_comp:
        comp_sorted = rank_calc.sort_values("prediccion_tasa_t3", ascending=True)
    elif "predicha (mayor)" in sort_comp:
        comp_sorted = rank_calc.sort_values("prediccion_tasa_t3", ascending=False)
    elif "base (menor)" in sort_comp:
        comp_sorted = rank_calc.sort_values("tasa_base", ascending=True)
    else:
        comp_sorted = rank_calc.sort_values("tasa_base", ascending=False)
    
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name="Tasa Base (Mar 2026)", x=comp_sorted["banco"], y=comp_sorted["tasa_base"], marker_color=BAR_COLOR_2))
    fig_comp.add_trace(go.Bar(name="Tasa Predicha (Jun 2026)", x=comp_sorted["banco"], y=comp_sorted["prediccion_tasa_t3"], marker_color=BAR_COLOR_1))
    fig_comp.update_layout(
        barmode="group",
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font_color=FONT_COLOR,
        height=350,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
        xaxis=dict(tickangle=-45, gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
        yaxis=dict(title=dict(text="Tasa (%)", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
        margin=dict(l=0, r=0, t=30, b=100)
    )
    st.plotly_chart(fig_comp, use_container_width=True, key="comp_chart_rank")
    
    # Distribucion por Rango de Monto
    sort_rango = render_chart_header_with_sort(
        "Distribucion por Rango de Monto", 
        "Tasa promedio y volumen por rango",
        "dist_rango",
        sort_options=["Menor tasa primero", "Mayor tasa primero"]
    )
    
    render_chart_info('''
        <strong>Grafico de barras:</strong> Tasa promedio para cada rango de monto de credito.<br>
        <strong>Grafico de torta:</strong> Como se distribuyen los creditos entre los rangos.<br><br>
        <em>Tip: Haz clic en una barra para filtrar por ese rango.</em>
    ''', "amber", "dist_rango")
    
    rango_agg = pred_filtradas.groupby("rango_monto").agg({
        "prediccion_tasa_t3": "mean",
        "total_creditos_base": "sum"
    }).reset_index()
    
    # Ordenar segun seleccion
    rango_sorted = rango_agg.sort_values("prediccion_tasa_t3", ascending=(sort_rango == "Menor tasa primero"))
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        fig_rango = px.bar(
            rango_sorted,
            x="rango_monto",
            y="prediccion_tasa_t3",
            color="prediccion_tasa_t3",
            color_continuous_scale=["#22c55e", "#fbbf24", "#ef4444"],
            title="Tasa Promedio por Rango"
        )
        fig_rango.update_layout(
            plot_bgcolor=PLOT_BG,
            paper_bgcolor=PAPER_BG,
            font_color=FONT_COLOR,
            height=300,
            showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(tickangle=-45, tickfont=dict(color="#000000")),
            yaxis=dict(tickfont=dict(color="#000000")),
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
            color_discrete_sequence=PIE_COLORS
        )
        fig_pie.update_layout(
            plot_bgcolor=PLOT_BG,
            paper_bgcolor=PAPER_BG,
            font_color=FONT_COLOR,
            height=300,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart_rank")
    
    # Tabla de predicciones
    st.markdown("#### Tabla de Predicciones")
    
    st.markdown("""
    <div class="metric-explanation">
        Esta tabla muestra todas las predicciones. Puedes ordenar por cualquier columna haciendo clic en el encabezado o usando los selectores.
    </div>
    """, unsafe_allow_html=True)
    
    col_sort, col_order, col_download = st.columns([2, 1, 1])
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
    
    # Boton de descarga
    with col_download:
        st.markdown("<br>", unsafe_allow_html=True)
        csv_data = tabla.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar CSV",
            data=csv_data,
            file_name="predicciones_tasas_junio2026.csv",
            mime="text/csv",
            help="Descarga todas las predicciones en formato CSV"
        )
    
    # Resumen final del Tab
    st.markdown("---")
    st.markdown("#### Resumen de tu Busqueda")
    
    filtro_banco_txt = f"**{banco_sel}**" if banco_sel != "Todos" else "todos los bancos"
    filtro_rango_txt = f"**{rango_sel}**" if rango_sel != "Todos" else "todos los rangos"
    
    if len(rank_calc) > 0:
        mejor = rank_calc.iloc[0]
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border-radius: 12px; padding: 20px; margin: 16px 0;">
            <p style="font-size: 1rem; color: #1E40AF; margin: 0;">
                Buscaste en {filtro_banco_txt} para {filtro_rango_txt}.<br><br>
                La mejor opcion es <strong style="font-size: 1.2rem;">{mejor['banco']}</strong> con una tasa predicha de 
                <strong style="font-size: 1.3rem; color: #059669;">{mejor['prediccion_tasa_t3']:.2f}%</strong> para Junio 2026.
            </p>
        </div>
        """, unsafe_allow_html=True)

#este por ahora no se va a usar poqruqe al momento de subir los cambios 
#a git hub es demasiado pesado los 2 archivos que tienen la data cruda


# =============================================================================
# TAB 3: COMPARACION DE MODELOS
# =============================================================================
with tab3:
    st.markdown('<div class="section-header">Comparacion de Modelos de Machine Learning</div>', unsafe_allow_html=True)

    # ── FILTRO DE NIVEL — va PRIMERO, arriba de todo ──────────────────────
    nivel_opciones = {
        "banco_rango": "Banco × Rango (mas detallado)",
        "banco":       "Por Banco",
        "rango":       "Por Rango de Monto",
        "total":       "Total del sistema",
    }

    col_filtro_lbl, col_filtro_sel = st.columns([2, 2])
    with col_filtro_lbl:
        st.markdown("""
        <div style="padding-top: 6px;">
            <span style="font-size: 1rem; font-weight: 600; color: #1E293B;">
                📊 Metricas de evaluacion por nivel
            </span><br>
            <span style="font-size: 0.8rem; color: #64748B;">
                Selecciona el nivel jerarquico para filtrar R², MAE y graficas
            </span>
        </div>
        """, unsafe_allow_html=True)
    with col_filtro_sel:
        nivel_sel = st.selectbox(
            "Nivel de evaluacion",
            options=list(nivel_opciones.keys()),
            format_func=lambda x: nivel_opciones[x],
            index=0,
            key="nivel_agregacion_tab3",
            label_visibility="collapsed",
        )

    # Descripcion del nivel activo
    st.markdown(f"""
    <div style="background: #EFF6FF; border: 1px solid #93C5FD; border-radius: 8px;
                padding: 10px 16px; margin: 8px 0 16px 0; display:flex; align-items:center; gap:8px;">
        <span style="font-size: 1.1rem;">🔍</span>
        <span style="color: #1E40AF; font-size: 0.88rem;">
            <strong>Nivel activo:</strong> {nivel_opciones[nivel_sel]}
            &nbsp;|&nbsp; Las graficas, el KPI y la tabla de abajo muestran las metricas de este nivel.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Calcular metricas filtradas por nivel ─────────────────────────────
    metricas_nivel = metricas_df[metricas_df["nivel"] == nivel_sel].copy()

    if len(metricas_nivel) > 0:
        metricas_para_usar = metricas_nivel.groupby("modelo").agg(
            {"r2": "mean", "mae": "mean"}
        ).reset_index()
    else:
        # fallback: usar nivel total
        metricas_para_usar = metricas_df[metricas_df["nivel"] == "total"].groupby("modelo").agg(
            {"r2": "mean", "mae": "mean"}
        ).reset_index()

    # ── Guia interactiva (va después del filtro) ──────────────────────────
    with st.expander("Guia: Como interpretar estos resultados - Haz clic para aprender", expanded=False):
        st.markdown("""
        <div style="background: #FFFFFF; border: 2px solid #2563EB; border-radius: 12px; padding: 20px; margin-bottom: 12px;">
            <h4 style="color: #1E40AF; margin-top: 0;">Que son los modelos?</h4>
            <p style="color: #1E293B; margin-bottom: 0;">Probamos 10 algoritmos diferentes para predecir las tasas de interes. Algunos son "baselines" (reglas simples) y otros son modelos de Machine Learning mas sofisticados.</p>
        </div>
        
        <div style="background: #FFFFFF; border: 2px solid #22C55E; border-radius: 12px; padding: 20px; margin-bottom: 12px;">
            <h4 style="color: #166534; margin-top: 0;">Metricas explicadas:</h4>
            <p style="color: #1E293B;"><strong>R2 (Precision):</strong> Mide que tan bien el modelo captura los patrones. 1.0 = perfecto, 0 = no captura nada.</p>
            <p style="color: #1E293B; margin-bottom: 0;"><strong>MAE (Error):</strong> Error promedio en puntos porcentuales. Si MAE = 0.5, el modelo se equivoca en promedio 0.5%.</p>
        </div>
        
        <div style="background: #FFFFFF; border: 2px solid #F59E0B; border-radius: 12px; padding: 20px; margin-bottom: 12px;">
            <h4 style="color: #92400E; margin-top: 0;">Tipos de modelos:</h4>
            <p style="color: #1E293B;"><strong>Baselines:</strong> Reglas simples como "la tasa de manana sera igual a la de hoy"</p>
            <p style="color: #1E293B; margin-bottom: 0;"><strong>ML:</strong> Algoritmos que aprenden patrones complejos de los datos historicos</p>
        </div>
        
        <div style="background: #FEF3C7; border: 2px solid #F59E0B; border-radius: 12px; padding: 16px;">
            <p style="color: #92400E; margin: 0;"><strong>Hallazgo interesante:</strong> Los baselines funcionan muy bien porque las tasas de credito tienen alta inercia (cambian poco de mes a mes).</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Diccionario para nombres de modelos legibles
    MODEL_DISPLAY_NAMES = {
        "baseline_tasa_actual": "Baseline Tasa Actual",
        "baseline_naive_lag1": "Baseline Naive Lag1",
        "baseline_media_movil_3": "Baseline Media Movil 3",
        "baseline_media_movil_6": "Baseline Media Movil 6",
        "ridge": "Ridge",
        "elastic_net": "Elastic Net",
        "random_forest": "Random Forest",
        "extra_trees": "Extra Trees",
        "hist_gradient_boosting": "Hist Gradient Boosting",
        "xgboost": "XGBoost",
    }
    
    MODEL_DESCRIPTIONS = {
        "baseline_tasa_actual": "Usa la tasa actual como prediccion (la tasa no cambiara)",
        "baseline_naive_lag1": "Usa la tasa del mes anterior",
        "baseline_media_movil_3": "Promedio de los ultimos 3 meses",
        "baseline_media_movil_6": "Promedio de los ultimos 6 meses",
        "ridge": "Regresion lineal con regularizacion L2",
        "elastic_net": "Regresion lineal con regularizacion L1+L2",
        "random_forest": "Conjunto de arboles de decision aleatorios",
        "extra_trees": "Arboles extremadamente aleatorios",
        "hist_gradient_boosting": "Gradient boosting con histogramas",
        "xgboost": "Extreme Gradient Boosting (muy popular)",
    }
    
    def format_model_name(name):
        """Convierte nombres de modelos a formato legible"""
        return MODEL_DISPLAY_NAMES.get(name, name.replace("_", " ").title())
    
    # Resumen simple: Mejor modelo para los datos filtrados
    # Calculamos el mejor modelo basado en metricas filtradas
    if len(metricas_para_usar) > 0 and "r2" in metricas_para_usar.columns:
        mejor_idx = metricas_para_usar["r2"].idxmax()
        mejor_modelo_nombre = metricas_para_usar.loc[mejor_idx, "modelo"]
        mejor_r2 = metricas_para_usar.loc[mejor_idx, "r2"]
        mejor_mae = metricas_para_usar.loc[mejor_idx, "mae"]
    else:
        mejor_modelo_row = criterio_df.loc[criterio_df["r2_recomendado"].idxmax()]
        mejor_modelo_nombre = mejor_modelo_row["modelo_recomendado"]
        mejor_r2 = mejor_modelo_row["r2_recomendado"]
        mejor_mae = mejor_modelo_row["mae_recomendado"]

    modelo_nombre_display = format_model_name(mejor_modelo_nombre)

    # Etiqueta del nivel activo (para el titulo del KPI)
    nivel_label = {
        "total":       "General (todo el sistema)",
        "banco":       "por Banco",
        "rango":       "por Rango de Monto",
        "banco_rango": "por Banco × Rango",
    }
    titulo_mejor = f"Mejor Modelo — Nivel {nivel_label.get(nivel_sel, nivel_sel)}"
    st.markdown(f"#### {titulo_mejor}")
    
    col_best1, col_best2 = st.columns([2, 1])
    
    with col_best1:
        st.markdown(f"""
        <div class="result-highlight" style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border-color: #2563EB;">
            <div class="big-number" style="color: #1E40AF; font-size: 2rem;">{modelo_nombre_display}</div>
            <div style="display: flex; justify-content: center; gap: 30px; margin-top: 16px;">
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #059669;">{mejor_r2:.2%}</div>
                    <div style="font-size: 0.8rem; color: #64748B;">Precision (R2)</div>
                </div>
                <div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #DC2626;">{mejor_mae:.2f}</div>
                    <div style="font-size: 0.8rem; color: #64748B;">Error (MAE)</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_best2:
        st.markdown("""
        <div class="metric-explanation" style="height: 100%;">
            <strong>Por que este modelo?</strong><br><br>
            Este modelo tiene la mejor combinacion de precision alta y error bajo. 
            En la practica, predice las tasas con un error promedio muy pequeno.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grafico simple: Comparacion de R2 de modelos
    orden_r2 = render_chart_header_with_sort(
        "Precision de los Modelos (R2)", 
        "Coeficiente de determinacion - Mayor es mejor",
        "r2_modelos",
        sort_options=["Mayor a menor", "Menor a mayor"]
    )
    
    render_chart_info('''
        <strong>R2 = 1.0:</strong> Prediccion perfecta<br>
        <strong>R2 = 0.9:</strong> Explica el 90% de la variacion (muy bueno)<br>
        <strong>R2 = 0.5:</strong> Explica solo la mitad (regular)<br>
        <strong>R2 &lt; 0:</strong> Peor que usar el promedio<br><br>
        <strong>Gris</strong> = Baselines (reglas simples) | <strong>Azul</strong> = Machine Learning
    ''', "blue", "r2_modelos")
    
    # Usar metricas_para_usar directamente (ya esta calculado o viene del fallback)
    modelo_resumen = metricas_para_usar.copy()
    if "modelo_display" not in modelo_resumen.columns:
        modelo_resumen["modelo_display"] = modelo_resumen["modelo"].apply(format_model_name)
    modelo_resumen = modelo_resumen.sort_values("r2", ascending=(orden_r2 == "Menor a mayor"))
    
    # Colores por tipo de modelo (baseline vs ML)
    def get_model_color(modelo):
        if "baseline" in modelo.lower():
            return "#64748B"  # Gris para baselines
        else:
            return "#2563EB"  # Azul para ML
    
    modelo_resumen["color"] = modelo_resumen["modelo"].apply(get_model_color)
    
    fig_r2 = go.Figure()
    fig_r2.add_trace(go.Bar(
        x=modelo_resumen["modelo_display"],
        y=modelo_resumen["r2"],
        marker_color=modelo_resumen["color"],
        text=modelo_resumen["r2"].apply(lambda x: f"{x:.2%}"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Precision R2: %{y:.4f}<extra></extra>"
    ))
    fig_r2.update_layout(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font_color=FONT_COLOR,
        height=350,
        showlegend=False,
        xaxis=dict(title=dict(text="Modelo", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickangle=-45, tickfont=dict(color="#000000")),
        yaxis=dict(title=dict(text="Precision (R2)", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
        margin=dict(l=0, r=0, t=10, b=100)
    )
    st.plotly_chart(fig_r2, use_container_width=True, key="chart_r2_modelos")
    
    # Leyenda de colores
    st.markdown("""
    <div style="display: flex; gap: 20px; justify-content: center; margin-bottom: 20px;">
        <span style="display: flex; align-items: center; gap: 5px;">
            <span style="width: 12px; height: 12px; background: #64748B; border-radius: 2px;"></span>
            <span style="font-size: 0.8rem; color: #64748B;">Modelos Baseline</span>
        </span>
        <span style="display: flex; align-items: center; gap: 5px;">
            <span style="width: 12px; height: 12px; background: #2563EB; border-radius: 2px;"></span>
            <span style="font-size: 0.8rem; color: #64748B;">Modelos Machine Learning</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Grafico MAE por modelo (simplificado)
    orden_mae = render_chart_header_with_sort(
        "Error de los Modelos (MAE)", 
        "Mean Absolute Error - Menor es mejor",
        "mae_modelos",
        sort_options=["Menor a mayor", "Mayor a menor"]
    )
    
    render_chart_info('''
        <strong>MAE = 0.3:</strong> Se equivoca en promedio 0.3 puntos<br>
        <strong>MAE = 1.0:</strong> Error de 1 punto porcentual (mayor error)<br><br>
        <strong>Verde</strong> = Error bajo (&lt;0.5) | <strong>Amarillo</strong> = Error medio | <strong>Rojo</strong> = Error alto<br><br>
        <em>Menor MAE = Mejor modelo</em>
    ''', "amber", "mae_modelos")
    
    # Usar el mismo resumen de modelos
    modelo_resumen_mae = modelo_resumen.sort_values("mae", ascending=(orden_mae == "Menor a mayor"))
    
    # Colores por nivel de error (verde=bajo, amarillo=medio, rojo=alto)
    def get_mae_color(mae):
        if mae < 0.5:
            return "#059669"  # Verde - error bajo
        elif mae < 1.0:
            return "#F59E0B"  # Amarillo - error medio
        else:
            return "#DC2626"  # Rojo - error alto
    
    modelo_resumen_mae["mae_color"] = modelo_resumen_mae["mae"].apply(get_mae_color)
    
    fig_mae = go.Figure()
    fig_mae.add_trace(go.Bar(
        x=modelo_resumen_mae["modelo_display"],
        y=modelo_resumen_mae["mae"],
        marker_color=modelo_resumen_mae["mae_color"],
        text=modelo_resumen_mae["mae"].apply(lambda x: f"{x:.2f}"),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Error MAE: %{y:.4f} puntos<extra></extra>"
    ))
    fig_mae.update_layout(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font_color=FONT_COLOR,
        height=350,
        showlegend=False,
        xaxis=dict(title=dict(text="Modelo", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickangle=-45, tickfont=dict(color="#000000")),
        yaxis=dict(title=dict(text="Error (MAE)", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
        margin=dict(l=0, r=0, t=10, b=100)
    )
    st.plotly_chart(fig_mae, use_container_width=True, key="chart_mae_modelos")
    
    # Leyenda de colores MAE
    st.markdown("""
    <div style="display: flex; gap: 20px; justify-content: center; margin-bottom: 20px;">
        <span style="display: flex; align-items: center; gap: 5px;">
            <span style="width: 12px; height: 12px; background: #059669; border-radius: 2px;"></span>
            <span style="font-size: 0.8rem; color: #64748B;">Error bajo (&lt; 0.5)</span>
        </span>
        <span style="display: flex; align-items: center; gap: 5px;">
            <span style="width: 12px; height: 12px; background: #F59E0B; border-radius: 2px;"></span>
            <span style="font-size: 0.8rem; color: #64748B;">Error medio (0.5 - 1.0)</span>
        </span>
        <span style="display: flex; align-items: center; gap: 5px;">
            <span style="width: 12px; height: 12px; background: #DC2626; border-radius: 2px;"></span>
            <span style="font-size: 0.8rem; color: #64748B;">Error alto (&gt; 1.0)</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabla simplificada
    st.markdown("#### Resumen de Modelos")
    
    tabla_simple = modelo_resumen.copy()
    tabla_simple["Tipo"] = tabla_simple["modelo"].apply(lambda x: "Baseline" if "baseline" in x.lower() else "ML")
    tabla_simple["Modelo"] = tabla_simple["modelo"].apply(format_model_name)
    tabla_simple["Precision (R2)"] = tabla_simple["r2"].apply(lambda x: f"{x:.2%}")
    tabla_simple["Error (MAE)"] = tabla_simple["mae"].apply(lambda x: f"{x:.2f}")
    tabla_simple = tabla_simple[["Modelo", "Tipo", "Precision (R2)", "Error (MAE)"]]
    tabla_simple = tabla_simple.sort_values("Precision (R2)", ascending=False)
    
    st.dataframe(tabla_simple, use_container_width=True, height=350, hide_index=True)
    
    # Grafico comparativo interactivo - Scatter R2 vs MAE
    sort_scatter_models = render_chart_header_with_sort(
        "Comparativa: Precision vs Error", 
        "Cada punto representa un modelo",
        "scatter_models",
        sort_options=["Por precision (mayor)", "Por precision (menor)", "Por error (menor)", "Por error (mayor)"]
    )
    
    render_chart_info('''
        <strong>Eje X:</strong> Precision (R2) - Mayor es mejor<br>
        <strong>Eje Y:</strong> Error (MAE) - Menor es mejor<br><br>
        El modelo ideal esta en la <strong>esquina inferior derecha</strong> (alta precision, bajo error).<br>
        <strong>Cuadrados grises</strong> = Baselines | <strong>Circulos azules</strong> = Machine Learning
    ''', "blue", "scatter_models")
    
    # Ordenar modelo_resumen segun seleccion
    if "precision (mayor)" in sort_scatter_models:
        modelo_scatter = modelo_resumen.sort_values("r2", ascending=False)
    elif "precision (menor)" in sort_scatter_models:
        modelo_scatter = modelo_resumen.sort_values("r2", ascending=True)
    elif "error (menor)" in sort_scatter_models:
        modelo_scatter = modelo_resumen.sort_values("mae", ascending=True)
    else:
        modelo_scatter = modelo_resumen.sort_values("mae", ascending=False)
    
    fig_scatter_models = go.Figure()
    
    for _, row in modelo_scatter.iterrows():
        is_baseline = "baseline" in row["modelo"].lower()
        fig_scatter_models.add_trace(go.Scatter(
            x=[row["r2"]],
            y=[row["mae"]],
            mode="markers+text",
            name=row["modelo_display"],
            text=[row["modelo_display"]],
            textposition="top center",
            textfont=dict(size=9, color="#64748B"),
            marker=dict(
                size=18,
                color="#64748B" if is_baseline else "#2563EB",
                symbol="square" if is_baseline else "circle",
                line=dict(width=2, color="#FFFFFF")
            ),
            hovertemplate=f"<b>{row['modelo_display']}</b><br>R2: {row['r2']:.4f}<br>MAE: {row['mae']:.4f}<extra></extra>"
        ))
    
    # Zona ideal (esquina inferior derecha)
    fig_scatter_models.add_shape(
        type="rect",
        x0=0.8, y0=0, x1=1.0, y1=0.5,
        fillcolor="rgba(5, 150, 105, 0.1)",
        line=dict(color="rgba(5, 150, 105, 0.3)", dash="dot")
    )
    fig_scatter_models.add_annotation(
        x=0.9, y=0.25,
        text="Zona Ideal",
        showarrow=False,
        font=dict(size=10, color="#059669")
    )
    
    fig_scatter_models.update_layout(
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font_color=FONT_COLOR,
        height=400,
        showlegend=False,
        xaxis=dict(
            title=dict(text="Precision (R2) - Mayor es mejor", font=dict(color="#000000")),
            gridcolor=GRID_COLOR,
            tickfont=dict(color="#000000"),
            range=[min(modelo_resumen["r2"]) - 0.05, 1.0]
        ),
        yaxis=dict(
            title=dict(text="Error (MAE) - Menor es mejor", font=dict(color="#000000")),
            gridcolor=GRID_COLOR,
            tickfont=dict(color="#000000")
        ),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_scatter_models, use_container_width=True, key="scatter_models")
    
    # Leyenda
    st.markdown("""
    <div style="display: flex; gap: 20px; justify-content: center; margin-bottom: 20px;">
        <span style="display: flex; align-items: center; gap: 5px;">
            <span style="width: 12px; height: 12px; background: #64748B; border-radius: 2px;"></span>
            <span style="font-size: 0.8rem; color: #64748B;">Modelos Baseline</span>
        </span>
        <span style="display: flex; align-items: center; gap: 5px;">
            <span style="width: 12px; height: 12px; background: #2563EB; border-radius: 50%;"></span>
            <span style="font-size: 0.8rem; color: #64748B;">Modelos Machine Learning</span>
        </span>
        <span style="display: flex; align-items: center; gap: 5px;">
            <span style="width: 12px; height: 12px; background: rgba(5, 150, 105, 0.3); border-radius: 2px;"></span>
            <span style="font-size: 0.8rem; color: #64748B;">Zona Ideal</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Insight automatico
    mejor_ml = modelo_resumen[~modelo_resumen["modelo"].str.contains("baseline", case=False)].sort_values("r2", ascending=False).head(1)
    mejor_baseline = modelo_resumen[modelo_resumen["modelo"].str.contains("baseline", case=False)].sort_values("r2", ascending=False).head(1)
    
    if len(mejor_ml) > 0 and len(mejor_baseline) > 0:
        ml_r2 = mejor_ml.iloc[0]["r2"]
        bl_r2 = mejor_baseline.iloc[0]["r2"]
        ml_name = mejor_ml.iloc[0]["modelo_display"]
        bl_name = mejor_baseline.iloc[0]["modelo_display"]
        
        if bl_r2 > ml_r2:
            insight_text = f"Los modelos baseline superan a los modelos ML. <strong>{bl_name}</strong> (R2: {bl_r2:.2%}) es mejor que <strong>{ml_name}</strong> (R2: {ml_r2:.2%}). Esto sugiere que las tasas de interes tienen alta inercia y son dificiles de predecir con modelos complejos."
            insight_color = "#FEF3C7"
            insight_border = "#F59E0B"
        else:
            insight_text = f"Los modelos ML superan a los baselines. <strong>{ml_name}</strong> (R2: {ml_r2:.2%}) es mejor que <strong>{bl_name}</strong> (R2: {bl_r2:.2%})."
            insight_color = "#DCFCE7"
            insight_border = "#059669"
        
        st.markdown(f"""
        <div style="background: {insight_color}; border-left: 4px solid {insight_border}; border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 16px 0; font-size: 0.85rem; color: #1E293B;">
        <strong>Insight:</strong> {insight_text}
        </div>
        """, unsafe_allow_html=True)
    
    # Explorador de modelos individual
    st.markdown("---")
    st.markdown("#### Explorador de Modelos")
    st.markdown("""
    <div class="metric-explanation">
        Selecciona un modelo para ver su descripcion detallada y como funciona.
    </div>
    """, unsafe_allow_html=True)
    
    modelo_seleccionado = st.selectbox(
        "Selecciona un modelo para ver detalles",
        options=modelo_resumen["modelo"].tolist(),
        format_func=format_model_name,
        key="explorador_modelo"
    )
    
    if modelo_seleccionado:
        datos_modelo = modelo_resumen[modelo_resumen["modelo"] == modelo_seleccionado].iloc[0]
        descripcion = MODEL_DESCRIPTIONS.get(modelo_seleccionado, "Sin descripcion disponible")
        es_baseline = "baseline" in modelo_seleccionado.lower()
        
        col_det1, col_det2 = st.columns([2, 1])
        
        with col_det1:
            tipo_badge = '<span class="comparison-badge badge-neutral">Baseline</span>' if es_baseline else '<span class="comparison-badge" style="background: #DBEAFE; color: #1E40AF;">Machine Learning</span>'
            
            st.markdown(f"""
            <div class="interactive-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin: 0; color: #1E293B;">{format_model_name(modelo_seleccionado)}</h3>
                        {tipo_badge}
                    </div>
                </div>
                <p style="margin-top: 16px; color: #64748B; font-size: 0.95rem;">{descripcion}</p>
                <div style="display: flex; gap: 40px; margin-top: 20px;">
                    <div>
                        <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Precision (R2)</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #059669;">{datos_modelo['r2']:.2%}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #64748B; text-transform: uppercase;">Error (MAE)</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: #DC2626;">{datos_modelo['mae']:.2f}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_det2:
            # Indicador visual de calidad
            r2_percent = datos_modelo['r2'] * 100
            if r2_percent >= 85:
                calidad = "Excelente"
                calidad_color = "#059669"
                calidad_bg = "#DCFCE7"
            elif r2_percent >= 70:
                calidad = "Bueno"
                calidad_color = "#2563EB"
                calidad_bg = "#DBEAFE"
            elif r2_percent >= 50:
                calidad = "Regular"
                calidad_color = "#F59E0B"
                calidad_bg = "#FEF3C7"
            else:
                calidad = "Bajo"
                calidad_color = "#DC2626"
                calidad_bg = "#FEE2E2"
            
            st.markdown(f"""
            <div style="background: {calidad_bg}; border-radius: 12px; padding: 20px; text-align: center; height: 100%;">
                <div style="font-size: 0.8rem; color: #64748B; text-transform: uppercase; margin-bottom: 8px;">Calidad del Modelo</div>
                <div style="font-size: 2rem; font-weight: 800; color: {calidad_color};">{calidad}</div>
                <div style="margin-top: 16px;">
                    <div style="background: #E2E8F0; border-radius: 8px; height: 12px; overflow: hidden;">
                        <div style="background: {calidad_color}; height: 100%; width: {min(r2_percent, 100)}%;"></div>
                    </div>
                    <div style="font-size: 0.75rem; color: #64748B; margin-top: 4px;">{r2_percent:.1f}% precision</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# TAB 4: DATOS Y ESTADISTICAS
# =============================================================================
with tab4:
    st.markdown('<div class="section-header">Datos y Estadisticas</div>', unsafe_allow_html=True)
    
    # Guia interactiva - formato claro y legible
    with st.expander("Que encontraras en esta seccion - Haz clic para ver", expanded=False):
        st.markdown("""
        <div style="background: #FFFFFF; border: 2px solid #2563EB; border-radius: 12px; padding: 20px;">
            <p style="color: #1E293B; margin-bottom: 12px;"><strong style="color: #1E40AF;">Resumen Estadistico:</strong> Estadisticas descriptivas (media, mediana, desviacion estandar, etc.)</p>
            <p style="color: #1E293B; margin-bottom: 12px;"><strong style="color: #1E40AF;">Distribucion de Tasas:</strong> Histograma que muestra como se distribuyen las tasas predichas.</p>
            <p style="color: #1E293B; margin-bottom: 12px;"><strong style="color: #1E40AF;">Box Plot:</strong> Visualizacion de la variabilidad de tasas por banco, mostrando valores atipicos.</p>
            <p style="color: #1E293B; margin-bottom: 0;"><strong style="color: #1E40AF;">Scatter Plot:</strong> Relacion entre la tasa base actual y la tasa predicha.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Mostrar filtros activos con mejor formato
    if banco_sel != "Todos" or rango_sel != "Todos":
        filtros_html = ""
        if banco_sel != "Todos":
            filtros_html += f'<span class="comparison-badge badge-neutral">Banco: {banco_sel}</span>'
        if rango_sel != "Todos":
            filtros_html += f'<span class="comparison-badge badge-neutral">Rango: {rango_sel[:30]}</span>'
        st.markdown(f'<div style="margin-bottom: 16px;"><strong>Filtros aplicados:</strong> {filtros_html}</div>', unsafe_allow_html=True)
    
    # Resumen estadistico mejorado
    render_chart_header(
        "Resumen Estadistico", 
        "Estadisticas descriptivas de las predicciones",
        "stats_resumen"
    )
    
    render_chart_info('''
        <strong>count:</strong> Numero de registros | <strong>mean:</strong> Promedio<br>
        <strong>std:</strong> Desviacion estandar | <strong>min/max:</strong> Valores extremos<br>
        <strong>25%/50%/75%:</strong> Percentiles (50% = mediana)
    ''', "blue", "stats_resumen")
    
    if len(pred_filtradas) > 0:
        stats = pred_filtradas[["tasa_base", "prediccion_tasa_t3", "variacion", "total_creditos_base"]].describe()
        stats.columns = ["Tasa Base (%)", "Tasa Predicha (%)", "Variacion (pp)", "Total Creditos"]
        st.dataframe(stats, use_container_width=True)
        
        # Descarga de estadisticas
        csv_stats = stats.to_csv().encode('utf-8')
        st.download_button(
            label="Descargar estadisticas CSV",
            data=csv_stats,
            file_name="estadisticas_predicciones.csv",
            mime="text/csv"
        )
    else:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")
    
    # Histograma mejorado con ordenamiento
    sort_hist = render_chart_header_with_sort(
        "Distribucion de Tasas", 
        "Frecuencia de predicciones por rango de tasa",
        "hist_tasas",
        sort_options=["Menor a mayor", "Mayor a menor"]
    )
    
    render_chart_info('''
        Muestra cuantas predicciones caen en cada rango de tasa.<br>
        Una <strong>distribucion concentrada</strong> indica tasas similares entre bancos.<br>
        Una <strong>distribucion dispersa</strong> indica mucha variedad.
    ''', "green", "hist_tasas")
    
    if len(pred_filtradas) > 0:
        # Ordenar datos del histograma
        hist_data = pred_filtradas.sort_values("prediccion_tasa_t3", ascending=(sort_hist == "Menor a mayor"))
        
        fig_hist = px.histogram(
            hist_data,
            x="prediccion_tasa_t3",
            nbins=20,
            color_discrete_sequence=["#2563EB"]
        )
        fig_hist.update_layout(
            plot_bgcolor=PLOT_BG,
            paper_bgcolor=PAPER_BG,
            font_color=FONT_COLOR,
            height=300,
            xaxis=dict(title=dict(text="Tasa Predicha (%)", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Frecuencia", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig_hist, use_container_width=True, key="hist_chart_tab4")
    
    # Box plot por banco con ordenamiento
    sort_box = render_chart_header_with_sort(
        "Box Plot por Banco", 
        "Variabilidad de tasas por entidad",
        "box_banco",
        sort_options=["Por mediana (menor)", "Por mediana (mayor)"]
    )
    
    render_chart_info('''
        <strong>Linea central:</strong> Mediana (valor del medio)<br>
        <strong>Caja:</strong> El 50% central de los datos<br>
        <strong>Bigotes:</strong> Rango de valores normales<br>
        <strong>Puntos fuera:</strong> Valores atipicos (outliers)<br><br>
        <em>Tip: Busca bancos con cajas bajas y pequenas (tasas bajas y consistentes).</em>
    ''', "amber", "box_banco")
    
    if len(pred_filtradas) > 0:
        # Calcular mediana por banco para ordenar
        mediana_por_banco = pred_filtradas.groupby("banco")["prediccion_tasa_t3"].median().sort_values(
            ascending=(sort_box == "Por mediana (menor)")
        )
        orden_bancos = mediana_por_banco.index.tolist()
        
        fig_box = px.box(
            pred_filtradas,
            x="banco",
            y="prediccion_tasa_t3",
            color="banco",
            color_discrete_sequence=px.colors.qualitative.Set3,
            category_orders={"banco": orden_bancos}
        )
        fig_box.update_layout(
            plot_bgcolor=PLOT_BG,
            paper_bgcolor=PAPER_BG,
            font_color=FONT_COLOR,
            height=350,
            showlegend=False,
            xaxis=dict(tickangle=-45, gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Tasa Predicha (%)", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
            margin=dict(l=0, r=0, t=10, b=100)
        )
        st.plotly_chart(fig_box, use_container_width=True, key="box_chart_tab4")
    
    # Scatter Tasa Base vs Predicha con ordenamiento
    sort_scatter = render_chart_header_with_sort(
        "Tasa Base vs Predicha", 
        "Relacion entre tasa actual y predicha",
        "scatter_base_pred",
        sort_options=["Por tasa predicha", "Por tasa base", "Por banco"]
    )
    
    render_chart_info('''
        <strong>Cada punto:</strong> Una combinacion banco + rango de monto<br>
        <strong>Linea diagonal:</strong> Referencia "sin cambio" (tasa queda igual)<br><br>
        <strong>Puntos debajo de la linea:</strong> La tasa bajara<br>
        <strong>Puntos arriba de la linea:</strong> La tasa subira
    ''', "blue", "scatter_base_pred")
    
    if len(pred_filtradas) > 0:
        # Ordenar segun seleccion
        if sort_scatter == "Por tasa predicha":
            scatter_data = pred_filtradas.sort_values("prediccion_tasa_t3")
        elif sort_scatter == "Por tasa base":
            scatter_data = pred_filtradas.sort_values("tasa_base")
        else:
            scatter_data = pred_filtradas.sort_values("banco")
        
        fig_scatter = px.scatter(
            scatter_data,
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
            plot_bgcolor=PLOT_BG,
            paper_bgcolor=PAPER_BG,
            font_color=FONT_COLOR,
            height=450,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
            xaxis=dict(title=dict(text="Tasa Base (%)", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
            yaxis=dict(title=dict(text="Tasa Predicha (%)", font=dict(color="#000000")), gridcolor=GRID_COLOR, tickfont=dict(color="#000000")),
            margin=dict(l=0, r=150, t=10, b=0)
        )
        st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_chart_tab4")
    
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
