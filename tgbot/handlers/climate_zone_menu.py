from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message

from tgbot.keyboards.reply import climate_zone_menu, btn_show_climate_zone, btn_like, btn_back, main_menu
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import ClimateZoneMenuStates


@rate_limit(5, key=btn_show_climate_zone.text)
async def show_climate_zone(message: Message, state: FSMContext):
    await message.answer('Пока не знаю как это сделать, но можешь поставить лайк:)', reply_markup=climate_zone_menu)
    await ClimateZoneMenuStates.climate_zone_state.set()


@rate_limit(5, key=btn_like.text)
async def like(message: Message):
    await message.answer('Спасибо:)')
    await message.bot.send_sticker(message.chat.id,
                                   'CAACAgIAAxkBAAIDf2I0sruXeS-rJxeSNhmhjXBp0B93AAIfAANZu_wl6jl0G9k9NpkjBA')


async def climate_zone_back(message: Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=main_menu)
    await state.finish()


def register_climate_zone_menu(dp: Dispatcher):
    dp.register_message_handler(show_climate_zone, ChatTypeFilter(types.ChatType.PRIVATE),
                                text=btn_show_climate_zone.text, state='*')
    dp.register_message_handler(like, ChatTypeFilter(types.ChatType.PRIVATE), text=btn_like.text,
                                state=ClimateZoneMenuStates.climate_zone_state)
    dp.register_message_handler(climate_zone_back, ChatTypeFilter(types.ChatType.PRIVATE), text=btn_back.text,
                                state=ClimateZoneMenuStates.climate_zone_state)
