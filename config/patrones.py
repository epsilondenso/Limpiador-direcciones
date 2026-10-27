from dataclasses import dataclass
import pandas as pd
from .paths import DICCIONARIOS 

@dataclass(frozen=True)
class Pattern:
    """
    Secuencia de tokens considerada ruido.

    Attributes
    ----------
    nombre : str
        Nombre descriptivo del patrón.
    patron : list[set[str]]
        Un conjunto de variantes válidas (normalizadas) por posición.
    action : str
        Acción a aplicar (actualmente solo ``"delete"``).
    """
    nombre: str
    patron: list[set[str]]
    action: str = "delete"


#PATRONES
PATRONES = [

    Pattern(
        nombre="Construido sobre",
        patron=[
            {"CONSTRUIDA", "CONSTRUIDO"},
            {"SOBRE"},
            {"LA", "EL"},
        ]
    ),

    Pattern(
        nombre="Sobre el/la",
        patron=[
            {"SOBRE"},
            {"LA", "EL"},
        ]
    ),

    Pattern(
        nombre="Ubicado en la",
        patron=[
            {"UBICADA", "UBICADO"},
            {"EN"},
            {"LA", "EL"},
        ]
    ),

    Pattern(
        nombre="Ubicado en",
        patron=[
            {"UBICADA", "UBICADO"},
            {"EN"}
        ]
    ),

    Pattern(
        nombre="Ubicado",
        patron = [
            {"UBICADO", "UBICADA"}
        ]
    ),

    Pattern(
        nombre="Identificado con la",
        patron=[
            {"IDENTIFICADA", "IDENTIFICADO"},
            {"CON"},
            {"EL", "LA"},
        ]
    ),

    Pattern(
        nombre="Identificado como",
        patron=[
            {"IDENTIFICADA", "IDENTIFICADO"},
            {"COMO"}
        ]
    ),

    Pattern(
        nombre="Marcado con",
        patron=[
            {"MARCADA", "MARCADO"},
            {"CON"},
            {"EL", "LA"},
        ]
    ),


    Pattern(
        nombre="Denominado como",
        patron=[
            {"DENOMINADA", "DENOMINADO"},
            {"COMO"}
        ]
    ),

    Pattern(
        nombre="Denominado",
        patron=[
            {"DENOMINADA", "DENOMINADO"},
        ]
    ),

    Pattern(
        nombre="Perteneciente a la",
        patron=[
            {"PERTENECIENTE"},
            {"A"},
            {"LA", "EL"},
        ]
    ),

    Pattern(
        nombre="Perteneciente al",
        patron=[
            {"PERTENECIENTE"},
            {"AL"},
        ]
    ),

    Pattern(
        nombre="Estado de",
        patron=[
            {"ESTADO"},
            {"DE"},
        ]
    ),

    Pattern(
        nombre="Municipio de",
        patron=[
            {"MUNICIPIO"},
            {"DE"},
        ]
    ),

    Pattern(
        nombre="Predio rústico",
        patron=[
            {"PREDIO"},
            {"RUSTICO"},
        ]
    ),

    Pattern(
        nombre="Predio urbano",
        patron=[
            {"PREDIO"},
            {"URBANO"},
        ]
    ),

    Pattern(
        nombre="Conjunto urbano",
        patron=[
            {"DEL"},
            {"CONJUNTO"},
            {"URBANO"},
            {"DE"},
        ]
    ),

    Pattern(
        nombre="Interés social",
        patron=[
            {"DE"},
            {"INTERES"},
            {"SOCIAL"},
        ]
    ),

    Pattern(
        nombre="Superficie",
        patron=[
            {"SUPERFICIE"},
        ]
    ),

    Pattern(
        nombre="oficial",
        patron=[
            {"OFICIAL"}
        ]
    ),

    Pattern(
        nombre="Catastralmente",
        patron=[
            {"CATASTRALMENTE"},
        ]
    ),

    Pattern(
        nombre="Identificado como",
        patron=[
            {"IDENTIFICADO", "IDENTIFICADA"},
            {"COMO"}
        ]
    ),

        Pattern(
        nombre="Colonia",
        patron=[
            {"COLONIA"}
        ]
    ),

        Pattern(
        nombre="Código postal",
        patron=[
            {"CP", "C.P", "C.P.", "cp", "c.p."},
        ]
    ),

        Pattern(
        nombre="De terreno",
        patron=[
            {"DE"},
            {"TERRENO"}
        ]
    ),

        Pattern(
            nombre = "Fraccionamiento",
            patron  =[{"FRACC", "FRACC.", "FRACCIONAMIENTO", "Fraccionamiento"}]

        )

]

#Palabras clave (normalizadas) cuyo valor es un nombre de varias palabras (p. ej. "Calle LOS PINOS").
#Para ellas solo se eliminan repeticiones consecutivas, no repeticiones con el mismo valor.
KEYWORDS_NOMBRE = {"CALLE", "AV", "COLONIA", "MUNICIPIO"}

#Abreviaturas de una letra que también pueden ser iniciales ("M. LOPEZ").
#Solo se reemplazan si les sigue un número o un numeral romano.
ABREVS_AMBIGUAS = {"M", "M.", "L", "L.", "N", "N."}

#Palabras sin contenido propio: un segmento repetido formado solo por ellas y palabras clave no se elimina.
STOPWORDS = {"DE", "DEL", "LA", "EL", "LOS", "LAS", "Y", "O", "E", "EN", "A", "AL", "CON"}

#Prefijos (normalizados) que se eliminan junto con el valor redundante de cada columna ("C.P. 77524", "CD. JUAREZ").
PREFIJOS_CONTEXTO = {
    "ESTADO": {"ESTADO", "EDO"},
    "MUNICIPIO": {"MUNICIPIO", "MPIO", "CD", "CIUDAD"},
    "COLONIA": {"COLONIA", "COL", "FRACC", "FRACCIONAMIENTO", "BARRIO", "BO"},
    "CP": {"CP"},
}

#Tipos de vía (normalizados): un valor redundante precedido por uno de ellos es el nombre de la calle y se conserva
#("Av. JUAREZ" con municipio Juárez).
TIPOS_VIA = {"CALLE", "AV", "PRIV", "PRIVADA", "CERRADA", "CDA", "BLVD", "BOULEVARD", "CALZ", "CALZADA",
             "PROL", "PROLONGACION", "CIRCUITO", "CTO", "CIRC", "RETORNO", "RET", "ANDADOR", "CARRETERA",
             "CAMINO", "PASEO"}

dict_abrevs_path = DICCIONARIOS / "dict_abrev.csv"
abrev_df= pd.read_csv(dict_abrevs_path)
abrev_dict= dict(zip(abrev_df['abrev'], abrev_df['significado']))