from config.patrones import abrev_dict, KEYWORDS_NOMBRE
from src.elim_noise import normalizar

#Palabras clave: los significados del diccionario de abreviaturas, normalizados (CALLE, NO, MZ, LT...)
KEYWORDS = {normalizar(v) for v in abrev_dict.values() if isinstance(v, str) and normalizar(v)}


def colapsar_consecutivas(tokens: list[str], keywords: set[str] = KEYWORDS) -> list[str]:
    """
    Elimina las repeticiones consecutivas de una palabra clave ("Calle Calle" -> "Calle").

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
        if new_tokens and norm in keywords and norm == normalizar(new_tokens[-1]):
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
    Elimina palabras clave duplicadas sin perder información: primero las consecutivas
    y después los pares palabra clave-valor repetidos.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.

    Returns
    -------
    list[str]
        Tokens sin palabras clave duplicadas.
    """

    return eliminar_repetidas(colapsar_consecutivas(tokens))
