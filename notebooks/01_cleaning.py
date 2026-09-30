import pandas as pd

# ============================================
# PARTE A: Lectura y limpieza estructural
# ============================================

# Leer el CSV con BOM y quedarnos solo con las primeras 4 columnas
df = pd.read_csv(
    "data/raw/instagram_orders.csv",
    encoding="utf-8-sig",
    header=0,
    usecols=[0, 1, 2, 3],   # solo nos importan estas 4 columnas
)

# Renombrar columnas a nombres cortos y consistentes
df.columns = ["fecha", "usuario_ig", "paqueteria", "datos_envio"]

print("Filas tras leer CSV:", len(df))

# ============================================
# PARTE B: Diagnóstico y eliminación de basura
# ============================================

# --- Eliminar filas de prueba ---
# Buscamos "PRUEBA" en cualquier campo de la fila
mask_prueba = df.apply(
    lambda fila: fila.astype(str).str.contains("PRUEBA", case=False, na=False).any(),
    axis=1
)
print("\nFilas con 'PRUEBA':", mask_prueba.sum())

df = df[~mask_prueba].reset_index(drop=True)
print("Filas después de eliminar pruebas:", len(df))

# --- Revisar las primeras 5 filas para confirmar que empezamos con datos reales ---
print("\nPrimeras 5 filas después de limpieza:")
print(df.head(5))

# --- Tipos de datos ---
print("\nTipos de datos:")
print(df.dtypes)

# --- Valores nulos por columna ---
print("\nValores nulos por columna:")
print(df.isna().sum())

# --- Guardamos el resultado intermedio (sin sobreescribir el raw) ---
df.to_csv("data/processed/instagram_clean_v1.csv", index=False, encoding="utf-8")
print("\nGuardado en data/processed/instagram_clean_v1.csv")

"""
!r:
Modificador que se usa dentro de f-strings (las cadenas que empiezan con f"...").
Le dice a Python: "muéstrame el valor usando repr() en vez de str()

iloc — "index location"
iloc es la forma de seleccionar filas y columnas por posición numérica en pandas.

dtypes — "data types"
df.dtypes te dice el tipo de dato que pandas detectó en cada columna.

sea object, int64, float64, datetime64 o bool
"""
