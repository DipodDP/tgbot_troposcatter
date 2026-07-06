import logging

from aiogram import Dispatcher
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

from tgbot.i18n import t_bot
from tgbot.keyboards.reply import get_main_menu


async def admin_start(message: Message, mware_data: object, lang: str = 'en'):
    await message.reply(
        t_bot('admin_hello', lang, mware_data=str(mware_data)),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=t_bot('admin_button', lang), callback_data='Button')]
            ]
        ),
    )
    await message.reply(t_bot('admin_troposcatter_calc', lang), reply_markup=get_main_menu(lang))
    logging.debug('6. handler')
    logging.debug('Next: post process message')
    return {'from_handler': 'data from handler'}


async def stop_bot(message: Message, lang: str = 'en'):
    await message.reply(t_bot('admin_stopping', lang))
    dp = Dispatcher.get_current()
    await dp.stop_polling()


async def get_button(call: CallbackQuery, lang: str = 'en'):
    await call.answer(t_bot('admin_button_pressed', lang), show_alert=True, cache_time=1)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(
        admin_start, commands=['start'], state='*', is_admin=True
    )
    dp.register_message_handler(stop_bot, commands=['stop'], state='*', is_admin=True)
    dp.register_callback_query_handler(
        get_button, text='Button', state='*', is_admin=True
    )
