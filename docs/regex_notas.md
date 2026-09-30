---

## Glosario de Regex

Esta sección explica los símbolos de expresiones regulares (regex) que se usaron
en el proyecto. Es una referencia práctica.

---

### ¿Qué es una regex?

Una **regex** (expresión regular) es un patrón de texto que describe qué buscar
dentro de un string. Se usa con funciones como `re.search`, `re.findall`,
`re.sub`, `re.split`, `re.fullmatch`.

**Ejemplo mental:** la regex `\d{3}` significa "tres dígitos seguidos". Con eso
puedes encontrar `123`, `456`, `789`, etc. dentro de cualquier texto.

---

### 1. Clases de caracteres

Definen **qué tipo de carácter** buscar.

| Símbolo | Significa | Ejemplo | Matchea |
|---|---|---|---|
| `\d` | Un dígito (0-9) | `\d` | `5`, `7` |
| `\D` | Cualquier cosa **excepto** un dígito | `\D` | `a`, `-`, ` ` |
| `\w` | Letra, número o guion bajo | `\w` | `a`, `7`, `_` |
| `\W` | Cualquier cosa **excepto** letra/número/_ | `\W` | `@`, ` `, `.` |
| `\s` | Espacio, tab, salto de línea | `\s` | ` `, `\t`, `\n` |
| `\S` | Cualquier cosa **excepto** espacio | `\S` | `a`, `7`, `@` |
| `.` | Cualquier carácter (excepto salto de línea) | `a.c` | `abc`, `a7c` |

**En el proyecto:**
- `\d` en el extractor de CP y teléfono.
- `\s` en el separador de tokens de usuarios.

---

### 2. Conjuntos personalizados

Cuando quieres buscar "cualquier carácter de este grupo".

| Símbolo | Significa | Ejemplo | Matchea |
|---|---|---|---|
| `[abc]` | Cualquiera de `a`, `b` o `c` | `[abc]` | `a`, `b`, `c` |
| `[a-z]` | Cualquier letra minúscula | `[a-z]` | `a`, `m`, `z` |
| `[A-Z]` | Cualquier letra mayúscula | `[A-Z]` | `A`, `M`, `Z` |
| `[0-9]` | Cualquier dígito (igual que `\d`) | `[0-9]` | `0` a `9` |
| `[a-zA-Z0-9]` | Letras (mayús/minús) y dígitos | | `a`, `M`, `7` |
| `[^abc]` | Cualquier cosa **excepto** `a`, `b`, `c` | `[^0-9]` | `a`, `@`, `-` |
| `[a-z0-9._]` | Letras, dígitos, punto y guion bajo | | `a`, `7`, `.`, `_` |

**En el proyecto:**
- `[a-z0-9._\u00c0-\u024f]` → caracteres válidos para un handle de Instagram.
  Acepta letras, números, punto, guion bajo y letras latinas con acento.
- `[^a-z0-9._\u00c0-\u024f]` → todo lo demás (para eliminarlo).

---

### 3. Cuantificadores

Dicen **cuántas veces** debe aparecer lo anterior.

| Símbolo | Significa | Ejemplo | Matchea |
|---|---|---|---|
| `?` | Cero o una vez (opcional) | `colou?r` | `color`, `colour` |
| `*` | Cero o más veces | `lo*l` | `ll`, `lol`, `lool` |
| `+` | Una o más veces | `lo+l` | `lol`, `lool` (no `ll`) |
| `{3}` | Exactamente 3 veces | `\d{3}` | `123`, `456` |
| `{2,4}` | Entre 2 y 4 veces | `\d{2,4}` | `12`, `123`, `1234` |
| `{7,}` | 7 o más veces | `\d{7,}` | `1234567`, `12345678` |

**En el proyecto:**
- `\d{5}` → exactamente 5 dígitos (CP).
- `\d{7,}` → 7 o más dígitos (para detectar teléfonos).
- `\d{2,3}` → 2 o 3 dígitos (lada del teléfono).
- `[/,;:()\-\s]+` → uno o más separadores seguidos.

---

### 4. Anclas y límites

Dicen **dónde** debe estar el match.

| Símbolo | Significa |
|---|---|
| `^` | Inicio del string |
| `$` | Fin del string |
| `\b` | Límite de palabra (entre letra y no-letra) |

