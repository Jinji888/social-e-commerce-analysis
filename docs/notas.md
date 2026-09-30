# Notas de estudio — Limpieza de datos

Documento de apoyo para entender cada paso del proceso de limpieza del proyecto
"Social Commerce → Ecommerce".

---

## Índice

1. Conceptos base
2. Script 01 — Carga inicial
3. Script 01b — Diagnóstico crudo
4. Script 01d — Nulos
5. Script 01e/f/g — Fechas
6. Script 01i/k — Limpieza de usuario
7. Script 01l — Paquetería
8. Script 01m/n — Direcciones
9. Glosario
10. Cómo estudiar esto

---

## Conceptos base

### ¿Qué es un DataFrame?
Es una tabla en memoria (como una hoja de Excel) con filas y columnas.
En pandas se llama `df`. Cada columna tiene un **tipo de dato**
(`str`, `int`, `datetime`, etc.).

### ¿Qué es la limpieza de datos?
Es el proceso de convertir datos crudos (sucios, inconsistentes, con errores)
en datos **utilizables** para análisis. Es el 70-80% del trabajo de un analista.

### Principio rector
**Los datos crudos no se tocan.** Todo el trabajo se hace en código, sobre
copias procesadas. Así siempre puedes volver al original.

### Flujo general

```
data/raw/*.csv  →  limpieza  →  data/processed/*.csv  →  análisis
     ↑                                                            ↓
  intacto                                                    resultados
```

---

## Script 01 — Carga inicial

**Archivo:** `notebooks/01_cleaning.py`

### ¿Qué hace?
Carga el CSV crudo y muestra su estructura básica.

### Código clave

```python
df = pd.read_csv("data/raw/instagram_orders.csv", encoding="utf-8")
```

- **`pd.read_csv(...)`**: lee el archivo y lo convierte en un DataFrame.
- **`encoding="utf-8"`**: especifica cómo interpretar los bytes. UTF-8 soporta
  tildes, ñ, emojis.

```python
print("Filas:", len(df))
```
- **`len(df)`**: número de filas.

```python
print(df.columns)
```
- **`df.columns`**: lista con los nombres de las columnas.

```python
print(df.head(3))
```
- **`df.head(n)`**: muestra las primeras `n` filas.

```python
print(df.dtypes)
```
- **`df.dtypes`**: tipo de dato de cada columna (`object`, `int64`,
  `datetime64`, etc.).

### Hallazgo
La primera columna se llamaba `'f'` en lugar de `'Fecha'` porque el CSV tenía
un BOM (marca invisible al inicio). Se arregla en la siguiente lectura con
`encoding="utf-8-sig"`.

---

## Script 01b — Diagnóstico crudo

**Archivo:** `notebooks/01b_diagnostico.py`

### ¿Qué hace?
Lee el CSV **sin encabezado** para ver qué hay realmente en cada celda,
incluyendo las primeras filas y las últimas.

### Código clave

```python
df_raw = pd.read_csv(..., header=None, nrows=8)
```
- **`header=None`**: no trata la primera fila como encabezado; la lee como dato.
- **`nrows=8`**: lee solo 8 filas (para no cargar todo).

```python
for i, row in df_raw.iterrows():
    for j, valor in enumerate(row):
        print(f"Col {j}: {str(valor)[:80]!r}")
```
- **`df.iterrows()`**: itera fila por fila.
- **`enumerate(row)`**: numera cada valor.
- **`[:80]`**: corta el texto a 80 caracteres.
- **`!r`** (en f-string): muestra el valor "crudo", con caracteres especiales
  visibles.

### ¿Por qué existe este script?
Porque **nunca debes limpiar sin antes entender el archivo**. Vimos cosas como:
- Filas de prueba mezcladas con pedidos reales.
- Columnas "basura" al final (`Unnamed: 5`, `Documento sin título`).
- Direcciones con saltos de línea.

### Hallazgo
La fila 1 era de prueba. Había 3 columnas basura. Los datos reales empiezan
en la fila 1 con formato consistente.

---

## Script 01d — Nulos

**Archivo:** `notebooks/01d_nulos.py`

### ¿Qué hace?
Detecta y clasifica los valores nulos (vacíos). Los separa en:
- Filas completamente vacías.
- Filas sin fecha pero con otros datos.
- Valores "N/A" escritos como texto.

### Código clave

```python
df = pd.read_csv(..., na_values=[""], keep_default_na=False)
```
- **`na_values=[""]`**: considera solo el string vacío como nulo.
- **`keep_default_na=False`**: desactiva la lista automática de pandas (que
  incluye `"N/A"`, `"null"`, `"NA"`, etc.).

