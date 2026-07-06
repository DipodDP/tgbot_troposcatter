from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, ContentType, ChatType
from aiogram.utils.markdown import text, code

from tgbot.i18n import t_bot
from tgbot.misc.rate_limit import rate_limit


@rate_limit(5)
async def get_sticker_id(message: Message, lang: str = 'en'):
    sticker_id = text(code(message.sticker.file_id)).replace("\\", "")
    await message.answer(
        t_bot('sticker_id', lang, sticker_id=sticker_id),
        parse_mode='Markdown',
    )


def register_sticker(dp: Dispatcher):
    dp.register_message_handler(
        get_sticker_id,
        ChatTypeFilter(ChatType.PRIVATE),
        content_types=ContentType.STICKER,
    )