**En el proyecto:**
- `\bpuebla\b` → matchea "puebla" como palabra completa, no dentro de "pueblito".
- Sin `\b`, buscar "df" dentro de "edificio" daría falso positivo.

---

### 5. Grupos

Agrupan partes del patrón.

| Símbolo | Significa |
|---|---|
| `(...)` | Grupo **capturador** (puedes extraer su contenido) |
| `(?:...)` | Grupo **no capturador** (agrupa pero no extrae) |
| `|` | Alternancia (OR) |

**Ejemplo capturador:**
```python
re.search(r"(\d{5})", "CP 12345")
```
- `match.group(0)` → `"12345"` (todo el match)
- `match.group(1)` → `"12345"` (lo que capturó el primer grupo)

**Ejemplo no capturador:**
```python
r"(?:\+?52[\s\-]?)?(\d{10})"
```
- `(?:...)` agrupa el prefijo `+52` pero no lo captura.
- El único grupo capturador es `(\d{10})`.

**En el proyecto:**
- `(\d{5})` en CP → captura los 5 dígitos.
- `(?:\+?52[\s\-]?)?` en teléfono → agrupa el prefijo opcional.

---

### 6. Lookarounds (mirar sin capturar)

Verifican algo **antes o después** del match sin incluirlo.

| Símbolo | Significa |
|---|---|
| `(?=...)` | Debe venir ... **después** (positivo) |
| `(?!...)` | **No** debe venir ... después (negativo) |
| `(?<=...)` | Debe haber ... **antes** (positivo) |
| `(?<!...)` | **No** debe haber ... antes (negativo) |

**En el proyecto — CP:**
```python
r"(?<!\d)(\d{5})(?!\d)"
```
- `(?<!\d)` → "antes de los 5 dígitos **no** debe haber otro dígito".
- `(\d{5})` → los 5 dígitos a capturar.
- `(?!\d)` → "después de los 5 dígitos **no** debe haber otro dígito".

**Ejemplo:** en el string `"5523666718"` (un teléfono):
- Sin lookarounds: matchearía `55236` (falso positivo).
- Con lookarounds: no matchea porque hay más dígitos alrededor.

**En el proyecto — teléfono:**
```python
r"(?<!\d)(?:\+?52[\s\-]?)?(\d{2,3})[\s\-]?(\d{3,4})[\s\-]?(\d{4})(?!\d)"
```
- `(?<!\d)` al inicio → no debe haber dígito antes.
- `(?!\d)` al final → no debe haber dígito después.

---

### 7. Escapes

