from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message


async def bad_words(message: Message):
    await message.reply("Фу таким быть")


async def unkw_text(message: Message):
    await message.reply("Неизвестная команда")


def register_user(dp: Dispatcher):
    dp.register_message_handler(bad_words, bad_words=True, state="*")
    dp.register_message_handler(unkw_text, ChatTypeFilter(types.ChatType.PRIVATE), state="*")
