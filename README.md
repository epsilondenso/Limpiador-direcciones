# Limpieza de direcciones

El proceso se basa en la tokenización de las direcciones y en una serie de reglas configurables para reemplazar abreviaturas y eliminar ruido textual.

## Objetivo

Las direcciones suelen presentar múltiples variaciones en su escritura, por ejemplo:

* Abreviaturas: `AV.`, `AVDA`, `CALLE`, `COL.`, `MZ.`, etc.
* Puntuación innecesaria.
* Guiones utilizados como separadores.
* Información administrativa o legal que no forma parte de la ubicación.
* Diferentes formas de expresar una misma estructura.

El objetivo de este proyecto es transformar estas direcciones en una representación más consistente que facilite su posterior procesamiento, comparación o geocodificación.

---

## Formato de entrada

El CSV de entrada debe contener, al menos, las siguientes columnas (puede tener más; se conservan):

| Columna              | Contenido                         |
| -------------------- | --------------------------------- |
| `DIRECCIÓN GARANTÍA` | Dirección cruda a limpiar.        |
| `ESTADO`             | Estado (nombre o abreviatura).    |
| `MUNICIPIO`          | Municipio.                        |
| `COLONIA`            | Colonia.                          |
| `CP`                 | Código postal.                    |

La salida es el mismo CSV, preprocesado, con dos columnas adicionales:

* `DIRECCIÓN LIMPIA`: la dirección limpia.
* `AVISOS`: señala direcciones que conviene revisar a mano, sin modificarlas: `Dirección vacía`, `Sin número` (ni dígitos ni `S/N`) y `Demasiado larga (posible texto legal)` (más de `MAX_TOKENS` = 25 tokens, en `src/pipeline.py`). Si hay varios, se separan con `; `.

Las listas de columnas están definidas en `src/pipeline.py` (`REQUIRED_COLUMNS`, `OUTPUT_COLUMN`).

---

## Pipeline

A nivel de archivo, el proceso es:

```text
CSV crudo
   │
   ▼
Validación de columnas
   │
   ▼
Preprocesamiento: se descartan filas sin dirección y duplicados,
se rellenan los vacíos con "Sin info" y se expanden las abreviaturas de estados
   │
   ▼
Limpieza de cada dirección (ver abajo)
   │
   ▼
Unión de tokens → columna DIRECCIÓN LIMPIA
```

