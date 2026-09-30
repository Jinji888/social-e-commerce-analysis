import pandas as pd

df = pd.read_csv(
    "data/processed/instagram_clean_v6.csv",
    encoding="utf-8",
    na_values=[""],
    keep_default_na=False,
)

print("Filas iniciales:", len(df))

# ============================================
# 1. Ver variantes originales
# ============================================
print("\n=== Variantes únicas (antes) ===")
print(df["paqueteria"].value_counts(dropna=False))

# ============================================
# 2. Guardar el original ANTES de sobrescribir
# ============================================
df["paqueteria_original"] = df["paqueteria"]

# ============================================
# 3. Normalizar
# ============================================
def normalizar_paqueteria(p):
    if pd.isna(p):
        return "Desconocida"
    
    p_upper = str(p).upper()
    
    if "CORREOS" in p_upper or "POSTAL MEXICANA" in p_upper:
        return "Correos de México"
    
    if "ESTAFETA" in p_upper:
        return "Estafeta"
    
    return "Desconocida"

df["paqueteria"] = df["paqueteria"].apply(normalizar_paqueteria)

# ============================================
# 4. Detectar caso especial (pidió Estafeta, se envió Correos)
# ============================================

# ============================================
# 5. Reporte
# ============================================
print("\n=== Variantes únicas (después) ===")
print(df["paqueteria"].value_counts())

print("\nPorcentajes:")
print((df["paqueteria"].value_counts(normalize=True) * 100).round(2))

# ============================================
# 6. Guardar v7
# ============================================
df.to_csv("data/processed/instagram_clean_v7.csv", index=False, encoding="utf-8")
print("\nGuardado en data/processed/instagram_clean_v7.csv")