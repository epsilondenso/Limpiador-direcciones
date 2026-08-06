from .replace_abrev import (
    tokenizar_direccion,
    reemplazar_abrevs
)

from .elim_noise import (
    limpiar_ruido
)

from config.patrones_a_eliminar import abrev_dict


def clean(raw_adress: str) -> list[str]:

    """
    raw_adress -> tokenizar -> reemp_abrevs -> limpiar_ruido
    """
    tokens = tokenizar_direccion(raw_adress)
    tokens = reemplazar_abrevs(tokens, abrev_dict=abrev_dict)
    tokens = limpiar_ruido(tokens= tokens)

    return tokens