import re
import unicodedata
import pandas as pd
import config.paths as pths 
from config.patrones import Pattern, PATRONES
from src.replace_abrev import tokenizar_direccion

def normalizar(token: str) -> str:
    """
    Normaliza un token para facilitar comparaciones.

    - Convierte a mayúsculas.
    - Elimina acentos.
    - Elimina puntos.
    - Elimina espacios sobrantes.
    """

    token = token.upper().strip().replace(".", "")#.replace("-","")

    token = "".join(
        c for c in unicodedata.normalize("NFD", token)
        if unicodedata.category(c) != "Mn"
    )

    return token

def match(tokens: list[str], pattern: Pattern, i:int) -> bool:

    """Comprueba si una lista de tokens, a partir del i-ésimo token, coincide con un patrón dado."""

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
    Puede recibir la lista completa de tokens
    """

    for i in range(len(tokens)):
        if match(tokens, pattern, i):
            return i
    return None

def eliminar_rango(tokens: list[str], start: int, long: int) -> list[str]:

    return tokens[:start] + tokens[start+long:]

def eliminar_patron(tokens: list[str], pattern: Pattern) -> list[str]:
    """
    Elimina la primera ocurrencia de un patrón en una lista de tokens.
    """

    start = buscar_match(tokens, pattern)
    if start is not None:
        return eliminar_rango(tokens, start, len(pattern.patron))
    else:
        return tokens
    
def limpiar_ruido(tokens: list[str], patterns: list[Pattern] = PATRONES) -> list[str]:
    """
    Recorre toda la lista de patrones, elimina todas las primeras apariciones
    """

    for i in range(len(patterns)):
        tokens = eliminar_patron(tokens, patterns[i])
    return tokens

def redundant_patterns(adresses_df: pd.DataFrame, columns: list[str], adress_index: int) -> list[Pattern]:

    red_ptrns = []
    for columna in columns:
        direccion = adresses_df.loc[adress_index, columna]
        tokens = tokenizar_direccion(direccion)
        norm_tokens = [normalizar(token) for token in tokens]
        red_ptrns.append(Pattern(nombre = direccion, patron=[{token} for token in norm_tokens]))

    return red_ptrns
