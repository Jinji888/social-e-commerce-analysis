import pandas as pd
import re

df = pd.read_csv(
    "data/processed/instagram_clean_v7.csv",
    encoding="utf-8",
    na_values=[""],
    keep_default_na=False,
)

print("Filas iniciales:", len(df))

# ============================================
# Lista de estados de México con variantes comunes
# ============================================
ESTADOS = {
    "aguascalientes": "Aguascalientes",
    "baja california sur": "Baja California Sur",
    "baja california": "Baja California",
    "bcs": "Baja California Sur",
    "bc": "Baja California",
    "campeche": "Campeche",
    "chiapas": "Chiapas",
    "chihuahua": "Chihuahua",
    "ciudad de mexico": "Ciudad de México",
    "ciudad de méxico": "Ciudad de México",
    "cdmx": "Ciudad de México",
    "distrito federal": "Ciudad de México",
    "df": "Ciudad de México",
    "coahuila": "Coahuila",
    "colima": "Colima",
    "durango": "Durango",
    "edomex": "Estado de México",
    "estado de mexico": "Estado de México",
    "estado de méxico": "Estado de México",
    "guanajuato": "Guanajuato",
    "guerrero": "Guerrero",
    "hidalgo": "Hidalgo",
    "jalisco": "Jalisco",
    "michoacan": "Michoacán",
    "michoacán": "Michoacán",
    "morelos": "Morelos",
    "nayarit": "Nayarit",
    "nuevo leon": "Nuevo León",
    "nuevo león": "Nuevo León",
    "oaxaca": "Oaxaca",
    "puebla": "Puebla",
    "queretaro": "Querétaro",
    "querétaro": "Querétaro",
    "quintana roo": "Quintana Roo",
    "san luis potosi": "San Luis Potosí",
    "san luis potosí": "San Luis Potosí",
    "sinaloa": "Sinaloa",
    "sonora": "Sonora",
    "tabasco": "Tabasco",
    "tamaulipas": "Tamaulipas",
    "tlaxcala": "Tlaxcala",
    "veracruz": "Veracruz",
    "yucatan": "Yucatán",
    "yucatán": "Yucatán",
    "zacatecas": "Zacatecas",
}

# ============================================
# Funciones extractoras
# ============================================
def extraer_cp(texto):
    if pd.isna(texto):
        return None
    t = str(texto)
    # Buscar 5 dígitos que NO estén pegados a más dígitos (evita teléfonos)
    # (?<!\d) = no precedido por dígito
    # (\d{5}) = exactamente 5 dígitos
    # (?!\d) = no seguido por dígito
    # Primero intentamos con contexto explícito (CP, C.P., código postal)
    match_ctx = re.search(
        r"(?:c\.?\s*p\.?|c[oó]digo\s+postal)[:\s]*(\d{5})(?!\d)",
        t, re.IGNORECASE
    )
    if match_ctx:
        return match_ctx.group(1)
    # Fallback: cualquier 5 dígitos aislados
    matches = re.findall(r"(?<!\d)(\d{5})(?!\d)", t)
    if matches:
        return matches[0]
    return None

def extraer_estado(texto):
    if pd.isna(texto):
        return None
    t = " " + str(texto).lower() + " "
    # Reemplazar puntuación por espacios para que \b funcione bien
    t = re.sub(r"[^\w\s]", " ", t)
    # Ordenar por longitud descendente para evitar matches parciales
    # (ej. "baja california sur" antes que "baja california")
    for clave in sorted(ESTADOS.keys(), key=len, reverse=True):
        patron = r"\b" + re.escape(clave) + r"\b"
        if re.search(patron, t):
            return ESTADOS[clave]
    return None

def extraer_telefono(texto):
    if pd.isna(texto):
        return None
    t = str(texto)
    patron = r"(?<!\d)(?:\+?52[\s\-]?)?(\d{2,3})[\s\-]?(\d{3,4})[\s\-]?(\d{4})(?!\d)"
    match = re.search(patron, t)
    if match:
        num = re.sub(r"\D", "", match.group(0))
        # Si tiene 12 dígitos y empieza con 52, quitarlo
        if len(num) == 12 and num.startswith("52"):
            num = num[2:]
        # Si tiene 13 y empieza con 521, quitarlo (WhatsApp MX)
        if len(num) == 13 and num.startswith("521"):
            num = num[3:]
        # Validar que queden exactamente 10 dígitos
        if len(num) == 10:
            return num
    return None

# ============================================
# Aplicar extracción
# ============================================
df["cp"] = df["datos_envio"].apply(extraer_cp)
df["estado"] = df["datos_envio"].apply(extraer_estado)
df["telefono_extraido"] = df["datos_envio"].apply(extraer_telefono)

# ============================================
# Reporte
# ============================================
total = len(df)
print(f"\n=== Resultados de extracción ===")
print(f"CP extraído:       {df['cp'].notna().sum():4} ({100*df['cp'].notna().sum()/total:.1f}%)")
print(f"Estado extraído:   {df['estado'].notna().sum():4} ({100*df['estado'].notna().sum()/total:.1f}%)")
print(f"Teléfono extraído: {df['telefono_extraido'].notna().sum():4} ({100*df['telefono_extraido'].notna().sum()/total:.1f}%)")

print("\n=== Top 15 estados ===")
print(df["estado"].value_counts().head(15))

print("\n=== Top 15 CPs ===")
print(df["cp"].value_counts().head(15))

# ============================================
# Verificar algunos casos (sin datos personales)
# ============================================
print("\n=== Verificación: 5 ejemplos (CP, estado, teléfono) ===")
for i in range(min(5, len(df))):
    row = df.iloc[i]
    print(f"\nFila {i}:")
    print(f"  CP:       {row['cp']}")
    print(f"  Estado:   {row['estado']}")
    print(f"  Teléfono: {row['telefono_extraido']}")

# ============================================
# Guardar v8
# ============================================
df.to_csv("data/processed/instagram_clean_v8.csv", index=False, encoding="utf-8")
print("\nGuardado en data/processed/instagram_clean_v8.csv")

