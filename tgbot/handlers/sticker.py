from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, ContentType

from tgbot.misc.rate_limit import rate_limit


@rate_limit(5)
async def get_sticker_id(message: Message):
    sticker_id = message.sticker.file_id
    await message.answer(f'Вот id твоего стикера\n'
                         f'{sticker_id}')


def register_sticker(dp: Dispatcher):
    dp.register_message_handler(get_sticker_id, ChatTypeFilter(types.ChatType.PRIVATE),
                                content_types=ContentType.STICKER)
