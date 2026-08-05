from dataclasses import dataclass

@dataclass(frozen=True)
class Pattern:
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

]