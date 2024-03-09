from enum import Enum


class Spielstatus(Enum):
    KEIN_SPIEL = 0
    WARTE_AUF_VORSCHLÄGE = 1
    SPIEL_IM_BETRIEB = 2
