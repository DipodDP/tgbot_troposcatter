import logging

from aiogram import Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from tgbot.keyboards.reply import main_menu
from tgbot.models.models import User


async def admin_start(message: Message, mware_data, user: User):
    await message.reply(f"Hello, admin! It's tropobot.\n {mware_data=}",
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text="Just button", callback_data='Button')
                                ]
                            ]
                        ))
    await message.reply('Troposcatter calculation', reply_markup=main_menu)
    logging.info(f'6. handler')
    logging.info(f'Next: post process message')

    return {"from_handler": "data from handler"}


async def get_button(call: CallbackQuery):
    await call.message.answer('You pressed the button')


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_callback_query_handler(get_button, text='Button', state="*", is_admin=True)
