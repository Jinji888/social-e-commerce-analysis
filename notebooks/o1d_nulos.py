import pandas as pd

df = pd.read_csv(
    "data/processed/instagram_clean_v1.csv",
    encoding="utf-8",
    na_values=[""],   # solo celdas vacías = nulo
    keep_default_na=False,
)

print("Filas iniciales:", len(df))

# ============================================
# 1. Filas completamente vacías (al final del archivo)
# ============================================
vacias = df.isna().all(axis=1)
print("\nFilas completamente vacías:", vacias.sum())

# ============================================
# 2. Filas sin fecha (probablemente basura o mal formadas)
# ============================================
sin_fecha = df["fecha"].isna()
print("Filas sin fecha:", sin_fecha.sum())
print("\nEjemplos de filas sin fecha:")
print(df[sin_fecha].head(10))

# ============================================
# 3. Filas con fecha pero sin usuario/dirección
# ============================================
sin_datos = df["fecha"].notna() & df["usuario_ig"].isna() & df["datos_envio"].isna()
print("\nFilas con fecha pero sin usuario ni dirección:", sin_datos.sum())
if sin_datos.sum() > 0:
    print(df[sin_datos].head(10))

# ============================================
# 4. Eliminar solo las filas completamente vacías
# ============================================
df = df[~vacias].reset_index(drop=True)
print("\nFilas tras eliminar completamente vacías:", len(df))

# ============================================
# 5. Verificar cuántos "N/A" hay ahora
# ============================================
mask_na = df.apply(
    lambda fila: fila.astype(str).str.contains(r"\bN/?A\b", case=False, na=False).any(),
    axis=1
)
print("\nFilas que contienen 'N/A' como texto:", mask_na.sum())

# ============================================
# 6. Guardar v2
# ============================================
df.to_csv("data/processed/instagram_clean_v2.csv", index=False, encoding="utf-8")
print("Guardado en data/processed/instagram_clean_v2.csv")