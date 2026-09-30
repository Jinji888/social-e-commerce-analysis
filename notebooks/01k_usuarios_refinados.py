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

STOPWORDS = {
    "instagram", "user", "usuario", "ig", "num", "numero", "número",
    "tel", "telefono", "teléfono", "mi", "y", "o", "e", "a", "de",
    "también", "tambien", "dejaré", "dejare", "es", "el", "la", "los",
    "las", "por", "con", "para", "que", "en", "un", "una", "este", "esta",
    "no", "sin", "al", "del", "como", "más", "mas", "su", "se", "lo",
    "nan", "none", "null",
}

def limpiar_usuario(u):
    if pd.isna(u):
        return None
    
    u = str(u)
    
    # 1. Normalizar unicode
    u = unicodedata.normalize("NFKC", u)
    
    # 2. Reemplazar caracteres invisibles por espacio
    u = re.sub(r"[\u200b-\u200f\u202a-\u202e\xa0]", " ", u)
    
    # 3. Quitar apóstrofes y comillas tipográficas
    u = u.replace("'", "").replace("'", "").replace("`", "").replace("´", "")
    
    # 4. Minúsculas y limpiar
    u = u.lower().strip()
    
    # 5. Si es literalmente "nan", "none", "null", fuera
    if u in ("nan", "none", "null", ""):
        return None
    
    # 6. Dividir por separadores
    tokens = re.split(r"[/,;:()\-\s]+", u)
    
    candidatos = []
    for tok in tokens:
        tok = tok.strip().lstrip("@").strip(".").strip()
        if not tok:
            continue
        # Descartar si es puro número (teléfono)
        if re.fullmatch(r"\+?\d+", tok):
            continue
        # Descartar stopwords
        if tok in STOPWORDS:
            continue
        # Descartar si NO tiene al menos una letra
        if not re.search(r"[a-z]", tok):
            continue
        # Limpiar caracteres no válidos (dejar solo letras a-z, números, ., _, y algunos unicode)
        tok = re.sub(r"[^a-z0-9._\u00c0-\u024f]", "", tok)
        # Después de limpiar, descartar si quedó vacío o muy corto
        if len(tok) < 3:
            continue
        candidatos.append(tok)
    
    if not candidatos:
        return None
    
    return max(candidatos, key=len)[:30]

df["usuario_ig_original"] = df["usuario_ig"]
df["usuario_ig"] = df["usuario_ig"].apply(limpiar_usuario)

# ============================================
# Marcar clientes sin handle (pero con datos válidos)
# ============================================
df["tiene_handle"] = df["usuario_ig"].notna()

print("\nCon handle:", df["tiene_handle"].sum())
print("Sin handle:", (~df["tiene_handle"]).sum())

# ============================================
# Reporte de los que aún quedan sin handle
# ============================================
print("\n=== Casos sin handle (original) ===")
sin_handle = df[~df["tiene_handle"]]
for _, row in sin_handle.head(25).iterrows():
    orig = str(row["usuario_ig_original"])[:50]
    print(f"  {orig!r}")

# ============================================
# Verificar que los 2 casos raros se rescataron
# ============================================
print("\n=== Verificar rescates ===")
for patron in ["It's.mxnni", "Milokix", "lu ar lu"]:
    match = df[df["usuario_ig_original"].astype(str).str.contains(patron[:5], case=False, na=False, regex=False)]
    if len(match) > 0:
        print(f"  '{patron}':")
        for _, row in match.head(2).iterrows():
            print(f"    original: {row['usuario_ig_original']!r} -> limpio: {row['usuario_ig']!r}")

# ============================================
# Usuarios únicos
# ============================================
print("\nUsuarios únicos:", df["usuario_ig"].nunique())

# ============================================
# Guardar v6
# ============================================
df.to_csv("data/processed/instagram_clean_v6.csv", index=False, encoding="utf-8")
print("\nGuardado en data/processed/instagram_clean_v6.csv")