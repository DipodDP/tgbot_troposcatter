import logging

from aiogram import Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from tgbot.keyboards.reply import main_menu


async def admin_start(message: Message, mware_data):
    await message.reply(f"Hello, admin! It's tropobot.\n Press /stop to stop bot\n {mware_data=}",
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text="Just button", callback_data='Button')
                                ]
                            ]
                        ))
    await message.reply('Troposcatter calculation', reply_markup=main_menu)
    logging.debug(f'6. handler')
    logging.debug(f'Next: post process message')
    return {"from_handler": "data from handler"}


async def stop_bot(message: Message):
    await message.reply(f'Stopping bot...')
    await message.delete()
    exit()


async def get_button(call: CallbackQuery):
    await call.answer('You pressed the button', show_alert=True, cache_time=1)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
    dp.register_message_handler(stop_bot, commands=["stop"], state="*", is_admin=True)
    dp.register_callback_query_handler(get_button, text='Button', state="*", is_admin=True)