Cuando quieres buscar un carácter especial **literalmente**, hay que escaparlo
con `\`.

| Símbolo | Significa |
|---|---|
| `\.` | Un punto literal |
| `\+` | Un `+` literal |
| `\?` | Un `?` literal |
| `\-` | Un guion literal |
| `\(` | Un paréntesis literal |
| `\[` | Un corchete literal |
| `\\` | Una barra invertida literal |

**En el proyecto:**
- `c\.?\s*p\.?` → matchea "CP" o "C.P." o "C P". Los `\.` son puntos literales.
- `[\s\-]?` → espacio o guion, opcional. El `\-` es guion literal (dentro de
  corchetes siempre conviene escaparlo).

**¿Por qué `re.escape(clave)`?**
```python
r"\b" + re.escape(clave) + r"\b"
```
Si la clave fuera `"s.l.p."`, sus puntos serían interpretados como "cualquier
carácter". `re.escape` los convierte en `s\.l\.p\.` (puntos literales). Es una
manera segura de insertar texto del usuario dentro de una regex.

---

### 8. Unicode

| Símbolo | Significa |
|---|---|
| `\uXXXX` | Carácter unicode con código hexadecimal XXXX |
| `[\u00c0-\u024f]` | Rango de letras latinas extendidas (á, é, ñ, ü, etc.) |

**En el proyecto:**
- `\u200b` a `\u200f` → espacios de ancho cero (invisibles).
- `\u202a` a `\u202e` → marcadores de dirección (se cuelan al copiar de
  WhatsApp).
- `\xa0` → espacio duro (non-breaking space).
- `\u00c0-\u024f` → letras latinas con acento.

---

### 9. Funciones de regex en Python

| Función | Qué hace |
|---|---|
| `re.search(p, t)` | Busca `p` en `t`. Devuelve el primer match o `None` |
| `re.findall(p, t)` | Devuelve una lista con **todos** los matches |
| `re.sub(p, r, t)` | Reemplaza todos los matches de `p` con `r` |
| `re.split(p, t)` | Divide `t` usando `p` como separador |
| `re.fullmatch(p, t)` | True solo si **todo** `t` matchea `p` |
| `re.match(p, t)` | Match solo al **inicio** de `t` |

**En el proyecto:**
- `re.sub(r"[\u200b-\u200f...]", " ", u)` → reemplaza caracteres invisibles.
- `re.split(r"[/,;:()\-\s]+", u)` → divide por separadores.
- `re.fullmatch(r"\+?\d+", tok)` → True si el token es solo dígitos.
- `re.search(r"\b" + re.escape(clave) + r"\b", t)` → busca el estado.

---

### 10. Los patrones completos del proyecto

**Extractor de CP — intento con contexto:**
```python
r"(?:c\.?\s*p\.?|c[oó]digo\s+postal)[:\s]*(\d{5})(?!\d)"
```
Traducción: "busca `CP`, `C.P.`, `código postal`, seguido de `:` o espacios,
luego captura exactamente 5 dígitos que no estén pegados a más dígitos".

**Extractor de CP — fallback:**
```python
r"(?<!\d)(\d{5})(?!\d)"
```
Traducción: "5 dígitos aislados".

**Extractor de estado:**
```python
r"\b" + re.escape(clave) + r"\b"
```
Traducción: "la palabra clave como palabra completa".

**Extractor de teléfono:**
```python
r"(?<!\d)(?:\+?52[\s\-]?)?(\d{2,3})[\s\-]?(\d{3,4})[\s\-]?(\d{4})(?!\d)"
```
Traducción: "opcionalmente `+52`, luego 2-3 dígitos, separador opcional, 3-4
dígitos, separador opcional, 4 dígitos; nada de dígitos alrededor".

**Detectar PRUEBA:**
```python
fila.astype(str).str.contains("PRUEBA", case=False, na=False)
```
Traducción: "el texto contiene 'PRUEBA' (sin importar mayúsculas), ignorando
nulos".

---

### 11. Cómo construir una regex tú mismo

**Método paso a paso:**

1. **Escribe 5-10 ejemplos** de strings que quieres matchear.
2. **Escribe 5-10 ejemplos** de strings que NO quieres matchear.
3. **Empieza simple** con la regex más básica. Prueba.
4. **Añade restricciones** poco a poco hasta que excluya los falsos positivos.
5. **Prueba en un sitio como regex101.com** — ahí puedes ver paso a paso qué
   matchea.
6. **Cuando funcione**, intégrala en Python.

**Ejemplo real de tu proyecto:**

Quieres extraer CP (5 dígitos). Ejemplos válidos:
- `"CP 97240"` → 97240
- `"C.P. 15960"` → 15960
- `"52920"` → 52920

Ejemplos inválidos:
- `"5523666718"` (teléfono)
- `"1234567"` (7 dígitos)

**Paso 1** — regex básica: `\d{5}`.  
Problema: matchea el `55236` del teléfono. Falso positivo.

**Paso 2** — añadir lookarounds: `(?<!\d)(\d{5})(?!\d)`.  
Ya no matchea el teléfono. ✅

**Paso 3** — priorizar el contexto "CP": primero buscar
`(?:c\.?\s*p\.?)[:\s]*(\d{5})`, luego el fallback. Así los CPs con etiqueta
tienen prioridad.

**Conclusión:** construir regex no es memorizar, es iterar con ejemplos.

---

### 12. Tabla de referencia rápida

| Necesito buscar... | Regex |
|---|---|
| Un dígito | `\d` |
| Exactamente 5 dígitos | `\d{5}` |
| 5 dígitos aislados | `(?<!\d)\d{5}(?!\d)` |
| Un espacio o guion | `[\s\-]` |
| Una palabra completa | `\bpalabra\b` |
| Letras, números, punto, guion bajo | `[a-z0-9._]` |
| Cualquier cosa menos letras | `[^a-z]` |
| Inicio del string | `^` |
| Fin del string | `$` |
| Un punto literal | `\.` |
| Uno o más de algo | `+` |
| Cero o más de algo | `*` |
| Algo opcional | `...?` |