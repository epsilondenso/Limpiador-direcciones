from pathlib import Path
import pandas as pd
import streamlit as st
from src.pipeline import REQUIRED_COLUMNS, ADDRESS_COLUMN, OUTPUT_COLUMN, clean_addresses_df


def read_csv(file) -> pd.DataFrame:
    """
    Lee un CSV subido como texto, probando UTF-8 y, si falla, cp1252 (Excel en Windows).

    Parameters
    ----------
    file : UploadedFile
        Archivo subido con ``st.file_uploader``.

    Returns
    -------
    pd.DataFrame
        Datos leídos, todas las columnas como texto.
    """
    try:
        return pd.read_csv(file, dtype=str, encoding="utf-8-sig")
    except UnicodeDecodeError:
        file.seek(0)
        return pd.read_csv(file, dtype=str, encoding="cp1252")


st.set_page_config(page_title="Limpieza de direcciones", page_icon="🏠")
st.title("Limpieza de direcciones")

st.markdown(
    f"""
Sube un CSV con direcciones en crudo y descarga una versión con la dirección limpia.

**Cómo funciona:** se descartan filas sin dirección y duplicadas, y en cada dirección se
expanden abreviaturas (`AV` → `Av.`), se quitan expresiones de relleno
("ubicado en", "predio urbano"…) y se eliminan el estado, municipio, colonia y CP,
que ya tienen su propia columna. El resultado se añade en la columna **`{OUTPUT_COLUMN}`**.

**Columnas requeridas** (puede tener otras; se conservan):
{", ".join(f"`{col}`" for col in REQUIRED_COLUMNS)}
"""
)

uploaded = st.file_uploader("CSV de direcciones", type="csv")

if uploaded is not None:
    raw = read_csv(uploaded)

    missing = [col for col in REQUIRED_COLUMNS if col not in raw.columns]
    if missing:
        st.error(f"Al archivo le faltan estas columnas: {', '.join(missing)}")
        st.stop()

    st.write(f"{len(raw):,} filas cargadas.")

    if st.button("Limpiar direcciones", type="primary"):
        bar = st.progress(0.0, text="Limpiando direcciones…")
        cleaned = clean_addresses_df(raw, progress=lambda p: bar.progress(p, text="Limpiando direcciones…"))
        bar.empty()
        st.session_state["result"] = (uploaded.name, cleaned)

    result = st.session_state.get("result")
    if result is not None and result[0] == uploaded.name:
        name, cleaned = result
        st.success(f"Listo: {len(cleaned):,} direcciones limpias ({len(raw) - len(cleaned):,} filas descartadas).")
        st.dataframe(cleaned[[ADDRESS_COLUMN, OUTPUT_COLUMN]].head(20), hide_index=True)
        st.download_button(
            "Descargar CSV limpio",
            data=cleaned.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{Path(name).stem}_limpio.csv",
            mime="text/csv",
        )
