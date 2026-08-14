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

## Pipeline

El proceso principal sigue las siguientes etapas:

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
 Eliminación de ruido
       │
       ▼
Eliminación de caracteres
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

La tokenización se realiza mediante una expresión regular.

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

### 3. Eliminación de ruido

Después de reemplazar las abreviaturas, se eliminan expresiones que aportan poca o ninguna información para identificar la ubicación.

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

### 4. Eliminación de caracteres

El pipeline permite eliminar determinados caracteres que aparecen como separadores y que no aportan información a la dirección.

Por defecto se elimina el guion:

```python
tokens = clean(direccion)
```

## Estructura del proyecto

```text
LIMPIEZA_DIRECCIONES/
│
├── config/
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
│   ├── elim_noise.py
│   ├── replace_abrev.py
│   └── __init__.py
│
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

* **`cleaning_pipe.py`**
  Integra las diferentes etapas en un único pipeline.

* **`clean_adresses_file.py`**
  Script para realizar el procesamiento de un archivo de direcciones.

### `config/`

Contiene configuraciones y reglas utilizadas por el pipeline.

* **`paths.py`**: define las rutas principales del proyecto.
* **`patrones.py`**: contiene los patrones utilizados para identificar y eliminar ruido, así como la carga del diccionario de abreviaturas.

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

Actualmente el proyecto utiliza principalmente:

```text
pandas==2.3.1
```

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

### Procesamiento de un archivo

El proyecto incluye un script para procesar el universo de direcciones localizado en:

```text
datos/direcciones_raw/universo_direcciones.csv
```

El resultado se almacena en:

```text
datos/direcciones_clean/universo_direcciones_clean.csv
```

El procesamiento elimina registros sin dirección y duplicados antes de generar el archivo de salida.

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
altaltiuminmovalor2025@gmail.com
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
     ├── Eliminación de ruido
     │
     └── Eliminación de caracteres
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
* [x] Procesamiento de archivos de direcciones.
* [ ] Reconstrucción de una representación final estandarizada de la dirección.
* [ ] Validación de los resultados.
* [ ] Ampliación y refinamiento de reglas de limpieza.

---