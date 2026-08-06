import pandas as pd
from config.paths import DIRECCIONES, DIRECCIONES_CLEAN

test_new_adress = pd.read_csv(DIRECCIONES / "universo_direcciones.csv")
test_new_adress.dropna(subset=["DIRECCIÓN GARANTÍA"]).drop_duplicates().to_csv(DIRECCIONES_CLEAN / "universo_direcciones_clean.csv", index=False)