from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

use_file = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Использовать', callback_data='use_file'),
            InlineKeyboardButton(text='Удалить', callback_data='del_file'),
        ]
    ],
)

add_names = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Да', callback_data='yes_names'),
            InlineKeyboardButton(text='Нет', callback_data='no_names'),
        ]
    ],
)

add_coords = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Да', callback_data='yes_coords'),
            InlineKeyboardButton(text='Нет', callback_data='no_coords'),
        ]
    ],
)

offer_set_heights = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [InlineKeyboardButton(text='Задать высоту', callback_data='set_custom_heights')]
    ],
)

# Keyboards for toggling report views
show_volume_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Показать данные об объеме', callback_data='show_volume'
            )
        ]
    ]
)

show_report_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Показать расчет потерь', callback_data='show_report'
            )
        ]
    ]
)