**Por qué:** pandas por defecto convierte `"N/A"` en nulo. Pero en nuestro caso,
"N/A" era información real: los clientes lo usaban para decir "sin número
interior". Sin este ajuste, habríamos perdido 2 clientes reales.

### Detección de filas

```python
vacias = df.isna().all(axis=1)
```
- **`df.isna()`**: matriz booleana (True donde hay nulo).
- **`.all(axis=1)`**: por cada fila, True si **todos** los valores son nulos.

```python
df = df[~vacias].reset_index(drop=True)
```
- **`~vacias`**: invierte la máscara. Nos quedamos con las filas que NO son
  vacías.
- **`.reset_index(drop=True)`**: reenumera el índice desde 0 (porque al filtrar
  quedan huecos).

### Hallazgo
31 filas completamente vacías. 4 filas sin fecha. Se eliminaron 31 + 1
abandonada.

---

## Script 01e/f/g — Fechas

**Archivos:** `01e_fechas.py`, `01f_fechas_diag.py`, `01g_fecha_fix.py`

### ¿Qué hacen?
Convierten la columna `fecha` de texto a tipo `datetime` y corrigen errores.

### El problema
Las fechas venían como texto:

```
'24/5/2024 12:25:33'
'11/2/2025 23:32:33'
'3/9/1774 4:27:47'      ← error
'\\'                     ← basura
```

Pandas no las reconoce como fechas automáticamente y no puedes hacer análisis
temporal con ellas.

### Conversión

```python
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
```
- **`pd.to_datetime(...)`**: convierte texto a fecha.
- **`errors="coerce"`**: los valores que no puede convertir los pone como `NaT`
  (Not a Time, el "nulo" de las fechas) en lugar de fallar.

**Detalle importante:** en un script intentamos usar
`format="%d/%m/%Y %H:%M:%S"`. Eso funciona con el formato original, pero falla
si la fecha ya fue convertida a ISO (`2024-05-24`). Por eso el script final usa
`pd.to_datetime` sin formato explícito: pandas detecta automáticamente.

### Corrección manual

```python
mask_1774 = df["fecha"].dt.year == 1774
df.loc[mask_1774, "fecha"] = pd.Timestamp("2024-04-26")
```
- **`df["fecha"].dt.year`**: accede al año como número.
- **`mask_1774`**: máscara booleana de las filas que cumplen.
- **`df.loc[filtro, columna] = valor`**: asigna un valor solo a las celdas que
  cumplen el filtro.
- **`pd.Timestamp(...)`**: crea una fecha específica.

### Bandera de confiabilidad

```python
df["fecha_confiable"] = df["fecha"].notna()
```
- **`.notna()`**: True donde NO hay nulo.

Sirve para filtrar en análisis temporales: `WHERE fecha_confiable = true`.

### Hallazgo
5 fechas problemáticas: 1 con año 1774 (corregida a 2024-04-26 usando evidencia
del campo usuario) + 4 con basura (marcadas como no confiables).

---

## Script 01i/k — Limpieza de usuario

**Archivos:** `01i_usuarios_clean.py`, `01k_usuarios_refinados.py`

### ¿Qué hacen?
Extraen el handle de Instagram (nombre de usuario) a partir de un campo muy
sucio.

### El problema
Ejemplos reales:

```
'@morguepartyy'                      ← con @
'soflopez_02 / 55 2366 6718'        ← con teléfono
'Abbysanlo 442 4893517'              ← con teléfono pegado
'instagram, cabezademdusa'           ← con prefijo
'26/abril/24 hawaii.pv / 3222375409' ← con fecha + teléfono
'Milokix☆'                           ← con símbolo
```

### Estrategia general
1. **Normalizar unicode**.
2. **Quitar caracteres invisibles**.
3. **Dividir por separadores**.
4. **Filtrar tokens inválidos** (teléfonos, stopwords, muy cortos).
5. **Elegir el mejor candidato**.

### Paso 1: Normalizar unicode

```python
u = unicodedata.normalize("NFKC", u)
```
- Convierte caracteres unicode equivalentes a su forma canónica.
- Ejemplo: `１２３` (ancho completo) → `123` (normal).

### Paso 2: Quitar caracteres invisibles

```python
u = re.sub(r"[\u200b-\u200f\u202a-\u202e\xa0]", " ", u)
```
- **`\u200b` a `\u200f`**: espacios de ancho cero (invisibles).
- **`\u202a` a `\u202e`**: marcadores de dirección (se cuelan al copiar de
  WhatsApp).
- **`\xa0`**: espacio duro (non-breaking space).
- **`re.sub(patrón, reemplazo, texto)`**: reemplaza todas las coincidencias.

