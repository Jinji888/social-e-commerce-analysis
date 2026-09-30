# Explicación de Consulta SQL: Análisis de Clientes en Instagram

Este documento contiene la explicación paso a paso de la consulta SQL utilizada para analizar el comportamiento y la tasa de recompra de los clientes a partir de los datos de Instagram.

## 📝 La Consulta SQL Completa

```sql
SELECT 
    COUNT(*) AS total_clientes, 
    SUM(CASE WHEN envios > 1 THEN 1 ELSE 0 END) AS recurrentes, 
    ROUND(100.0 * SUM(CASE WHEN envios > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_recompra, 
    ROUND(AVG(envios), 2) AS envios_promedio 
FROM ( 
    SELECT 
        usuario_ig, 
        COUNT(*) AS envios 
    FROM 'data/processed/instagram_clean_v8.csv' 
    WHERE usuario_ig IS NOT NULL 
    GROUP BY 1 
) AS por_cliente;
```

---

## 📦 1. La subconsulta interna (El bloque de adentro)

Este bloque toma el archivo original y crea una lista temporal con cada cliente y su número de envíos.

* **`SELECT usuario_ig, COUNT(*) AS envios`**
  Selecciona el nombre de usuario de Instagram (`usuario_ig`) y cuenta cuántas filas (registros) tiene cada uno en la tabla. A ese conteo le pone el apodo o alias de `envios`.
* **`FROM 'data/processed/instagram_clean_v8.csv'`**
  Le indica al sistema de dónde sacar los datos, que en este caso es un archivo de texto plano (CSV) con los datos limpios de Instagram.
* **`WHERE usuario_ig IS NOT NULL`**
  Filtra los datos para ignorar cualquier fila que no tenga un usuario de Instagram (deja fuera los valores vacíos o nulos).
* **`GROUP BY 1`**
  Agrupa los resultados por la primera columna mencionada en el `SELECT` (es decir, por `usuario_ig`). Esto hace que si un usuario aparece 5 veces en el archivo, se junte en una sola fila y el `COUNT(*)` devuelva un 5.
* **`) AS por_cliente;`**
  Cierra este bloque interno y le da el nombre temporal de `por_cliente`. A partir de aquí, la consulta de afuera tratará a este bloque como si fuera una tabla nueva con dos columnas: `usuario_ig` y `envios`.

---

## 📊 2. La consulta externa (El bloque de afuera)

Este bloque toma la lista que creamos arriba y calcula los porcentajes y totales finales.

* **`SELECT COUNT(*) AS total_clientes,`**
  Cuenta cuántas filas tiene la tabla temporal `por_cliente`. Como cada fila representa a un usuario único, esto nos da el total de clientes únicos.
* **`SUM(CASE WHEN envios > 1 THEN 1 ELSE 0 END) AS recurrentes,`**
  Esta es una condicional. Va cliente por cliente mirando su número de envíos: si el cliente tiene más de 1 envío, le asigna un 1; si tiene solo 1 envío, le asigna un 0. Al final, suma todos esos unos y ceros, lo que te da el total de clientes que han comprado más de una vez.
* **`ROUND(100.0 * SUM(CASE WHEN envios > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_recompra,`**
  Calcula el porcentaje de clientes fieles. Toma el número de clientes recurrentes (la suma de unos), lo multiplica por 100.0 (el .0 fuerza a SQL a usar decimales para que la división sea exacta), lo divide entre el total de clientes y, finalmente, la función `ROUND(..., 2)` lo redondea a dos decimales.
* **`ROUND(AVG(envios), 2) AS envios_promedio`**
  Calcula el promedio de la columna `envios` usando la función `AVG()`. Te dice, en promedio, cuántos envíos hace un cliente. También lo redondea a dos decimales.
* **`FROM (`**
  Le dice a la consulta externa que no va a leer el archivo CSV directamente, sino que va a usar los resultados del bloque interno que explicamos en el paso 1.