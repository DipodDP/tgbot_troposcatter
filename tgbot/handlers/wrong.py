from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message


async def bad_words_ru(message: Message):
    await message.reply("Фу таким быть")


async def bad_words_en(message: Message):
    await message.reply("Wash your mouth with soap, please! 🤢🧼")


async def unkw_text(message: Message):
    await message.reply("Неизвестная команда")


def register_wrong(dp: Dispatcher):
    dp.register_message_handler(bad_words_ru, bad_words_ru=True, state="*")
    dp.register_message_handler(bad_words_en, bad_words_en=True, state="*")
    dp.register_message_handler(unkw_text, ChatTypeFilter(types.ChatType.PRIVATE), state="*")
