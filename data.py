"""
Carga dinamica de datos desde los CSVs generados por el notebook de modelado.

Archivos esperados en la carpeta data/:
- predicciones_t3.csv (109 filas) - Predicciones finales
- metricas_modelos_t3.csv (40 filas) - Metricas por modelo/nivel
- mejores_modelos_t3.csv (4 filas) - Mejor modelo por nivel
- criterio_seleccion_modelos_t3.csv - Criterios de seleccion
- tasas_ponderadas_banco_rango_mes.csv - Historico del ETL
"""
import os
import pandas as pd
import numpy as np

# =============================================================================
# RUTAS DE ARCHIVOS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Crear carpeta data si no existe
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def _find_csv(name: str) -> str:
    """Busca el CSV en varias ubicaciones posibles."""
    candidates = [
        # Carpeta data/outputs_modelado/ (donde se extrajeron los ZIPs)
        os.path.join(DATA_DIR, "outputs_modelado", name),
        # Carpeta data/outputs/ (donde se extrajeron los ZIPs del ETL)
        os.path.join(DATA_DIR, "outputs", name),
        # Carpeta data/ directamente
        os.path.join(DATA_DIR, name),
        # Carpeta base
        os.path.join(BASE_DIR, name),
        # Carpetas hermanas
        os.path.join(BASE_DIR, "..", "outputs_modelado", name),
        os.path.join(BASE_DIR, "..", "mlops-tasas", "outputs_modelado", name),
        os.path.join(BASE_DIR, "..", "outputs", name),
        os.path.join(BASE_DIR, "..", name),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return os.path.join(DATA_DIR, name)  # fallback


# =============================================================================
# CARGA DE PREDICCIONES (predicciones_t3.csv)
# Columnas: banco, rango_orden, rango_monto, serie_banco_rango, nivel_usado,
#           serie_usada, modelo_usado, mes_base, mes_predicho, tasa_base,
#           prediccion_tasa_t3, total_creditos_base
# =============================================================================
def get_predicciones_df() -> pd.DataFrame:
    csv_path = _find_csv("predicciones_t3.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        
        # Calcular variacion si no existe
        if "variacion" not in df.columns:
            if "prediccion_tasa_t3" in df.columns and "tasa_base" in df.columns:
                df["variacion"] = df["prediccion_tasa_t3"] - df["tasa_base"]
            else:
                df["variacion"] = 0.0
        
        # Asegurar columnas necesarias
        required_cols = ["banco", "rango_monto", "mes_base", "mes_predicho", 
                        "tasa_base", "prediccion_tasa_t3", "variacion",
                        "modelo_usado", "total_creditos_base", "nivel_usado"]
        for col in required_cols:
            if col not in df.columns:
                df[col] = "N/A" if col in ["banco", "rango_monto", "modelo_usado", "nivel_usado", "mes_base", "mes_predicho"] else 0.0
        
        return df
    
    # Si no hay archivo, retornar DataFrame vacio con estructura
    print(f"AVISO: No se encontro {csv_path}")
    return pd.DataFrame(columns=[
        "banco", "rango_orden", "rango_monto", "serie_banco_rango", "nivel_usado",
        "serie_usada", "modelo_usado", "mes_base", "mes_predicho", "tasa_base",
        "prediccion_tasa_t3", "total_creditos_base", "variacion"
    ])


# =============================================================================
# CARGA DE METRICAS (metricas_modelos_t3.csv)
# Columnas: nivel, modelo, split, r2, mae, rmse, smape
# =============================================================================
def get_metricas_df() -> pd.DataFrame:
    csv_path = _find_csv("metricas_modelos_t3.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip().str.lower()
        return df
    
    print(f"AVISO: No se encontro {csv_path}")
    return pd.DataFrame(columns=["nivel", "modelo", "split", "r2", "mae", "rmse", "smape"])


# =============================================================================
# CARGA DE MEJORES MODELOS (mejores_modelos_t3.csv)
# =============================================================================
def get_mejores_modelos_df() -> pd.DataFrame:
    csv_path = _find_csv("mejores_modelos_t3.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip().str.lower()
        return df
    
    print(f"AVISO: No se encontro {csv_path}")
    return pd.DataFrame(columns=["nivel", "modelo", "r2", "mae", "rmse"])


# =============================================================================
# CARGA DE CRITERIO DE SELECCION (criterio_seleccion_modelos_t3.csv)
# =============================================================================
def get_criterio_df() -> pd.DataFrame:
    csv_path = _find_csv("criterio_seleccion_modelos_t3.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip().str.lower()
        return df
    
    # Fallback con datos del notebook
    data = [
        {"nivel": "banco_rango", "modelo_elegido": "HistGradientBoosting", "r2": 0.93, "mae": 0.41, "descripcion": "Modelo granular por banco y rango"},
        {"nivel": "banco", "modelo_elegido": "ExtraTrees", "r2": 0.90, "mae": 0.52, "descripcion": "Fallback por entidad bancaria"},
        {"nivel": "rango", "modelo_elegido": "Ridge", "r2": 0.85, "mae": 0.65, "descripcion": "Fallback por rango de monto"},
        {"nivel": "total", "modelo_elegido": "ElasticNet", "r2": 0.80, "mae": 0.78, "descripcion": "Fallback global del sistema"},
    ]
    return pd.DataFrame(data)


# =============================================================================
# CARGA DE HISTORICO (tasas_ponderadas_banco_rango_mes.csv del ETL)
# Columnas: mes, banco, rango_orden, rango_monto, suma_tasa_credito,
#           total_creditos, registros_fuente, fecha_minima, fecha_maxima, tasa_ponderada
# =============================================================================
def get_historico_df() -> pd.DataFrame:
    # Intentar primero el archivo del ETL
    csv_path = _find_csv("tasas_ponderadas_banco_rango_mes.csv")
    
    if not os.path.exists(csv_path):
        # Intentar alternativas
        csv_path = _find_csv("tasas_ponderadas_por_rango_2023-2026.csv")
    
    if not os.path.exists(csv_path):
        csv_path = _find_csv("historico_tasas_rango.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        
        # Normalizar nombres de columnas
        rename_map = {
            "nombre_entidad": "banco",
            "rango_monto_desembolsado": "rango_monto",
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
        
        # Asegurar columna tasa_ponderada
        if "tasa_ponderada" not in df.columns and "tasa" in df.columns:
            df["tasa_ponderada"] = df["tasa"]
        
        return df
    
    print(f"AVISO: No se encontro archivo de historico")
    return pd.DataFrame(columns=["mes", "banco", "rango_monto", "tasa_ponderada", "total_creditos"])


def get_historico_total_df() -> pd.DataFrame:
    """Tasa promedio ponderada mensual global."""
    df = get_historico_df()
    if df.empty:
        return pd.DataFrame(columns=["mes", "tasa_prom"])
    
    # Agrupar por mes
    grp = df.groupby("mes").apply(
        lambda g: np.average(g["tasa_ponderada"], weights=g["total_creditos"].clip(lower=1)) 
        if "total_creditos" in g.columns and g["total_creditos"].sum() > 0
        else g["tasa_ponderada"].mean()
    ).reset_index(name="tasa_prom")
    
    return grp


# =============================================================================
# CARGA DE FALLBACK DECISIONS (fallback_decisions_t3.csv)
# =============================================================================
def get_fallback_df() -> pd.DataFrame:
    csv_path = _find_csv("fallback_decisions_t3.csv")
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        return df
    
    return pd.DataFrame()


# =============================================================================
# RANKING DE BANCOS
# =============================================================================
def get_ranking_df() -> pd.DataFrame:
    pred = get_predicciones_df()
    if pred.empty:
        return pd.DataFrame(columns=["banco", "tasa_predicha", "total_creditos", "tasa_base", "posicion"])
    
    rank = pred.groupby("banco").agg(
        tasa_predicha=("prediccion_tasa_t3", "mean"),
        total_creditos=("total_creditos_base", "sum"),
        tasa_base=("tasa_base", "mean"),
    ).reset_index()
    rank = rank.sort_values("tasa_predicha").reset_index(drop=True)
    rank["posicion"] = range(1, len(rank) + 1)
    return rank


# =============================================================================
# LISTAS DINAMICAS PARA FILTROS
# =============================================================================
def get_bancos() -> list:
    pred = get_predicciones_df()
    if pred.empty or "banco" not in pred.columns:
        hist = get_historico_df()
        if not hist.empty and "banco" in hist.columns:
            return sorted(hist["banco"].unique().tolist())
        return []
    return sorted(pred["banco"].unique().tolist())


def get_rangos() -> list:
    pred = get_predicciones_df()
    if pred.empty or "rango_monto" not in pred.columns:
        hist = get_historico_df()
        if not hist.empty and "rango_monto" in hist.columns:
            return sorted(hist["rango_monto"].unique().tolist())
        return []
    return sorted(pred["rango_monto"].unique().tolist())


def get_meses() -> list:
    hist = get_historico_df()
    if hist.empty or "mes" not in hist.columns:
        return []
    return sorted(hist["mes"].unique().tolist())


def get_niveles() -> list:
    pred = get_predicciones_df()
    if pred.empty or "nivel_usado" not in pred.columns:
        return ["banco_rango", "banco", "rango", "total"]
    return sorted(pred["nivel_usado"].unique().tolist())


# =============================================================================
# KPIs GLOBALES
# =============================================================================
def get_kpis() -> dict:
    pred = get_predicciones_df()
    hist = get_historico_df()
    
    if pred.empty:
        return {
            "total_predicciones": 0,
            "tasa_promedio": 0.0,
            "tasa_minima": 0.0,
            "tasa_maxima": 0.0,
            "periodo": "Sin datos",
            "mes_prediccion": "N/A",
        }
    
    return {
        "total_predicciones": len(pred),
        "tasa_promedio": pred["prediccion_tasa_t3"].mean(),
        "tasa_minima": pred["prediccion_tasa_t3"].min(),
        "tasa_maxima": pred["prediccion_tasa_t3"].max(),
        "periodo": f"{hist['mes'].min()} - {hist['mes'].max()}" if not hist.empty else "N/A",
        "mes_prediccion": pred["mes_predicho"].iloc[0] if "mes_predicho" in pred.columns else "T+3",
    }


# =============================================================================
# COMPATIBILIDAD CON IMPORTS ANTERIORES
# =============================================================================
KPIS = get_kpis()
NIVELES = get_niveles()
