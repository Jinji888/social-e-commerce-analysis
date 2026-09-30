import pandas as pd

# Leer SIN encabezado, para ver las primeras filas crudas
df_raw = pd.read_csv(
    "data/raw/instagram_orders.csv",
    encoding="utf-8",
    header=None,
    nrows=8,          # solo las primeras 8 filas
)

print("=== Primeras 8 filas crudas (sin encabezado) ===")
for i, row in df_raw.iterrows():
    print(f"\n--- Fila {i} ---")
    for j, valor in enumerate(row):
        # Mostramos los primeros 80 caracteres de cada celda
        texto = str(valor)[:80].replace("\n", "\\n")
        print(f"  Col {j}: {texto!r}")

print("\n=== Total de columnas: ===", df_raw.shape[1])

# Leer las últimas 5 filas
df_tail = pd.read_csv(
    "data/raw/instagram_orders.csv",
    encoding="utf-8",
    header=None,
    skipfooter=0,
)
print("\n=== Últimas 5 filas crudas ===")
print(df_tail.tail(5))