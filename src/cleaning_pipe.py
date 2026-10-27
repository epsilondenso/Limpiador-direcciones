from .replace_abrev import (
    tokenizar_direccion,
    reemplazar_abrevs
)

from .elim_noise import (
    limpiar_ruido
)

from config.patrones import abrev_dict, Pattern, PATRONES

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


def clean(raw_adress: str, elim_caracters: bool = True, patterns: list[Pattern] = PATRONES, caracter: str = "-") -> list[str]:
    """
    Limpia una dirección: tokenizar -> reemplazar abreviaturas -> limpiar ruido -> eliminar carácter.

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

    Returns
    -------
    list[str]
        Tokens de la dirección limpia.
    """
    tokens = tokenizar_direccion(raw_adress)
    tokens = reemplazar_abrevs(tokens, abrev_dict=abrev_dict)
    tokens = limpiar_ruido(tokens=tokens, patterns=patterns)
    if elim_caracters:
        tokens = elim_caracter(tokens, caracter=caracter)

    return tokens
