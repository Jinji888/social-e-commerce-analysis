-- ============================================================
-- Q1: Crecimiento mensual de envíos
-- Objetivo: ver cómo evolucionó el volumen de envíos mes a mes
-- NOTA: cada fila = 1 envío (puede contener varios productos/pedidos)
-- ============================================================
SELECT
    DATE_TRUNC('month', fecha) AS mes,
    COUNT(*) AS envios,
    COUNT(DISTINCT usuario_ig) AS clientes_unicos,
    SUM(COUNT(*)) OVER (ORDER BY DATE_TRUNC('month', fecha)) AS envios_acumulados
FROM 'data/processed/instagram_clean_v8.csv'
WHERE fecha_confiable = true
GROUP BY 1
ORDER BY 1;

-- ============================================================
-- Q2: Top 15 estados por envíos
-- Objetivo: ver la distribución geográfica de los clientes
-- ============================================================
SELECT
    estado,
    COUNT(*) AS envios,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct
FROM 'data/processed/instagram_clean_v8.csv'
WHERE estado IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC
LIMIT 15;


-- ============================================================
-- Q3: Tasa de recompra
-- Objetivo: ¿qué % de clientes han comprado más de una vez?
-- ============================================================
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

-- ============================================================
-- Q4: Top 20 clientes con más envíos
-- Objetivo: identificar a los clientes más leales
-- ============================================================
SELECT
    usuario_ig,
    COUNT(*) AS envios,
    MIN(fecha)::DATE AS primera_compra,
    MAX(fecha)::DATE AS ultima_compra,
    DATE_DIFF('day', MIN(fecha), MAX(fecha)) AS dias_como_cliente
FROM 'data/processed/instagram_clean_v8.csv'
WHERE usuario_ig IS NOT NULL
GROUP BY 1
HAVING COUNT(*) > 1
ORDER BY 2 DESC
LIMIT 20;

-- ============================================================
-- Q5: Estacionalidad — envíos por mes del año (agregado 2 años)
-- Objetivo: detectar meses pico independientemente del año
-- ============================================================
SELECT
    EXTRACT(MONTH FROM fecha) AS mes,
    COUNT(*) AS envios
FROM 'data/processed/instagram_clean_v8.csv'
WHERE fecha_confiable = true
GROUP BY 1
ORDER BY 1;


-- ============================================================
-- Q6: Top 10 CPs por envíos
-- Objetivo: detectar zonas específicas con alta concentración
-- ============================================================
SELECT
    cp,
    COUNT(*) AS envios
FROM 'data/processed/instagram_clean_v8.csv'
WHERE cp IS NOT NULL
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10;


-- ============================================================
-- Q7: Crecimiento por año
-- Objetivo: ver el crecimiento anual y su %
-- ============================================================
SELECT
    EXTRACT(YEAR FROM fecha) AS año,
    COUNT(*) AS envios, 
    LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM fecha)) AS año_anterior,
    ROUND(
        100.0 * (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM fecha)))
        / LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM fecha)),
        1
    ) AS crecimiento_pct
FROM 'data/processed/instagram_clean_v8.csv'
WHERE fecha_confiable = true
GROUP BY 1
ORDER BY 1;

-- ============================================================
-- Q9: Tasa de recompra por año (validar impacto de la decisión)
-- ============================================================
SELECT
    EXTRACT(YEAR FROM fecha) AS año,
    COUNT(*) AS envios,
    COUNT(DISTINCT usuario_ig) AS clientes,
    ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT usuario_ig), 2) AS envios_por_cliente
FROM 'data/processed/instagram_clean_v8.csv'
WHERE fecha_confiable = true AND usuario_ig IS NOT NULL
GROUP BY 1
ORDER BY 1;