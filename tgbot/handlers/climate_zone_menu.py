from pathlib import Path

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, ChatType, InputFile
from aiogram.utils.exceptions import BadRequest
from aiogram.utils.markdown import text, code

from tgbot.config import Config
from tgbot.i18n import t_bot
from tgbot.keyboards.reply import (
    get_climate_zone_menu,
    get_main_menu,
    ALL_BTN_SHOW_CLIMATE_ZONE,
    ALL_BTN_BACK,
    ALL_BTN_CLIMATE_ZONES,
)
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import ClimateZoneMenuStates


@rate_limit(5, key='show_climate_zone')
async def show_climate_zone(message: Message, state: FSMContext, lang: str = 'en'):
    await message.answer(
        t_bot('climate_zone_info', lang),
        reply_markup=get_climate_zone_menu(lang),
    )
    await ClimateZoneMenuStates.climate_zone_state.set()


@rate_limit(5, key='climate_zones')
async def climate_zones(message: Message, lang: str = 'en'):
    config: Config = message.bot.get('config')

    try:
        m = await message.bot.send_document(
            message.chat.id,
            config.misc.c_zones_file_id,
            caption=t_bot('climate_map_caption', lang),
        )
        file_id = m.document.file_id

    except BadRequest:
        file = InputFile(Path(Path.cwd(), 'tgbot', 'services', 'climate_zones.pdf'))
        msg_doc = await message.bot.send_document(
            message.chat.id, file, caption=t_bot('climate_map_caption', lang)
        )
        file_id = msg_doc.document.file_id
        config.misc.c_zones_file_id = file_id

        with open('.env', 'r+t') as f:
            s = '?'
            while s != '':
                n = f.tell()
                s = f.readline()
                try:
                    key, value = s.split('=')
                    if key == 'CLIMATE_ZONES_FILE_ID':
                        f.seek(n)
                        f.write(f'CLIMATE_ZONES_FILE_ID={file_id}')
                except ValueError:
                    pass

        msg_file_id = text(code(file_id)).replace('\\', '')
        await message.answer(
            t_bot('file_id_saved', lang, file_id=msg_file_id),
            parse_mode='Markdown',
        )


async def climate_zone_back(message: Message, state: FSMContext, lang: str = 'en'):
    await message.answer(t_bot('main_menu_label', lang), reply_markup=get_main_menu(lang))
    await state.finish()


def register_climate_zone_menu(dp: Dispatcher):
    dp.register_message_handler(
        show_climate_zone,
        ChatTypeFilter(ChatType.PRIVATE),
        text=ALL_BTN_SHOW_CLIMATE_ZONE,
        state='*',
    )
    dp.register_message_handler(
        climate_zones,
        ChatTypeFilter(ChatType.PRIVATE),
        text=ALL_BTN_CLIMATE_ZONES,
        state=ClimateZoneMenuStates.climate_zone_state,
    )
    dp.register_message_handler(
        climate_zone_back,
        ChatTypeFilter(ChatType.PRIVATE),
        text=ALL_BTN_BACK,
        state=ClimateZoneMenuStates.climate_zone_state,
    )
