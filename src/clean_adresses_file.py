from pathlib import Path
import pandas as pd
from config.paths import DIRECCIONES, DIRECCIONES_CLEAN
from config.abrev_estados import ESTADOS_MAP
from config.patrones import PATRONES 
from src.elim_noise import redundant_patterns
from src.cleaning_pipe import clean


columnas = ["ESTADO", "MUNICIPIO", "COLONIA", "CP"]


def join_tokens(tokens: list[str]) -> str:
    joined = " ".join(tokens)
    return joined

def clean_adresses_file(input_paht: str|Path = DIRECCIONES / "universo_direcciones.csv",
                        preprocessed_path: str|Path = DIRECCIONES_CLEAN / "universo_direcciones_preprocessed.csv",
                        output_path: str|Path = DIRECCIONES_CLEAN / "universo_direcciones_clean.csv"):

    raw = pd.read_csv(input_paht)
    preprocessed = raw.dropna(subset=["DIRECCIÓN GARANTÍA"]).drop_duplicates().fillna("Sin info")
    preprocessed["ESTADO"] = preprocessed["ESTADO"].replace(ESTADOS_MAP)
    preprocessed.to_csv(path_or_buf = preprocessed_path, index=False)

    clean_adresses = [] 

    for i in range(preprocessed.shape[0]):
        index = preprocessed.index[i]
        red_ptrns = redundant_patterns(preprocessed, columnas, index)
        clean_tokens = clean(raw_adress = preprocessed["DIRECCIÓN GARANTÍA"][index], patterns= PATRONES + red_ptrns)
        clean_adresses.append(join_tokens(clean_tokens))
    preprocessed["DIRECCIÓN LIMPIA"] = clean_adresses
    cleaned = preprocessed.copy()
    cleaned.to_csv(path_or_buf = output_path, index= False)


    return cleaned

if __name__ == "__main__":
    clean_adresses_file()