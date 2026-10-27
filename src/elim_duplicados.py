from config.patrones import abrev_dict, KEYWORDS_NOMBRE, STOPWORDS
from src.elim_noise import normalizar

#Palabras clave: los significados del diccionario de abreviaturas, normalizados (CALLE, NO, MZ, LT...)
KEYWORDS = {normalizar(v) for v in abrev_dict.values() if isinstance(v, str) and normalizar(v)}


def _tiene_contenido(norm_tokens: list[str]) -> bool:
    """
    Indica si un segmento es una copia con información propia: contiene un número (o "S/N")
    y al menos dos tokens que no son palabras clave ni stopwords.

    Así no se eliminan coincidencias parciales de nombres ("B DE LA", "LOMAS DE LA").

    Parameters
    ----------
    norm_tokens : list[str]
        Tokens normalizados del segmento.

    Returns
    -------
    bool
        ``True`` si el segmento aporta información propia.
    """

    contenido = [token for token in norm_tokens if token not in KEYWORDS and token not in STOPWORDS]
    tiene_numero = any(any(c.isdigit() for c in token) or token == "S/N" for token in contenido)
    return tiene_numero and len(contenido) >= 2


def _mayor_repeticion(norm: list[str], i: int, previos: list[str]) -> int:
    """
    Longitud del segmento más largo que empieza en ``norm[i]`` y ya aparece en ``previos``.

    Parameters
    ----------
    norm : list[str]
        Tokens normalizados.
    i : int
        Posición inicial en ``norm``.
    previos : list[str]
        Tokens normalizados ya conservados.

    Returns
    -------
    int
        Longitud de la repetición más larga (0 si no hay).
    """

    mayor = 0
    for j in range(len(previos)):
        k = 0
        while i + k < len(norm) and j + k < len(previos) and previos[j+k] == norm[i+k]:
            k += 1
        mayor = max(mayor, k)
    return mayor


def eliminar_segmentos_repetidos(tokens: list[str], min_len: int = 3) -> list[str]:
    """
    Elimina segmentos de al menos ``min_len`` tokens idénticos a uno anterior
    ("Av. TOLUCA No. 5 0001 Av. TOLUCA No. 5" -> "Av. TOLUCA No. 5 0001").

    No se eliminan segmentos formados solo por palabras clave y stopwords ("DE LA Calle").

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    min_len : int
        Longitud mínima del segmento repetido.

    Returns
    -------
    list[str]
        Tokens sin segmentos repetidos.
    """

    norm = [normalizar(token) for token in tokens]
    previos = []
    new_tokens = []
    i = 0
    while i < len(tokens):
        largo = _mayor_repeticion(norm, i, previos)
        if largo >= min_len and _tiene_contenido(norm[i:i+largo]):
            i += largo
            continue
        previos.append(norm[i])
        new_tokens.append(tokens[i])
        i += 1
    return new_tokens


def colapsar_consecutivas(tokens: list[str], keywords: set[str] = KEYWORDS) -> list[str]:
    """
    Elimina las repeticiones consecutivas de una palabra clave ("Calle Calle" -> "Calle")
    o de una palabra de 3 o más letras ("PUEBLA PUEBLA" -> "PUEBLA").

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    keywords : set[str]
        Palabras clave normalizadas.

    Returns
    -------
    list[str]
        Tokens sin palabras clave repetidas consecutivamente.
    """

    new_tokens = []
    for token in tokens:
        norm = normalizar(token)
        repetible = norm in keywords or (norm.isalpha() and len(norm) >= 3)
        if new_tokens and repetible and norm == normalizar(new_tokens[-1]):
            continue
        new_tokens.append(token)
    return new_tokens


def eliminar_repetidas(tokens: list[str], keywords: set[str] = KEYWORDS,
                       keywords_nombre: set[str] = KEYWORDS_NOMBRE) -> list[str]:
    """
    Elimina una palabra clave y su valor cuando ese mismo par ya apareció antes
    ("Mz. 8 Lt. 11 ... Mz. 8" -> "Mz. 8 Lt. 11 ...").

    El valor es el primer token que no es palabra clave tras ella, por lo que
    "No. Ext. 4126" y "No. Int. A" se consideran distintos. Las palabras de
    ``keywords_nombre`` se ignoran, ya que su valor ocupa varias palabras.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    keywords : set[str]
        Palabras clave normalizadas.
    keywords_nombre : set[str]
        Palabras clave cuyo valor es un nombre de varias palabras.

    Returns
    -------
    list[str]
        Tokens sin pares palabra clave-valor repetidos.
    """

    norm = [normalizar(token) for token in tokens]
    vistos = set()
    new_tokens = []
    i = 0
    while i < len(tokens):
        if norm[i] in keywords and norm[i] not in keywords_nombre:
            j = i + 1
            while j < len(tokens) and norm[j] in keywords:
                j += 1
            if j < len(tokens):
                clave = tuple(norm[i:j+1])
                if clave not in vistos:
                    vistos.add(clave)
                    new_tokens.extend(tokens[i:j+1])
                i = j + 1
                continue
        new_tokens.append(tokens[i])
        i += 1
    return new_tokens


def eliminar_duplicados(tokens: list[str]) -> list[str]:
    """
    Elimina duplicados sin perder información: primero los segmentos repetidos, luego las
    palabras clave consecutivas y por último los pares palabra clave-valor repetidos.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.

    Returns
    -------
    list[str]
        Tokens sin palabras clave duplicadas.
    """

    return eliminar_repetidas(colapsar_consecutivas(eliminar_segmentos_repetidos(tokens)))
