from aiogram import Dispatcher
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, ContentType, ChatType
from aiogram.utils.markdown import text, code


async def get_file_id(message: Message):
    file_id = text(code(message.document.file_id)).replace("\\", "")
    await message.answer(f'Вот id твоего файла:\n'
                         f'{file_id}', parse_mode='Markdown',)


def register_file(dp: Dispatcher):
    dp.register_message_handler(get_file_id, ChatTypeFilter(ChatType.PRIVATE), content_types=ContentType.DOCUMENT)