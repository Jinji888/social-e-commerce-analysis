import pandas as pd

df = pd.read_csv(
    "data/processed/instagram_clean_v7.csv",
    encoding="utf-8",
    na_values=[""],
    keep_default_na=False,
)

envios = df["datos_envio"].dropna().astype(str)

print("Total direcciones:", len(envios))

# Longitud de cada dirección
longitudes = envios.str.len()
print("\nLongitud de las direcciones:")
print(longitudes.describe())

# Cuántas líneas tiene cada dirección (por los \n)
lineas = envios.str.count("\n") + 1
print("\nNúmero de líneas por dirección:")
print(lineas.value_counts().sort_index())

# Cuántas contienen la palabra "CP", "C.P.", "código postal"
print("\nContienen 'CP' o similar:")
con_cp = envios.str.contains(r"\bC\.?P\.?\b|\bc[oó]digo postal\b", case=False, regex=True)
print("  ", con_cp.sum())

# Cuántas contienen "Calle", "Av", "Avenida"
print("\nContienen indicador de calle:")
con_calle = envios.str.contains(r"\bcalle\b|\bav\.?\b|\bavenida\b|\bprivada\b", case=False, regex=True)
print("  ", con_calle.sum())

# Muestra 10 ejemplos (sin datos personales sensibles)
print("\n=== 10 ejemplos (primeros 200 caracteres) ===")
for i, e in enumerate(envios.head(10)):
    print(f"\n--- Ejemplo {i} ---")
    print(e[:200])