import re
from config.patrones import abrev_dict

#Formas de las palabras clave tal como aparecen en el diccionario ("Calle", "Mz.", "No.")
FORMAS_KEYWORDS = {v for v in abrev_dict.values() if isinstance(v, str)}


def limpiar_puntuacion(tokens: list[str]) -> list[str]:
    """
    Elimina tokens formados solo por puntos y barras ``/`` sueltas al inicio o al final.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.

    Returns
    -------
    list[str]
        Tokens sin puntuación suelta.
    """

    tokens = [token for token in tokens if not re.fullmatch(r"\.+", token)]
    while tokens and tokens[0] == "/":
        tokens = tokens[1:]
    while tokens and tokens[-1] == "/":
        tokens = tokens[:-1]
    return tokens


def unificar_mayusculas(tokens: list[str], formas_keywords: set[str] = FORMAS_KEYWORDS) -> list[str]:
    """
    Pasa los tokens a mayúsculas, salvo las palabras clave del diccionario ("Calle", "Mz.").

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    formas_keywords : set[str]
        Tokens que conservan su forma.

    Returns
    -------
    list[str]
        Tokens en mayúsculas.
    """

    return [token if token in formas_keywords else token.upper() for token in tokens]
