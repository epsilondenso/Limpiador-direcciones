import unicodedata
import pandas as pd
from config.patrones import Pattern, PATRONES, PREFIJOS_CONTEXTO, TIPOS_VIA, ABREVS_AMBIGUAS, abrev_dict
from src.replace_abrev import tokenizar_direccion, reemplazar_abrevs
from src.formato import limpiar_puntuacion

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

def tokens_valor(valor: str) -> list[str]:
    """
    Tokeniza el valor de una columna de contexto aplicándole la misma limpieza que a la dirección
    (abreviaturas, guiones, puntuación y ruido), para que ambos sean comparables.

    Parameters
    ----------
    valor : str
        Valor de la columna (p. ej. la colonia).

    Returns
    -------
    list[str]
        Tokens normalizados del valor.
    """

    tokens = reemplazar_abrevs(tokenizar_direccion(valor), abrev_dict=abrev_dict, ambiguas=ABREVS_AMBIGUAS)
    tokens = limpiar_puntuacion([token for token in tokens if token != "-"])
    tokens = limpiar_ruido(tokens, PATRONES)
    return [norm for norm in (normalizar(token) for token in tokens) if norm]


def redundant_patterns(adresses_df: pd.DataFrame, columns: list[str], adress_index: int) -> list[Pattern]:
    """
    Construye patrones a partir de los valores de ``columns`` de un registro (p. ej. estado, municipio),
    para eliminarlos de su dirección por ser redundantes.

    Por cada columna se genera primero la variante con prefijo (``PREFIJOS_CONTEXTO``, p. ej. "C.P. 77524")
    y después el valor solo. Se ignoran valores sin ningún token de 3 o más caracteres ("0", "Sin info").

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
        Patrones redundantes, con prefijo antes que sin él.
    """

    red_ptrns = []
    for columna in columns:
        valor = str(adresses_df.loc[adress_index, columna])
        if valor == "Sin info":
            continue
        norm_tokens = tokens_valor(valor)
        if not any(len(token) >= 3 for token in norm_tokens):
            continue
        patron = [{token} for token in norm_tokens]
        prefijos = PREFIJOS_CONTEXTO.get(columna)
        if prefijos:
            red_ptrns.append(Pattern(nombre=f"{columna} {valor}", patron=[prefijos] + patron))
        red_ptrns.append(Pattern(nombre=valor, patron=patron))

    return red_ptrns


def eliminar_redundantes(tokens: list[str], patterns: list[Pattern], tipos_via: set[str] = TIPOS_VIA) -> list[str]:
    """
    Elimina todas las apariciones de cada patrón redundante, salvo las que parecen nombre de calle:
    las precedidas por un tipo de vía ("Av. JUAREZ") y, si el valor aparece más de una vez,
    la que está al inicio de la dirección. Si el valor ocupa toda la dirección, no se elimina.

    Parameters
    ----------
    tokens : list[str]
        Lista de tokens.
    patterns : list[Pattern]
        Patrones redundantes (ver ``redundant_patterns``).
    tipos_via : set[str]
        Tipos de vía normalizados.

    Returns
    -------
    list[str]
        Tokens sin los valores redundantes.
    """

    for pattern in patterns:
        largo = len(pattern.patron)
        inicios = []
        i = 0
        while i < len(tokens):
            if match(tokens, pattern, i):
                inicios.append(i)
                i += largo
            else:
                i += 1

        borrar = set()
        for inicio in inicios:
            es_calle = inicio > 0 and normalizar(tokens[inicio-1]) in tipos_via
            es_inicio = inicio == 0 and len(inicios) > 1
            if not (es_calle or es_inicio):
                borrar.update(range(inicio, inicio + largo))
        #Si el valor ocupa toda la dirección, la columna contiene la dirección (error de captura) y no se borra
        if len(borrar) < len(tokens):
            tokens = [token for k, token in enumerate(tokens) if k not in borrar]

    return tokens
