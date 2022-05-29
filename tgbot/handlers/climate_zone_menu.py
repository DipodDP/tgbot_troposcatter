from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, document, InputFile

from tgbot.keyboards.reply import climate_zone_menu, btn_show_climate_zone, btn_back, main_menu, btn_climate_zones
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import ClimateZoneMenuStates


@rate_limit(5, key=btn_show_climate_zone.text)
async def show_climate_zone(message: Message, state: FSMContext):
    await message.answer('Здесь можно скачать карту климатических зон в формате .PDF:)', reply_markup=climate_zone_menu)
    await ClimateZoneMenuStates.climate_zone_state.set()


@rate_limit(50, key=btn_climate_zones.text)
async def climate_zones(message: Message):

    await message.bot.send_document(message.chat.id,"BQACAgIAAxkBAAIVVGKTWDFj2uimlJ_BXuVBJPKmF83gAAJyFAACPqKYSLSGMBwSO9OsJAQ",
                                    caption='Карта климатических зон'
                                    )


async def climate_zone_back(message: Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=main_menu)
    await state.finish()


def register_climate_zone_menu(dp: Dispatcher):
    dp.register_message_handler(show_climate_zone, ChatTypeFilter(types.ChatType.PRIVATE),
                                text=btn_show_climate_zone.text, state='*')
    dp.register_message_handler(climate_zones, ChatTypeFilter(types.ChatType.PRIVATE), text=btn_climate_zones.text,
                                state=ClimateZoneMenuStates.climate_zone_state)
    dp.register_message_handler(climate_zone_back, ChatTypeFilter(types.ChatType.PRIVATE), text=btn_back.text,
                                state=ClimateZoneMenuStates.climate_zone_state)
