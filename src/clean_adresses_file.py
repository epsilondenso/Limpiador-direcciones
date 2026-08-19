import pandas as pd
from config.paths import DIRECCIONES, DIRECCIONES_CLEAN
from config.abrev_estados import ESTADOS_MAP

test_new_adress = pd.read_csv(DIRECCIONES / "universo_direcciones.csv")
test_new_adress = test_new_adress.dropna(subset=["DIRECCIÓN GARANTÍA"]).drop_duplicates().fillna("Sin info")
test_new_adress["ESTADO"] = test_new_adress["ESTADO"].replace(ESTADOS_MAP)
test_new_adress.to_csv(path_or_buf = DIRECCIONES_CLEAN / "universo_direcciones_clean.csv", index=False)