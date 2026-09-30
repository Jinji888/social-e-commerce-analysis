import pandas as pd

df = pd.read_csv(
    "data/processed/instagram_clean_v5.csv",
    encoding="utf-8",
    na_values=[""],
    keep_default_na=False,
)

vacios = df[df["usuario_ig"].isna()]

print(f"Filas con usuario vacío: {len(vacios)}")
print("\n=== Original vs limpiado ===")
for i, row in vacios.iterrows():
    orig = str(row["usuario_ig_original"])[:70]
    tiene_datos = pd.notna(row["datos_envio"]) and pd.notna(row["fecha"])
    print(f"\nFila {i} (tiene dirección/fecha: {tiene_datos})")
    print(f"  original: {orig!r}")