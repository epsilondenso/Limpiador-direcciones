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



test_new_adress = pd.read_csv(DIRECCIONES / "universo_direcciones.csv")
test_new_adress = test_new_adress.dropna(subset=["DIRECCIÓN GARANTÍA"]).drop_duplicates().fillna("Sin info")
test_new_adress["ESTADO"] = test_new_adress["ESTADO"].replace(ESTADOS_MAP)
test_new_adress.to_csv(path_or_buf = DIRECCIONES_CLEAN / "universo_direcciones_clean.csv", index=False)

direcciones = test_new_adress.copy()

clean_adresses = []
for i in range(direcciones.shape[0]):
    index = direcciones.index[i]
    red_ptrns = redundant_patterns(direcciones, columnas, index)
    clean_tokens = clean(raw_adress = direcciones["DIRECCIÓN GARANTÍA"][index], patterns= PATRONES + red_ptrns)
    clean_adresses.append(join_tokens(clean_tokens))
direcciones["DIRECCIÓN LIMPIA"] = clean_adresses
direcciones.to_csv("test_pipe.csv", index= False)
