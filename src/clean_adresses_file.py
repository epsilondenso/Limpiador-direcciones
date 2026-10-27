from pathlib import Path
import pandas as pd
from config.paths import DIRECCIONES, DIRECCIONES_CLEAN
from src.pipeline import index_raw, preprocess, clean_addresses_df


def clean_adresses_file(input_path: str | Path = DIRECCIONES / "universo_direcciones.csv",
                        indexed_path: str | Path | None = DIRECCIONES / "universo_direcciones_indexed.csv",
                        preprocessed_path: str | Path | None = DIRECCIONES_CLEAN / "universo_direcciones_preprocessed.csv",
                        output_path: str | Path = DIRECCIONES_CLEAN / "universo_direcciones_clean.csv") -> pd.DataFrame:
    """
    Lee un CSV crudo, lo indexa, limpia sus direcciones y guarda el resultado.

    Parameters
    ----------
    input_path : str | Path
        CSV crudo de entrada.
    indexed_path : str | Path | None
        Dónde guardar el CSV crudo con la columna ``ID``. ``None`` para no guardarlo.
    preprocessed_path : str | Path | None
        Dónde guardar el CSV preprocesado (sin dirección limpia). ``None`` para no guardarlo.
    output_path : str | Path
        Dónde guardar el CSV con la columna ``DIRECCIÓN LIMPIA``.

    Returns
    -------
    pd.DataFrame
        Datos limpios.
    """
    raw = index_raw(pd.read_csv(input_path))

    if indexed_path is not None:
        raw.to_csv(path_or_buf=indexed_path, index=False)

    if preprocessed_path is not None:
        preprocess(raw).to_csv(path_or_buf=preprocessed_path, index=False)

    cleaned = clean_addresses_df(raw)
    cleaned.to_csv(path_or_buf=output_path, index=False)

    return cleaned


if __name__ == "__main__":
    clean_adresses_file()
