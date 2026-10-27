from collections.abc import Callable
import pandas as pd
from config.abrev_estados import ESTADOS_MAP
from config.patrones import PATRONES
from src.elim_noise import redundant_patterns
from src.cleaning_pipe import clean


ADDRESS_COLUMN = "DIRECCIÓN GARANTÍA"
CONTEXT_COLUMNS = ["ESTADO", "MUNICIPIO", "COLONIA", "CP"]
REQUIRED_COLUMNS = [ADDRESS_COLUMN] + CONTEXT_COLUMNS
OUTPUT_COLUMN = "DIRECCIÓN LIMPIA"
WARNINGS_COLUMN = "AVISOS"
MAX_TOKENS = 25


def avisos(tokens: list[str], max_tokens: int = MAX_TOKENS) -> str:
    """
    Señala direcciones limpias que conviene revisar a mano, sin modificarlas.

    Parameters
    ----------
    tokens : list[str]
        Tokens de la dirección limpia.
    max_tokens : int
        A partir de cuántos tokens se considera demasiado larga.

    Returns
    -------
    str
        Avisos separados por ``"; "``, o cadena vacía si no hay.
    """
    if not tokens:
        return "Dirección vacía"

    mensajes = []
    if not any(any(c.isdigit() for c in token) or token == "S/N" for token in tokens):
        mensajes.append("Sin número")
    if len(tokens) > max_tokens:
        mensajes.append("Demasiado larga (posible texto legal)")
    return "; ".join(mensajes)


def join_tokens(tokens: list[str]) -> str:
    """
    Une una lista de tokens en una sola cadena separada por espacios.

    Parameters
    ----------
    tokens : list[str]
        Tokens de la dirección.

    Returns
    -------
    str
        Dirección reconstruida.
    """
    return " ".join(tokens)


def validate_columns(df: pd.DataFrame) -> None:
    """
    Verifica que el DataFrame contenga todas las columnas requeridas.

    Parameters
    ----------
    df : pd.DataFrame
        Datos de entrada.

    Raises
    ------
    ValueError
        Si falta alguna de las columnas de ``REQUIRED_COLUMNS``.
    """
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")


def preprocess(raw: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina registros sin dirección y duplicados, rellena vacíos y expande abreviaturas de estados.

    Parameters
    ----------
    raw : pd.DataFrame
        Datos crudos con las columnas de ``REQUIRED_COLUMNS``.

    Returns
    -------
    pd.DataFrame
        Datos preprocesados (vacíos rellenados con ``"Sin info"``).
    """
    validate_columns(raw)
    preprocessed = raw.dropna(subset=[ADDRESS_COLUMN]).drop_duplicates().fillna("Sin info")
    preprocessed["ESTADO"] = preprocessed["ESTADO"].replace(ESTADOS_MAP)
    return preprocessed


def clean_addresses_df(raw: pd.DataFrame, progress: Callable[[float], None] | None = None) -> pd.DataFrame:
    """
    Preprocesa los datos y añade las columnas ``OUTPUT_COLUMN`` con la dirección limpia
    y ``WARNINGS_COLUMN`` con avisos para revisión manual.

    Además de los patrones de ``PATRONES``, de cada dirección se eliminan todas las apariciones
    del estado, municipio, colonia y CP de su propio registro, por ser redundantes.

    Parameters
    ----------
    raw : pd.DataFrame
        Datos crudos con las columnas de ``REQUIRED_COLUMNS``.
    progress : Callable[[float], None] | None
        Función opcional que recibe la fracción procesada (entre 0 y 1), p. ej. para una barra de progreso.

    Returns
    -------
    pd.DataFrame
        Datos preprocesados con las columnas ``OUTPUT_COLUMN`` y ``WARNINGS_COLUMN`` añadidas.
    """
    cleaned = preprocess(raw)
    total = len(cleaned)
    step = max(total // 100, 1)

    clean_adresses = []
    warnings = []
    for i, index in enumerate(cleaned.index, start=1):
        red_ptrns = redundant_patterns(cleaned, CONTEXT_COLUMNS, index)
        clean_tokens = clean(raw_adress=cleaned.loc[index, ADDRESS_COLUMN], patterns=PATRONES, redundantes=red_ptrns)
        clean_adresses.append(join_tokens(clean_tokens))
        warnings.append(avisos(clean_tokens))
        if progress is not None and (i % step == 0 or i == total):
            progress(i / total)
    cleaned[OUTPUT_COLUMN] = clean_adresses
    cleaned[WARNINGS_COLUMN] = warnings

    return cleaned
