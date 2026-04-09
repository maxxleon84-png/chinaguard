from parsers.vc import parse_vc
from parsers.pikabu import parse_pikabu
from parsers.dzen import parse_dzen
from parsers.chinapostman import parse_chinapostman
from parsers.telegram_chats import setup_telegram_listener

ALL_PARSERS = [
    parse_vc,
    parse_pikabu,
    parse_dzen,
    parse_chinapostman,
]
