from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message

from tgbot.i18n import t_bot


async def bad_words_ru(message: Message, lang: str = 'en'):
    await message.reply(t_bot('bad_words_ru', lang))


async def bad_words_en(message: Message):
    await message.reply("Wash your mouth with soap, please! 🤢🧼")


async def unkw_text(message: Message, lang: str = 'en'):
    await message.reply(t_bot('unknown_command', lang))


def register_wrong(dp: Dispatcher):
    dp.register_message_handler(bad_words_ru, bad_words_ru=True, state="*")
    dp.register_message_handler(bad_words_en, bad_words_en=True, state="*")
    dp.register_message_handler(unkw_text, ChatTypeFilter(types.ChatType.PRIVATE), state="*")
