import pandas as pd
import re

df = pd.read_csv(
    "data/processed/instagram_clean_v4.csv",
    encoding="utf-8",
    na_values=[""],
    keep_default_na=False,
)

usuarios = df["usuario_ig"].dropna().astype(str)

print("Total usuarios:", len(usuarios))

# --- 1. Cuántos empiezan con @ ---
con_arroba = usuarios.str.startswith("@")
print("\nEmpiezan con @:", con_arroba.sum())

# --- 2. Cuántos contienen "/" (barra separadora) ---
con_barra = usuarios.str.contains("/", na=False)
print("Contienen '/':", con_barra.sum())

# --- 3. Cuántos contienen dígitos seguidos (posible teléfono) ---
con_digitos = usuarios.str.contains(r"\d{7,}", na=False)
print("Contienen 7+ dígitos seguidos:", con_digitos.sum())

# --- 4. Cuántos contienen la palabra 'instagram' ---
con_instagram = usuarios.str.lower().str.contains("instagram", na=False)
print("Contienen 'instagram':", con_instagram.sum())

# --- 5. Cuántos contienen espacios ---
con_espacios = usuarios.str.contains(" ", na=False)
print("Contienen espacios:", con_espacios.sum())

# --- 6. Muestra algunos ejemplos de cada caso (sin datos personales) ---
print("\n=== Ejemplos: contienen '/' o dígitos o 'instagram' ===")
casos_raros = usuarios[
    usuarios.str.contains(r"/|\d{7,}|instagram", case=False, na=False)
].head(20)
for u in casos_raros:
    # Mostramos solo los primeros 60 caracteres
    print(f"  {u[:60]!r}")

# --- 7. Longitud de los usuarios ---
print("\nLongitud (caracteres):")
print(usuarios.str.len().describe())