from .replace_abrev import (
    tokenizar_direccion,
    reemplazar_abrevs
)

from .elim_noise import (
    limpiar_ruido
)

from config.patrones import abrev_dict

def elim_caracter(tokens: list[str], caracter: str = "-"):
    new_tokens = [token for token in tokens if token != caracter]
    return new_tokens


def clean(raw_adress: str, elim_caracters: bool = True, caracter = "-") -> list[str]:

    """
    raw_adress -> tokenizar -> reemp_abrevs -> limpiar_ruido
    PARAMS:
    -raw_adress: Dirección en sucio
    -caracter: Solo se usa cuando elim_caracters = True
    """
    tokens = tokenizar_direccion(raw_adress)
    tokens = reemplazar_abrevs(tokens, abrev_dict=abrev_dict)
    tokens = elim_caracter(limpiar_ruido(tokens= tokens), caracter = caracter) if elim_caracter else limpiar_ruido(tokens= tokens)

    return tokens