from pathlib import Path

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, ChatType, InputFile
from aiogram.utils.exceptions import BadRequest
from aiogram.utils.markdown import text, code

from tgbot.config import Config
from tgbot.keyboards.reply import climate_zone_menu, btn_show_climate_zone, btn_back, main_menu, btn_climate_zones
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import ClimateZoneMenuStates


@rate_limit(5, key=btn_show_climate_zone.text)
async def show_climate_zone(message: Message, state: FSMContext):
    await message.answer('Здесь можно скачать карту климатических зон в формате .PDF', reply_markup=climate_zone_menu)
    await ClimateZoneMenuStates.climate_zone_state.set()


@rate_limit(5, key=btn_climate_zones.text)
async def climate_zones(message: Message):
    config: Config = message.bot.get('config')

    try:
        m = await message.bot.send_document(message.chat.id, config.misc.c_zones_file_id,
                                            caption='Карта климатических зон')
        file_id = m.document.file_id

    except BadRequest:

        file = InputFile(Path(Path.cwd(), 'tgbot', 'services', 'climate_zones.pdf'))
        msg_doc = await message.bot.send_document(message.chat.id, file, caption='Карта климатических зон')
        file_id = msg_doc.document.file_id
        config.misc.c_zones_file_id = file_id

        with open(".env", "r+t") as f:
            s = '?'
            n1 = 0
            while s != '':
                n = f.tell()
                s = f.readline()
                try:
                    key, value = s.split('=')
                    if key == 'CLIMATE_ZONES_FILE_ID':
                        f.seek(n)
                        f.write(f"CLIMATE_ZONES_FILE_ID={file_id}")
                except ValueError:
                    pass

        msg_file_id = text(code(file_id)).replace("\\", "")
        await message.answer(f'Id файла сохранен для более быстрой загрузки.\n'
                             f'Id для переменной окружения CLIMATE\_ZONES\_FILE\_ID:\n{msg_file_id}',
                             parse_mode='Markdown')


async def climate_zone_back(message: Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=main_menu)
    await state.finish()


def register_climate_zone_menu(dp: Dispatcher):
    dp.register_message_handler(show_climate_zone, ChatTypeFilter(ChatType.PRIVATE),
                                text=btn_show_climate_zone.text, state='*')
    dp.register_message_handler(climate_zones, ChatTypeFilter(ChatType.PRIVATE), text=btn_climate_zones.text,
                                state=ClimateZoneMenuStates.climate_zone_state)
    dp.register_message_handler(climate_zone_back, ChatTypeFilter(ChatType.PRIVATE), text=btn_back.text,
                                state=ClimateZoneMenuStates.climate_zone_state)
