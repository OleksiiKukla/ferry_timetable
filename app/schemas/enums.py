from enum import Enum


class Countries(Enum):
    POLAND = "Poland"
    SWEDEN = "Sweden"


class CountriesAbbreviatedName(Enum):
    PL = "Poland"
    SE = "Sweden"


class FerryNames(Enum):
    BAL = "baltivia"
    CRA = "cracovia"
    MAZ = "mazovia"


class Ports(Enum):
    YSTAD = "ystad"
    SWINOUJSCIE = "swinoujscie"


class Languages(Enum):
    ENGLISH = "eng"
    UKRAINIAN = "ukr"
    POLISH = "pl"

class Owners(Enum):
    POLFERRIES = "polferries"
    UNITY_LINE = 'unity_line'