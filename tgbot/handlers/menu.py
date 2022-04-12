from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter, Command, Text
from aiogram.types import Message, ReplyKeyboardRemove

from tgbot.keyboards.menu import menu


async def show_menu(message: Message):
    await message.answer("Choose option:", reply_markup=menu)


async def get_option1(message: Message):
    await message.answer("Option 1 has been chosen")


async def get_options(message: Message):
    await message.answer(f"Your choice: {message.text}", reply_markup=ReplyKeyboardRemove())


def register_menu(dp: Dispatcher):
    dp.register_message_handler(show_menu, ChatTypeFilter(types.ChatType.PRIVATE), Command('menu'), state="*")
    dp.register_message_handler(get_option1, ChatTypeFilter(types.ChatType.PRIVATE), text='Option 1', state="*")
    dp.register_message_handler(get_options, ChatTypeFilter(types.ChatType.PRIVATE),
                                Text(equals=['Option 2', 'Option 3']), state="*")
