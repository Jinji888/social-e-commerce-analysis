import pandas as pd

# Leemos v3 SIN parsear todavía
df = pd.read_csv(
    "data/processed/instagram_clean_v3.csv",
    encoding="utf-8",
    na_values=[""],
    keep_default_na=False,
)

print("Filas iniciales:", len(df))

# ============================================
# 1. Parsear fecha automáticamente (sin format)
# ============================================
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

print("\nFechas válidas antes de corregir:", df["fecha"].notna().sum())
print("Fechas NaT antes de corregir:", df["fecha"].isna().sum())

# ============================================
# 2. Corregir la del año 1774
# ============================================
mask_1774 = df["fecha"].dt.year == 1774
print("\nFilas con año 1774:", mask_1774.sum())

df.loc[mask_1774, "fecha"] = pd.Timestamp("2024-04-26")
print("Corregida a: 2024-04-26")

# ============================================
# 3. Bandera de confiabilidad
# ============================================
df["fecha_confiable"] = df["fecha"].notna()

print("\nConfiabilidad:")
print(df["fecha_confiable"].value_counts())

# ============================================
# 4. Validar rango
# ============================================
print("\nRango de fechas válidas:")
print("  Primera:", df["fecha"].min())
print("  Última:", df["fecha"].max())

print("\nDistribución por año:")
print(df["fecha"].dt.year.value_counts().sort_index())

# ============================================
# 5. Guardar v4
# ============================================
df.to_csv("data/processed/instagram_clean_v4.csv", index=False, encoding="utf-8")
print("\nGuardado en data/processed/instagram_clean_v4.csv")