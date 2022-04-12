from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(text='Option 1')
        ],
        [
            KeyboardButton(text='Option 2'),
            KeyboardButton(text='Option 3'),

        ],
    ],
    resize_keyboard=True
)
