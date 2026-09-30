import duckdb

# Leer el archivo SQL
with open("sql/analysis.sql", "r", encoding="utf-8") as f:
    contenido = f.read()

# Dividir por punto y coma (;), ignorar bloques vacíos
queries = [q.strip() for q in contenido.split(";") if q.strip()]

# Conectar y ejecutar
con = duckdb.connect()

for i, q in enumerate(queries, 1):
    print(f"\n=== QUERY {i} ===")
    print(con.sql(q).df())

con.close()