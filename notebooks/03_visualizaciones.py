import duckdb
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# ============================================
# Configuración
# ============================================
FIGURAS = Path("reports/figures")
FIGURAS.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()

# ============================================
# GRÁFICO 1: Crecimiento mensual de envíos
# ============================================
query = """
SELECT
    DATE_TRUNC('month', fecha) AS mes,
    COUNT(*) AS envios
FROM 'data/processed/instagram_clean_v8.csv'
WHERE fecha_confiable = true
GROUP BY 1
ORDER BY 1;
"""

df = con.sql(query).df()

plt.figure(figsize=(12, 5))
plt.plot(df["mes"], df["envios"], marker="o", linewidth=2, color="#2E86AB")
plt.title("Crecimiento mensual de envíos (Instagram)", fontsize=14)
plt.xlabel("Año/Mes")
plt.ylabel("Envíos")
plt.grid(alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(FIGURAS / "01_crecimiento_mensual.png", dpi=120, bbox_inches="tight")
plt.show()

print("Gráfico 1 guardado:", FIGURAS / "01_crecimiento_mensual.png")


# ============================================
# GRÁFICO 2: Top 10 estados por envíos
# ============================================
query = """
SELECT
    estado,
    COUNT(*) AS envios
FROM 'data/processed/instagram_clean_v8.csv'
WHERE estado IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10;
"""

df = con.sql(query).df()
df = df.sort_values("envios", ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(df["estado"], df["envios"], color="#A23B72")
plt.title("Top 10 estados por envíos", fontsize=14)
plt.xlabel("Envíos")
plt.ylabel("Estado")
plt.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURAS / "02_top_estados.png", dpi=120, bbox_inches="tight")
plt.show()

print("Gráfico 2 guardado:", FIGURAS / "02_top_estados.png")


# ============================================
# GRÁFICO 3: Estacionalidad — envíos por mes del año
# ============================================
query = """
SELECT
    EXTRACT(MONTH FROM fecha) AS mes_num,
    COUNT(*) AS envios
FROM 'data/processed/instagram_clean_v8.csv'
WHERE fecha_confiable = true
GROUP BY 1
ORDER BY 1;
"""

df = con.sql(query).df()

MESES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}
df["mes_nombre"] = df["mes_num"].map(MESES)

colores = ["#2E86AB" if m in (6, 7, 8) else "#B0B0B0" for m in df["mes_num"]]

plt.figure(figsize=(10, 5))
plt.bar(df["mes_nombre"], df["envios"], color=colores)
plt.title("Estacionalidad — envíos por mes del año (2024-2026)", fontsize=14)
plt.xlabel("Mes")
plt.ylabel("Envíos totales")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(FIGURAS / "03_estacionalidad.png", dpi=120, bbox_inches="tight")
plt.show()

print("Gráfico 3 guardado:", FIGURAS / "03_estacionalidad.png")


# ============================================
# GRÁFICO 4: Crecimiento anual
# ============================================
query = """
SELECT
    EXTRACT(YEAR FROM fecha) AS año,
    COUNT(*) AS envios
FROM 'data/processed/instagram_clean_v8.csv'
WHERE fecha_confiable = true
GROUP BY 1
ORDER BY 1;
"""

df = con.sql(query).df()

# Colorear 2026 diferente porque está incompleto (9 meses)
colores = ["#2E86AB", "#2E86AB", "#B0B0B0"]

plt.figure(figsize=(8, 5))
bars = plt.bar(df["año"].astype(int).astype(str), df["envios"], color=colores)
plt.title("Envíos totales por año", fontsize=14)
plt.xlabel("Año")
plt.ylabel("Envíos")
plt.grid(axis="y", alpha=0.3)

# Etiqueta de valor encima de cada barra
for bar in bars:
    altura = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, altura + 5,
            f"{int(altura)}", ha="center", fontsize=11)

plt.tight_layout()
plt.savefig(FIGURAS / "04_crecimiento_anual.png", dpi=120, bbox_inches="tight")
plt.show()

print("Gráfico 4 guardado:", FIGURAS / "04_crecimiento_anual.png")


# ============================================
# GRÁFICO 5: Tasa de recompra
# ============================================
query = """
SELECT
    CASE WHEN envios > 1 THEN 'Recurrentes' ELSE 'Una sola compra' END AS tipo,
    COUNT(*) AS clientes
FROM (
    SELECT usuario_ig, COUNT(*) AS envios
    FROM 'data/processed/instagram_clean_v8.csv'
    WHERE usuario_ig IS NOT NULL
    GROUP BY 1
) AS por_cliente
GROUP BY 1;
"""

df = con.sql(query).df()

plt.figure(figsize=(7, 6))
colores = ["#2E86AB", "#B0B0B0"]
plt.pie(df["clientes"], labels=df["tipo"], autopct="%1.1f%%",
        colors=colores, startangle=90, textprops={"fontsize": 12})
plt.title("Tasa de recompra de clientes", fontsize=14)
plt.tight_layout()
plt.savefig(FIGURAS / "05_recompra.png", dpi=150, bbox_inches="tight")
plt.show()

print("Gráfico 5 guardado:", FIGURAS / "05_recompra.png")


# ============================================
# Cierre
# ============================================
plt.close("all")
con.close()
print("\nTodos los gráficos fueron generados en reports/figures/ :) ")