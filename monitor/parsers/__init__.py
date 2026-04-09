from parsers.vc import parse_vc
from parsers.pikabu import parse_pikabu
from parsers.alta_forum import parse_alta_forum
from parsers.dzen import parse_dzen
from parsers.chinapostman import parse_chinapostman
from parsers.tvoipostavshik import parse_tvoipostavshik
from parsers.mp_forum import parse_mp_forum
from parsers.telegram_chats import setup_telegram_listener

ALL_PARSERS = [
    parse_vc,
    parse_pikabu,
    parse_alta_forum,
    parse_dzen,
    parse_chinapostman,
    parse_tvoipostavshik,
    parse_mp_forum,
]