### Paso 3: Dividir por separadores

```python
tokens = re.split(r"[/,;:()\-\s]+", u)
```
- **`re.split`**: divide el string en partes usando el patrón.
- **`[/,;:()\-\s]+`**: cualquier combinación de `/ , ; : ( ) -` o espacios.
- Resultado: `"@user 1234 / extra"` → `["@user", "1234", "extra"]`.

### Paso 4: Filtrar tokens

**Descartar teléfonos:**
```python
if re.fullmatch(r"\+?\d+", tok):
    continue
```
- **`fullmatch`**: todo el string debe coincidir (no solo una parte).
- **`\+?`**: un `+` opcional (teléfonos internacionales).
- **`\d+`**: uno o más dígitos.

**Descartar stopwords:**
```python
if tok in STOPWORDS:
    continue
```
Lista de palabras comunes que no son handles: `user`, `num`, `instagram`, `mi`,
etc.

**Descartar si no tiene letras:**
```python
if not re.search(r"[a-z]", tok):
    continue
```

**Limpiar caracteres no válidos:**
```python
tok = re.sub(r"[^a-z0-9._\u00c0-\u024f]", "", tok)
```
- **`[^...]`**: "cualquier caracter que NO esté en este conjunto".
- Elimina todo lo que no sea letra, número, punto, guion bajo o letra latina
  extendida.
- Ejemplo: `"milokix☆"` → `"milokix"`.

### Paso 5: Elegir el mejor

```python
return max(candidatos, key=len)[:30]
```
- **`max(..., key=len)`**: elige el elemento más largo.
- **`[:30]`**: trunca a 30 caracteres (límite oficial de Instagram).

**Por qué el más largo:** en `"user: vkyaaaa num: 9612909557"`, después de
filtrar teléfonos y stopwords, solo queda `"vkyaaaa"` (que es el handle). El
más largo suele ser el correcto.

### Hallazgo
De 1309 filas: 1286 con handle extraído, 23 sin handle (mayoría solo teléfono).
880 usuarios únicos.

### Lección
El campo usuario original se guardó en `usuario_ig_original` antes de
sobrescribir. **Regla:** nunca sobrescribas el original sin respaldarlo.

---

## Script 01l — Paquetería

**Archivo:** `notebooks/01l_paqueteria.py`

### ¿Qué hace?
Normaliza 27 variantes de paquetería a 2 categorías.

### El problema

```
'CORREOS DE MÉXICO / POSTAL MEXICANA'
'CORREOS DE MÉXICO (70 PESOS)'
'CORREOS DE MÉXICO / POSTAL MEXICANA (80 pesos)'
'Correos de Mexico'
'CORREOS VIEJA RATA'                    ← meme
'ESTAFETA (COTIZADO Y PAGADO)'
'ESTAFETA (COTIZADO)'
'ESTAFETA'
```

Todos son lo mismo, pero escritos distinto.

### Código clave

```python
df["paqueteria_original"] = df["paqueteria"]   # respaldo
df["paqueteria"] = df["paqueteria"].apply(normalizar_paqueteria)
```
- **`df["columna"].apply(función)`**: aplica una función a cada valor de la
  columna.
- Primero guardamos el original, luego sobrescribimos.

```python
def normalizar_paqueteria(p):
    if pd.isna(p):
        return "Desconocida"
    p_upper = str(p).upper()
    if "CORREOS" in p_upper or "POSTAL MEXICANA" in p_upper:
        return "Correos de México"
    if "ESTAFETA" in p_upper:
        return "Estafeta"
    return "Desconocida"
```
- **`.upper()`**: convierte a mayúsculas para comparar sin importar el case.
- **`in`**: busca si la palabra está contenida en cualquier parte del texto.

### Caso especial detectado

```python
mask_especial = df["paqueteria_original"].str.contains("NO ES ESTAFETA", na=False)
df.loc[mask_especial, "paqueteria_nota"] = "Cliente eligió Estafeta, se envió por Correos"
```
Algunos clientes eligieron Estafeta pero se envió por Correos. Se clasifican por
lo que eligió el cliente (Estafeta) pero se documenta en una nota.

### Hallazgo
- Correos de México: 1149 (87.78%)
- Estafeta: 157 (11.99%)
- Desconocida: 3 (0.23%)

---

## Script 01m/n — Direcciones

**Archivos:** `01m_direcciones_diag.py`, `01n_direcciones.py`

### ¿Qué hacen?
Diagnostican y extraen CP, estado y teléfono del campo `datos_envio`.

### El problema
Direcciones en texto libre con 9-10 líneas:

