from .replace_abrev import (
    tokenizar_direccion,
    reemplazar_abrevs
)

from .elim_noise import (
    limpiar_ruido,
    eliminar_redundantes
)

from .elim_duplicados import (
    eliminar_duplicados
)

from .formato import (
    limpiar_puntuacion,
    unificar_mayusculas
)

from config.patrones import abrev_dict, Pattern, PATRONES, ABREVS_AMBIGUAS

def elim_caracter(tokens: list[str], caracter: str = "-") -> list[str]:
    """
    Elimina los tokens que sean exactamente igual a ``caracter``.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    caracter : str
        Carácter a eliminar.

    Returns
    -------
    list[str]
        Tokens sin las apariciones de ``caracter``.
    """
    new_tokens = [token for token in tokens if token != caracter]
    return new_tokens


def clean(raw_adress: str, elim_caracters: bool = True, patterns: list[Pattern] = PATRONES, caracter: str = "-",
          elim_duplicados: bool = True, mayusculas: bool = True, redundantes: list[Pattern] | None = None) -> list[str]:
    """
    Limpia una dirección: tokenizar -> reemplazar abreviaturas -> eliminar carácter -> limpiar puntuación
    -> limpiar ruido -> eliminar redundantes -> eliminar duplicados -> unificar mayúsculas.

    Parameters
    ----------
    raw_adress : str
        Dirección en sucio.
    elim_caracters : bool
        Si es ``True``, elimina los tokens iguales a ``caracter``.
    patterns : list[Pattern]
        Patrones de ruido a eliminar.
    caracter : str
        Carácter a eliminar; solo se usa cuando ``elim_caracters=True``.
    elim_duplicados : bool
        Si es ``True``, elimina duplicados (ver ``eliminar_duplicados``).
    mayusculas : bool
        Si es ``True``, pasa a mayúsculas todo salvo las palabras clave del diccionario.
    redundantes : list[Pattern] | None
        Patrones de información redundante del registro (ver ``redundant_patterns``); se eliminan todas sus apariciones.

    Returns
    -------
    list[str]
        Tokens de la dirección limpia.
    """
    tokens = tokenizar_direccion(raw_adress)
    tokens = reemplazar_abrevs(tokens, abrev_dict=abrev_dict, ambiguas=ABREVS_AMBIGUAS)
    if elim_caracters:
        tokens = elim_caracter(tokens, caracter=caracter)
    tokens = limpiar_puntuacion(tokens)
    tokens = limpiar_ruido(tokens=tokens, patterns=patterns)
    if redundantes:
        tokens = eliminar_redundantes(tokens, redundantes)
    if elim_duplicados:
        tokens = eliminar_duplicados(tokens)
    if mayusculas:
        tokens = unificar_mayusculas(tokens)

    return tokens