Para cada dirección, además de los patrones genéricos, se eliminan como redundantes el estado, el municipio, la colonia y el CP de su propio registro, ya que esa información existe en sus columnas (ver [Eliminación de información redundante](#6-eliminación-de-información-redundante)).

La limpieza de una dirección individual sigue las siguientes etapas:

```text
Dirección original
       │
       ▼
   Tokenización
       │
       ▼
Reemplazo de abreviaturas
       │
       ▼
Eliminación de caracteres
       │
       ▼
Limpieza de puntuación
       │
       ▼
 Eliminación de ruido
       │
       ▼
Eliminación de información redundante
       │
       ▼
Eliminación de duplicados
       │
       ▼
Unificación de mayúsculas
       │
       ▼
Dirección limpia
```

La función principal del pipeline es:

```python
from src.cleaning_pipe import clean

tokens = clean(direccion)
```

### 1. Tokenización

La dirección se divide en tokens correspondientes a palabras, números y determinados caracteres.

Por ejemplo:

```text
"AV. INSURGENTES SUR #123-B"
```

se transforma aproximadamente en:

```python
["Av.", "INSURGENTES", "SUR", "No.", "123", "B"]
```

La tokenización se realiza mediante una expresión regular, con dos reglas adicionales:

* **Unidades con barra**: `S/N`, `N/A`, `Y/O` (letra/letra) y fracciones como `1/2` se conservan como un solo token, con o sin espacios (`S / N` → `S/N`). `S/NO` también se reconoce y el diccionario lo convierte en `S/N`.
* **Abreviaturas pegadas**: se separan en el punto cuando antes hay al menos dos letras: `NO.INT.` → `NO.` `INT.`, `FRACC.A` → `FRACC.` `A`. Las siglas como `B.C.S.` no se separan.

### 2. Reemplazo de abreviaturas

Las abreviaturas se reemplazan utilizando el diccionario localizado en:

```text
datos/dictionaries/dict_abrev.csv
```

El diccionario contiene pares de la forma:

```text
abrev, significado
```

Esto permite centralizar las abreviaturas y modificar el comportamiento del pipeline sin necesidad de modificar el código.

Las abreviaturas de una sola letra (`M`, `L`, `N`, con o sin punto; `ABREVS_AMBIGUAS` en `config/patrones.py`) también pueden ser iniciales (`M. LOPEZ`) o letras de una sección (`SECCION A-L`). Por eso solo se reemplazan si les sigue, ignorando guiones, un número o un numeral romano: `M I` → `Mz. I`, `L-29` → `Lt. 29`.

### 3. Eliminación de caracteres

El pipeline permite eliminar determinados caracteres que aparecen como separadores y que no aportan información a la dirección. Se hace antes de buscar patrones, para que un guion no impida una coincidencia.

Por defecto se elimina el guion:

```python
tokens = clean(direccion)                        # elimina "-"
tokens = clean(direccion, elim_caracters=False)  # lo conserva
```

### 4. Limpieza de puntuación

Se eliminan los tokens formados solo por puntos (`.`, `.....`) y las barras `/` sueltas al inicio o al final. Las barras entre palabras (`FRACC. / COL.`) se conservan.

### 5. Eliminación de ruido

Después de reemplazar las abreviaturas y quitar los separadores, se eliminan expresiones que aportan poca o ninguna información para identificar la ubicación.

Las reglas se encuentran en:

```text
config/patrones.py
```

Los patrones se representan mediante la clase `Pattern`:

```python
@dataclass(frozen=True)
class Pattern:
    nombre: str
    patron: list[set[str]]
    action: str = "delete"
```

Esto permite representar patrones con diferentes variantes. Por ejemplo:

```python
Pattern(
    nombre="Ubicado en",
    patron=[
        {"UBICADA", "UBICADO"},
        {"EN"}
    ]
)
```

El sistema compara los patrones después de normalizar los tokens para evitar que diferencias como mayúsculas, acentos o puntos afecten la comparación.

### 6. Eliminación de información redundante

El estado, municipio, colonia y CP de cada registro ya están en sus columnas, así que se eliminan de su dirección (`redundant_patterns` y `eliminar_redundantes` en `src/elim_noise.py`):

* **El valor de la columna recibe la misma limpieza que la dirección** (abreviaturas, guiones, puntuación y ruido), para que ambos sean comparables: la colonia `FRACC. TACOTENO` se busca como `TACOTENO`.
* **Se eliminan todas las apariciones**, no solo la primera: `REAL DE MINAS HERMOSILLO 83285 HERMOSILLO SONORA` → `REAL DE MINAS 83285`.
* **El prefijo se elimina junto con el valor** (`PREFIJOS_CONTEXTO` en `config/patrones.py`): `C.P. 77524`, `CD. JUAREZ`, `COL. CENTRO`.
* **Se conservan las apariciones que parecen nombre de calle**:
  * las precedidas por un tipo de vía (`TIPOS_VIA` en `config/patrones.py`): `Av. JUAREZ 120` con municipio Juárez se conserva;
  * si el valor aparece más de una vez, la que está al inicio de la dirección: `VILLA FONTANA SUR … VILLA FONTANA RESIDENCIAL` → `VILLA FONTANA SUR … RESIDENCIAL`.
* **Se ignoran los valores sin contenido**, es decir, sin ningún token de 3 o más caracteres (`0`, `N/A`), y los `Sin info`.
* **Si el valor ocupa toda la dirección** (la columna contiene la dirección por error de captura), no se elimina.

### 7. Eliminación de duplicados

Las palabras clave son los significados del diccionario de abreviaturas (`Calle`, `Av.`, `No.`, `Mz.`, `Lt.`, `Int.`, `Ext.`, …). Los duplicados se eliminan sin perder información, en este orden:

1. **Segmentos repetidos**: se elimina un segmento de 3 o más tokens idéntico a uno anterior, como `Av. TOLUCA S/N 0001 0001 Av. TOLUCA S/N` → `Av. TOLUCA S/N 0001 0001`. Solo se aplica si el segmento contiene un número (o `S/N`) y al menos dos tokens que no son palabras clave ni stopwords (`STOPWORDS` en `config/patrones.py`). Así no se eliminan coincidencias parciales de nombres, como `B DE LA` en `Calle CERRADA B DE LA Calle CAFETOS`.
2. **Repeticiones consecutivas** de una palabra clave o de una palabra de 3 o más letras: `Calle Calle 16` → `Calle 16`, `CHAMAPA CHAMAPA` → `CHAMAPA`.
3. **Pares palabra clave-valor repetidos**: `Mz. 8 Lt. 11 … Mz. 8` → `Mz. 8 Lt. 11 …`. El valor es el primer token que no es palabra clave, así que `No. Ext. 4126 No. Int. A` se conserva.

Las repeticiones con valores distintos (`Mz. XLI Mz. 41`, `Lt. 29 y parte del Lt. 30`) se conservan, porque contienen información distinta. Las palabras clave cuyo valor es un nombre de varias palabras (`KEYWORDS_NOMBRE` en `config/patrones.py`: `Calle`, `Av.`, `Colonia`, `Municipio`) no pasan por el punto 3; si no, `ENTRE Av. LAGUNA EL MANGAL` perdería parte del nombre.

Se puede desactivar con `clean(direccion, elim_duplicados=False)`.

### 8. Unificación de mayúsculas

Todo se pasa a mayúsculas, conservando los acentos, salvo las palabras clave del diccionario, que mantienen su forma (`Calle`, `Mz.`, `No.`): `Privada San José No. 44` → `PRIVADA SAN JOSÉ No. 44`.

Se puede desactivar con `clean(direccion, mayusculas=False)`.

## Estructura del proyecto

```text
LIMPIEZA_DIRECCIONES/
│
├── config/
│   ├── abrev_estados.py
│   ├── paths.py
│   └── patrones.py
│
├── datos/
│   ├── dictionaries/
│   │   └── dict_abrev.csv
│   │
│   ├── direcciones_raw/
│   │   └── universo_direcciones.csv
│   │
│   └── direcciones_clean/
│       └── universo_direcciones_clean.csv
│
├── notebooks/
│   ├── set_paths.py
│   └── test.ipynb
│
├── src/
│   ├── cleaning_pipe.py
│   ├── clean_adresses_file.py
│   ├── elim_duplicados.py
│   ├── elim_noise.py
│   ├── formato.py
│   ├── pipeline.py
│   ├── replace_abrev.py
│   └── __init__.py
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

### `src/`

Contiene la lógica principal del proyecto.

* **`replace_abrev.py`**
  Tokenización de direcciones y reemplazo de abreviaturas.

* **`elim_noise.py`**
  Normalización de tokens, búsqueda de patrones y eliminación de expresiones consideradas ruido.

* **`elim_duplicados.py`**
  Eliminación de segmentos y palabras clave duplicados.

* **`formato.py`**
  Limpieza de puntuación y unificación de mayúsculas.

* **`cleaning_pipe.py`**
  Integra las diferentes etapas en un único pipeline para **una** dirección (`clean`).

* **`pipeline.py`**
  Procesamiento de un `DataFrame` completo, sin lectura ni escritura de archivos: validación de columnas (`validate_columns`), preprocesamiento (`preprocess`) y limpieza (`clean_addresses_df`). Es el punto de entrada pensado para la app.

* **`clean_adresses_file.py`**
  Envoltorio de `pipeline.py` que lee un CSV de disco y guarda los resultados.

### `config/`

Contiene configuraciones y reglas utilizadas por el pipeline.

* **`paths.py`**: define las rutas principales del proyecto.
* **`abrev_estados.py`**: mapa de abreviaturas de estados a su nombre completo (`ESTADOS_MAP`).
* **`patrones.py`**: contiene los patrones utilizados para identificar y eliminar ruido, la carga del diccionario de abreviaturas y las listas `KEYWORDS_NOMBRE`, `ABREVS_AMBIGUAS` y `STOPWORDS`.

### `datos/`

Contiene los datos de entrada, diccionarios auxiliares y resultados del procesamiento.

* `direcciones_raw/`: direcciones originales.
* `direcciones_clean/`: direcciones procesadas.
* `dictionaries/`: diccionarios utilizados durante la normalización.

### `notebooks/`

Contiene notebooks utilizados para pruebas y exploración durante el desarrollo.

---

## Instalación

Se requiere Python y las dependencias especificadas en `requirements.txt`.

Instalar las dependencias mediante:

```bash
pip install -r requirements.txt
```

Actualmente el proyecto utiliza:

```text
pandas==2.3.1
streamlit==1.60.0
```

---

## App

La forma más sencilla de usar el proyecto es la app de Streamlit. Desde la raíz del proyecto:

```bash
streamlit run app.py
```

La app permite subir un CSV con las columnas requeridas (ver [Formato de entrada](#formato-de-entrada)), limpiarlo con una barra de progreso, ver una vista previa y descargar el CSV con la columna `DIRECCIÓN LIMPIA`.

* Acepta CSV en UTF-8 o en cp1252 (el formato que suele generar Excel en Windows).
* Todas las columnas se leen como texto.
* El CSV descargado está en UTF-8 con BOM, para que Excel muestre bien los acentos.

---

## Uso

El pipeline puede utilizarse directamente sobre una dirección:

```python
from src.cleaning_pipe import clean

direccion = "AV. INSURGENTES SUR #123-B"

tokens = clean(direccion)

print(tokens)
```

La función devuelve una lista de tokens, lo que permite realizar transformaciones adicionales antes de reconstruir la dirección.

### Procesamiento de un `DataFrame`

Para integrar el pipeline en otra aplicación (por ejemplo, Streamlit) se usa `clean_addresses_df`, que recibe y devuelve un `DataFrame` sin tocar el disco:

```python
import pandas as pd
from src.pipeline import clean_addresses_df

raw = pd.read_csv(archivo, dtype=str)   # ruta o archivo en memoria
cleaned = clean_addresses_df(raw)       # lanza ValueError si faltan columnas
```

Se puede pasar `progress`, una función que recibe la fracción procesada (entre 0 y 1), para mostrar el avance.

Se recomienda leer con `dtype=str` para que columnas como `CP` no se interpreten como números (p. ej. `32551.0`).

Las rutas de `config/` se resuelven a partir de la ubicación del propio paquete, por lo que el pipeline funciona sin importar el directorio de trabajo, siempre que la raíz del proyecto esté en el `PYTHONPATH`.

### Procesamiento de un archivo

El proyecto incluye un script para procesar el universo de direcciones localizado en:

```text
datos/direcciones_raw/universo_direcciones.csv
```

El resultado se almacena en:

```text
datos/direcciones_clean/universo_direcciones_clean.csv
```

Además se guarda la versión preprocesada (sin la columna limpia) en `datos/direcciones_clean/universo_direcciones_preprocessed.csv`.

Se ejecuta desde la raíz del proyecto:

```bash
python -m src.clean_adresses_file
```

O, con otras rutas:

```python
from src.clean_adresses_file import clean_adresses_file

clean_adresses_file(
    input_path="entrada.csv",
    preprocessed_path=None,   # None para no guardar el preprocesado
    output_path="salida.csv",
)
```

---

## Configuración de patrones

Los patrones de limpieza se encuentran en:

```text
config/patrones.py
```

Por ejemplo:

```python
Pattern(
    nombre="Municipio de",
    patron=[
        {"MUNICIPIO"},
        {"DE"},
    ]
)
```

Los elementos del patrón son conjuntos (`set`) para permitir diferentes variantes de un mismo token:

```python
Pattern(
    nombre="Ubicado en la",
    patron=[
        {"UBICADA", "UBICADO"},
        {"EN"},
        {"LA", "EL"},
    ]
)
```
De esta manera, el mismo patrón puede reconocer:

```text
UBICADO EN EL
UBICADA EN LA
```

sin tener que crear una regla independiente para cada variante.

---

## Normalización

La comparación de patrones utiliza una función de normalización que:

1. Convierte los tokens a mayúsculas.
2. Elimina espacios sobrantes.
3. Elimina puntos.
4. Elimina acentos únicamente para efectos de comparación.

Por ejemplo:

```text
"ubicada"
"UBICADA"
"ubicáda"
"UBICADA."
```

pueden ser tratados como equivalentes durante la búsqueda de patrones.

La normalización **no modifica directamente el texto original de la dirección**; se utiliza para facilitar las comparaciones.

---

## Filosofía del proyecto

El sistema busca mantener separadas las diferentes responsabilidades del proceso:

```text
Tokenización
     │
     ├── Reemplazo de abreviaturas
     │
     ├── Eliminación de caracteres y puntuación
     │
     ├── Eliminación de ruido e información redundante
     │
     ├── Eliminación de duplicados
     │
     └── Unificación de mayúsculas
```

Esto permite modificar o ampliar cada etapa independientemente.

Las reglas de limpieza no están codificadas directamente dentro de las funciones de procesamiento, sino que se definen como datos mediante objetos `Pattern`. Esto facilita agregar, modificar o retirar reglas conforme se encuentren nuevos casos en el universo de direcciones.

---

## Estado actual

El proyecto se encuentra en desarrollo. Actualmente el pipeline contempla:

* [x] Tokenización de direcciones.
* [x] Reemplazo de abreviaturas mediante diccionario.
* [x] Normalización de tokens para comparación.
* [x] Detección de patrones.
* [x] Eliminación de ruido textual.
* [x] Eliminación configurable de caracteres.
* [x] Eliminación de segmentos y palabras clave duplicados.
* [x] Limpieza de puntuación y unificación de mayúsculas.
* [x] Avisos para revisión manual.
* [x] Procesamiento de archivos de direcciones.
* [x] Procesamiento de `DataFrame` en memoria (base para la app).
* [x] App de Streamlit para subir un CSV y descargar la versión limpia.
* [ ] Reconstrucción de una representación final estandarizada de la dirección.
* [ ] Validación de los resultados.
* [ ] Ampliación y refinamiento de reglas de limpieza.

---