```
Sofía Victoria López López 
Cerrada de Juárez 
21
San Mateo Tecoloapan
52920
México 
Atizapán de Zaragoza
Estado de México
55 2366 6718
```

Pero también hay casos de **una sola línea**:

```
Alexia Ivana Rodríguez Durán Calle 27 #162 A x 22 y 24 col. Fco. I. Madero CP 97240 Mérida, Yucatán...
```

### Decisión
Parsear solo 3 cosas: **CP, estado, teléfono**. Ciudad, calle y colonia son
demasiado variables.

### Extractor de CP

```python
# Intento 1: con contexto explícito
r"(?:c\.?\s*p\.?|c[oó]digo\s+postal)[:\s]*(\d{5})(?!\d)"

# Intento 2: cualquier 5 dígitos aislados
r"(?<!\d)(\d{5})(?!\d)"
```

**Desglose del segundo:**
- **`(?<!\d)`**: lookbehind negativo. "No debe haber dígito antes".
- **`(\d{5})`**: captura exactamente 5 dígitos.
- **`(?!\d)`**: lookahead negativo. "No debe haber dígito después".

Sin estos lookarounds, un teléfono de 10 dígitos como `5523666718` haría match
con `55236` y `66718`.

### Extractor de estado

```python
ESTADOS = {"cdmx": "Ciudad de México", "edomex": "Estado de México", ...}
```

```python
t = re.sub(r"[^\w\s]", " ", t)   # quitar puntuación
for clave in sorted(ESTADOS.keys(), key=len, reverse=True):
    if re.search(r"\b" + re.escape(clave) + r"\b", t):
        return ESTADOS[clave]
```

- **`\b`**: límite de palabra. Evita que "puebla" matchee en "pueblito".
- **`re.escape(...)`**: escapa caracteres especiales en la clave.
- **`sorted(..., key=len, reverse=True)`**: ordena de más largas a más cortas.
  Evalúa "baja california sur" antes que "baja california".

### Extractor de teléfono

```python
patron = r"(?<!\d)(?:\+?52[\s\-]?)?(\d{2,3})[\s\-]?(\d{3,4})[\s\-]?(\d{4})(?!\d)"
```

- **`(?:\+?52[\s\-]?)?`**: prefijo `+52` opcional. `(?:...)` = grupo no
  capturador.
- **`(\d{2,3})`**: 2-3 dígitos (lada).
- **`(\d{3,4})`**: 3-4 dígitos.
- **`(\d{4})`**: últimos 4.
- Acepta `55 2366 6718`, `5523666718`, `+52 55 2366 6718`.

**Corrección posterior:**

```python
if len(num) == 12 and num.startswith("52"):
    num = num[2:]
if len(num) == 13 and num.startswith("521"):
    num = num[3:]
if len(num) == 10:
    return num
```

Quita el prefijo `52` de México para quedarse solo con 10 dígitos.

### Hallazgo
- CP: 96.3%
- Estado: 95.3%
- Teléfono: 92.0%

Muy por encima del 70-80% esperado. Excelente calidad.

---

## Glosario

| Término | Significado |
|---|---|
| **DataFrame** | Tabla en memoria de pandas |
| **Serie** | Una columna de un DataFrame |
| **NaN / NaT** | Valor nulo. NaT es específico de fechas |
| **Máscara booleana** | Serie de True/False para filtrar filas |
| **`axis=0` / `axis=1`** | 0 = columnas, 1 = filas |
| **Regex** | Expresión regular para buscar patrones en texto |
| **Lookahead / Lookbehind** | Verificar algo antes/después sin capturarlo |
| **Lambda** | Función anónima de una línea |
| **`apply`** | Aplicar una función a cada valor de una serie/columna |
| **`loc` / `iloc`** | Acceso por nombre / por posición |
| **UTF-8** | Codificación de texto que soporta todos los caracteres |
| **BOM** | Marca invisible al inicio del archivo |
| **CTE (`WITH`)** | Subconsulta con nombre en SQL |
| **Window function** | Cálculo que depende de otras filas (`LAG`, `SUM OVER`) |

---

## Cómo estudiar esto

1. **Lee este documento completo una vez.**
2. **Abre cada script** y busca las líneas mencionadas aquí. Verás el código
   real.
3. **Modifícalo y observa qué cambia.** Por ejemplo, quita una regla del parser
   de usuario y mira qué se rompe.
4. **Escribe tus propias notas** en los comentarios del código.
5. **Practica explicarlo en voz alta** como si fuera para la entrevista.

**Regla de oro:** si puedes explicar qué hace una función y por qué existe, ya
la entiendes. No necesitas memorizar la sintaxis.