import pandas as pd

df = pd.read_csv(
    "data/processed/instagram_clean_v2.csv",
    encoding="utf-8",
    na_values=[""],
    keep_default_na=False,
)

print("Filas iniciales:", len(df))

# ============================================
# 1. Eliminar fila con solo fecha (abandonada)
# ============================================
sin_datos = df["usuario_ig"].isna() & df["datos_envio"].isna()
print("\nFilas con fecha pero sin usuario ni dirección:", sin_datos.sum())

df = df[~sin_datos].reset_index(drop=True)
print("Filas tras eliminar abandonadas:", len(df))

# ============================================
# 2. Convertir fecha a datetime
# ============================================
# El formato es "24/5/2024 12:25:33" -> día/mes/año hora
# dayfirst=True porque el día va primero
df["fecha"] = pd.to_datetime(
    df["fecha"],
    format="%d/%m/%Y %H:%M:%S",
    errors="coerce",
)

print("\nFechas convertidas:")
print("  Válidas:", df["fecha"].notna().sum())
print("  Inválidas (NaT):", df["fecha"].isna().sum())
print("  Primera:", df["fecha"].min())
print("  Última:", df["fecha"].max())

# ============================================
# 3. Mostrar las filas con fecha inválida (si hay)
# ============================================
invalidas = df[df["fecha"].isna()]
if len(invalidas) > 0:
    print("\n=== Filas con fecha inválida ===")
    print(invalidas.head(10))

# ============================================
# 4. Guardar v3
# ============================================
df.to_csv("data/processed/instagram_clean_v3.csv", index=False, encoding="utf-8")
print("\nGuardado en data/processed/instagram_clean_v3.csv")