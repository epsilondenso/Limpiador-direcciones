import re 

def tokenizar_direccion(direccion: str) -> list[str]:
    """
    Tokeniza una dirección. Cada token puede ser una palabra, un número o un guión.

    PARAMS:
        -direccion: str. Dirección a tokenizar.
    RETURNS:
        -tokens: list[str]. Lista de tokens.
    """

    tokens = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ\.]+|\d+|[-/]|[#/]", direccion)
    return tokens

def reemplazar_abrevs(tokens: list[str], abrev_dict: dict[str, str]) -> list[str]:
    """
    Reemplaza las abreviaturas en una lista de tokens por su significado.

    PARAMS:
        -tokens: list[str]. Lista de tokens.
        -abrev_dict: dict[str, str]. Diccionario de abreviaturas y sus significados.
    RETURNS:
        -nuevos_tokens: list[str]. Lista de tokens con las abreviaturas reemplazadas.
    """

    nuevos_tokens = []
    for token in tokens:
        if token in abrev_dict:
            nuevos_tokens.append(abrev_dict[token])
        else:
            nuevos_tokens.append(token)
    return nuevos_tokens