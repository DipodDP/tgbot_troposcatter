from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.i18n import t_bot


def get_use_file_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[[
            InlineKeyboardButton(t_bot('btn_use_file', lang), callback_data='use_file'),
            InlineKeyboardButton(t_bot('btn_del_file', lang), callback_data='del_file'),
        ]],
    )


def get_add_names_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[[
            InlineKeyboardButton(t_bot('btn_yes', lang), callback_data='yes_names'),
            InlineKeyboardButton(t_bot('btn_no', lang), callback_data='no_names'),
        ]],
    )


def get_add_coords_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[[
            InlineKeyboardButton(t_bot('btn_yes', lang), callback_data='yes_coords'),
            InlineKeyboardButton(t_bot('btn_no', lang), callback_data='no_coords'),
        ]],
    )


def get_offer_set_heights_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=[[
            InlineKeyboardButton(t_bot('btn_set_heights', lang), callback_data='set_custom_heights'),
        ]],
    )


def get_show_volume_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(t_bot('btn_show_volume', lang), callback_data='show_volume'),
        ]],
    )


def get_show_report_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(t_bot('btn_show_report', lang), callback_data='show_report'),
        ]],
    )
