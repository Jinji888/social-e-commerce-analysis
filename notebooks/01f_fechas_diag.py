import pandas as pd

# Leemos v2 (antes de la conversión de fechas) para ver los strings originales
df = pd.read_csv(
    "data/processed/instagram_clean_v2.csv",
    encoding="utf-8",
    na_values=[""],
    keep_default_na=False,
)

# Reaplicamos la eliminación de la fila abandonada
df = df[~(df["usuario_ig"].isna() & df["datos_envio"].isna())].reset_index(drop=True)

# Reaplicamos la conversión para localizar las problemáticas
df["fecha_dt"] = pd.to_datetime(
    df["fecha"], format="%d/%m/%Y %H:%M:%S", errors="coerce"
)

# --- Ver las 4 fechas inválidas ---
invalidas = df[df["fecha_dt"].isna()]
print("=== 4 fechas inválidas (string original) ===")
for i, row in invalidas.iterrows():
    print(f"\nFila {i}:")
    print(f"  fecha original: {row['fecha']!r}")
    print(f"  usuario: {row['usuario_ig']!r}")
    print(f"  paqueteria: {row['paqueteria']!r}")
    print(f"  dirección: {str(row['datos_envio'])[:80]!r}")

# --- Ver las fechas antes del 2020 (sospechosas) ---
print("\n=== Fechas sospechosas (< 2020) ===")
sospechosas = df[
    (df["fecha_dt"].notna()) & (df["fecha_dt"] < "2020-01-01")
]
for i, row in sospechosas.iterrows():
    print(f"\nFila {i}:")
    print(f"  fecha original: {row['fecha']!r}")
    print(f"  fecha parseada: {row['fecha_dt']}")
    print(f"  usuario: {row['usuario_ig']!r}")

# --- Rango real esperado ---
print("\n=== Distribución por año (solo válidas) ===")
df["año"] = df["fecha_dt"].dt.year
print(df["año"].value_counts().sort_index())