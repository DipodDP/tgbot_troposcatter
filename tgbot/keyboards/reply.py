# main menu
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from tgbot.i18n import SUPPORTED_LANGS, t_bot


# ---------------------------------------------------------------------------
# Factory functions — call with lang to get a localized keyboard
# ---------------------------------------------------------------------------

def get_main_menu(lang: str = 'en') -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        KeyboardButton(t_bot('btn_calc_t', lang)),
        KeyboardButton(t_bot('btn_show_climate_zone', lang)),
        KeyboardButton(t_bot('btn_show_bot_inf', lang)),
    )


def get_calc_t_menu(lang: str = 'en') -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        KeyboardButton(t_bot('btn_next', lang)),
        KeyboardButton(t_bot('btn_back', lang)),
    )


def get_climate_zone_menu(lang: str = 'en') -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        KeyboardButton(t_bot('btn_climate_zones', lang)),
        KeyboardButton(t_bot('btn_back', lang)),
    )


def get_bot_inf_menu(lang: str = 'en') -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
        KeyboardButton(t_bot('btn_saved_sites', lang)),
        KeyboardButton(t_bot('btn_bot_inf', lang)),
        KeyboardButton(t_bot('btn_like', lang)),
        KeyboardButton(t_bot('btn_back', lang)),
    )


# ---------------------------------------------------------------------------
# All-language text sets — used in handler registrations so a handler
# responds to the same button regardless of which language the user has.
# ---------------------------------------------------------------------------

def _all_texts(key: str) -> list[str]:
    """Return the set of button texts for *key* across all supported languages."""
    return list({t_bot(key, lang) for lang in SUPPORTED_LANGS})


ALL_BTN_CALC_T = _all_texts('btn_calc_t')
ALL_BTN_SHOW_CLIMATE_ZONE = _all_texts('btn_show_climate_zone')
ALL_BTN_SHOW_BOT_INF = _all_texts('btn_show_bot_inf')
ALL_BTN_NEXT = _all_texts('btn_next')
ALL_BTN_BACK = _all_texts('btn_back')
ALL_BTN_CLIMATE_ZONES = _all_texts('btn_climate_zones')
ALL_BTN_BOT_INF = _all_texts('btn_bot_inf')
ALL_BTN_SAVED_SITES = _all_texts('btn_saved_sites')
ALL_BTN_LIKE = _all_texts('btn_like')
