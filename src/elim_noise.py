import unicodedata
import pandas as pd
from config.patrones import Pattern, PATRONES
from src.replace_abrev import tokenizar_direccion

def normalizar(token: str) -> str:
    """
    Normaliza un token para facilitar comparaciones.

    Convierte a mayúsculas y elimina espacios sobrantes, puntos y acentos.

    Parameters
    ----------
    token : str
        Token a normalizar.

    Returns
    -------
    str
        Token normalizado.
    """

    token = token.upper().strip().replace(".", "")#.replace("-","")

    token = "".join(
        c for c in unicodedata.normalize("NFD", token)
        if unicodedata.category(c) != "Mn"
    )

    return token

def match(tokens: list[str], pattern: Pattern, i: int) -> bool:
    """
    Comprueba si una lista de tokens, a partir del i-ésimo token, coincide con un patrón dado.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    pattern : Pattern
        Patrón a comparar.
    i : int
        Posición inicial en ``tokens``.

    Returns
    -------
    bool
        ``True`` si hay coincidencia.
    """

    secuencia = pattern.patron

    if i + len(secuencia) > len(tokens):
        return False

    for j in range(len(secuencia)):
        if normalizar(tokens[i+j]) not in secuencia[j]:
            return False

    return True

def buscar_match(tokens: list[str], pattern: Pattern) -> int | None:
    """
    Busca la primera posición en la que una lista de tokens hace match con un patrón dado.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    pattern : Pattern
        Patrón a buscar.

    Returns
    -------
    int | None
        Índice de la primera coincidencia, o ``None`` si no hay.
    """

    for i in range(len(tokens)):
        if match(tokens, pattern, i):
            return i
    return None

def eliminar_rango(tokens: list[str], start: int, long: int) -> list[str]:
    """
    Elimina ``long`` tokens a partir de la posición ``start``.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    start : int
        Posición inicial.
    long : int
        Número de tokens a eliminar.

    Returns
    -------
    list[str]
        Tokens sin el rango eliminado.
    """

    return tokens[:start] + tokens[start+long:]

def eliminar_patron(tokens: list[str], pattern: Pattern) -> list[str]:
    """
    Elimina la primera ocurrencia de un patrón en una lista de tokens.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    pattern : Pattern
        Patrón a eliminar.

    Returns
    -------
    list[str]
        Tokens sin la primera ocurrencia del patrón.
    """

    start = buscar_match(tokens, pattern)
    if start is not None:
        return eliminar_rango(tokens, start, len(pattern.patron))
    else:
        return tokens

def limpiar_ruido(tokens: list[str], patterns: list[Pattern] = PATRONES) -> list[str]:
    """
    Recorre la lista de patrones y elimina la primera aparición de cada uno.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    patterns : list[Pattern]
        Patrones a eliminar, aplicados en orden.

    Returns
    -------
    list[str]
        Tokens sin ruido.
    """

    for i in range(len(patterns)):
        tokens = eliminar_patron(tokens, patterns[i])
    return tokens

def redundant_patterns(adresses_df: pd.DataFrame, columns: list[str], adress_index: int) -> list[Pattern]:
    """
    Construye patrones a partir de los valores de ``columns`` de un registro (p. ej. estado, municipio),
    para eliminarlos de su dirección por ser redundantes.

    Parameters
    ----------
    adresses_df : pd.DataFrame
        Datos de direcciones.
    columns : list[str]
        Columnas cuyos valores se consideran redundantes.
    adress_index : int
        Índice (etiqueta) del registro.

    Returns
    -------
    list[Pattern]
        Un patrón por columna.
    """

    red_ptrns = []
    for columna in columns:
        direccion = str(adresses_df.loc[adress_index, columna])
        tokens = tokenizar_direccion(direccion)
        norm_tokens = [normalizar(token) for token in tokens]
        red_ptrns.append(Pattern(nombre = direccion, patron=[{token} for token in norm_tokens]))

    return red_ptrns
