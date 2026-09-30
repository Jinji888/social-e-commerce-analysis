import pandas as pd
import re
import unicodedata

df = pd.read_csv(
    "data/processed/instagram_clean_v4.csv",
    encoding="utf-8",
    na_values=[""],
    keep_default_na=False,
)

print("Filas iniciales:", len(df))

# ============================================
# Palabras que NO son handles (stopwords)
# ============================================
STOPWORDS = {
    "instagram", "user", "usuario", "ig", "num", "numero", "número",
    "tel", "telefono", "teléfono", "mi", "y", "o", "e", "a", "de",
    "también", "tambien", "dejaré", "dejare", "es", "el", "la", "los",
    "las", "por", "con", "para", "que", "en", "un", "una", "este", "esta",
    "no", "sin", "al", "del", "como", "más", "mas", "su", "se", "lo",
}

def limpiar_usuario(u):
    """Extrae el handle de Instagram más probable de un campo sucio."""
    if pd.isna(u):
        return None
    
    u = str(u)
    
    # 1. Normalizar unicode (ñ -> ñ, combina acentos, etc.)
    u = unicodedata.normalize("NFKC", u)
    
    # 2. Quitar caracteres invisibles de control (zero-width, dirección LTR/RTL)
    #    \u200b-\u200f: espacios invisibles
    #    \u202a-\u202e: marcadores de dirección
    #    \xa0: espacio duro
    u = re.sub(r"[\u200b-\u200f\u202a-\u202e\xa0]", " ", u)
    
    # 3. Minúsculas y limpiar extremos
    u = u.lower().strip()
    
    # 4. Dividir por cualquier separador común
    #    Incluye: / , ; : ( ) - _ y espacios (deja _ y . porque son válidos en IG)
    tokens = re.split(r"[/,;:()\-\s]+", u)
    
    candidatos = []
    for tok in tokens:
        tok = tok.strip().lstrip("@").strip(".").strip()
        if not tok:
            continue
        # Descartar si es puro dígito (teléfono)
        if re.fullmatch(r"\+?\d+", tok):
            continue
        # Descartar si es una stopword
        if tok in STOPWORDS:
            continue
        # Descartar si tiene caracteres no válidos en IG (solo letras, números, ., _)
        if not re.fullmatch(r"[a-z0-9._]+", tok):
            continue
        # Descartar muy cortos
        if len(tok) < 3:
            continue
        candidatos.append(tok)
    
    if not candidatos:
        return None
    
    # 5. Elegir el más largo (los handles suelen ser más largos que nombres)
    return max(candidatos, key=len)[:30]

# ============================================
# Aplicar la limpieza
# ============================================
df["usuario_ig_original"] = df["usuario_ig"]
df["usuario_ig"] = df["usuario_ig"].apply(limpiar_usuario)

# ============================================
# Reporte
# ============================================
print("\nUsuarios limpios:", df["usuario_ig"].notna().sum())
print("Usuarios vacíos tras limpieza:", df["usuario_ig"].isna().sum())

# Muestra ejemplos donde cambió mucho
df["cambio"] = df["usuario_ig_original"].astype(str) != df["usuario_ig"].astype(str)
print("\nFilas donde el valor cambió:", df["cambio"].sum())

print("\n=== 20 ejemplos de limpieza ===")
for _, row in df[df["cambio"]].head(20).iterrows():
    orig = str(row["usuario_ig_original"])[:50]
    nuevo = str(row["usuario_ig"])[:30]
    print(f"  {orig!r:55} -> {nuevo!r}")

# Verificar duplicados ahora
print("\nUsuarios únicos:", df["usuario_ig"].nunique())

# ============================================
# Guardar v5
# ============================================
df.to_csv("data/processed/instagram_clean_v5.csv", index=False, encoding="utf-8")
print("\nGuardado en data/processed/instagram_clean_v5.csv")