#Python
import re

LETRAS = "A-Za-zÁÉÍÓÚÑáéíóúñ"

#Unidades con barra que se conservan como un solo token: "S/N", "S/NO", "N/A", "Y/O" o fracciones "1/2"
UNIDAD_BARRA = rf"[Ss]\s*/\s*[Nn][Oo](?![{LETRAS}])\.?|[{LETRAS}]\s*/\s*[{LETRAS}](?![{LETRAS}])\.?|\d+\s*/\s*\d+"
TOKEN = rf"{UNIDAD_BARRA}|[{LETRAS}\.]+|\d+|[-/]|[#/]"
PEGADO = rf"([{LETRAS}]{{2,}}\.)([{LETRAS}].*)"
ROMANO = r"[IVXLCDM]+"


def separar_pegados(token: str) -> list[str]:
    """
    Separa abreviaturas pegadas a la palabra siguiente ("NO.INT." -> "NO.", "INT.").

    Solo se separa cuando antes del punto hay al menos dos letras, para no romper siglas como "B.C.S.".

    Parameters
    ----------
    token : str
        Token a separar.

    Returns
    -------
    list[str]
        Partes del token.
    """

    partes = []
    while (m := re.fullmatch(PEGADO, token)):
        partes.append(m.group(1))
        token = m.group(2)
    partes.append(token)
    return partes


def tokenizar_direccion(direccion: str) -> list[str]:
    """
    Tokeniza una dirección. Cada token puede ser una palabra, un número, un guion, ``/``, ``#``
    o una unidad con barra ("S/N", "1/2"). Las abreviaturas pegadas se separan.

    Parameters
    ----------
    direccion : str
        Dirección a tokenizar.

    Returns
    -------
    list[str]
        Lista de tokens.
    """

    tokens = []
    for token in re.findall(TOKEN, direccion):
        tokens.extend(separar_pegados(re.sub(r"\s+", "", token)))
    return tokens


def _seguido_de_numero(tokens: list[str], i: int) -> bool:
    """
    Indica si al token ``i`` le sigue (ignorando guiones) un número o un numeral romano.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    i : int
        Posición del token.

    Returns
    -------
    bool
        ``True`` si le sigue un número o un numeral romano.
    """

    j = i + 1
    while j < len(tokens) and tokens[j] == "-":
        j += 1
    return j < len(tokens) and (tokens[j].isdigit() or re.fullmatch(ROMANO, tokens[j]) is not None)


def reemplazar_abrevs(tokens: list[str], abrev_dict: dict[str, str], ambiguas: set[str] = frozenset()) -> list[str]:
    """
    Reemplaza las abreviaturas en una lista de tokens por su significado.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    abrev_dict : dict[str, str]
        Diccionario ``{abreviatura: significado}``.
    ambiguas : set[str]
        Abreviaturas que solo se reemplazan si les sigue un número o un numeral romano.

    Returns
    -------
    list[str]
        Lista de tokens con las abreviaturas reemplazadas.
    """

    nuevos_tokens = []
    for i, token in enumerate(tokens):
        if token in abrev_dict and (token not in ambiguas or _seguido_de_numero(tokens, i)):
            nuevos_tokens.append(abrev_dict[token])
        else:
            nuevos_tokens.append(token)
    return nuevos_tokens
