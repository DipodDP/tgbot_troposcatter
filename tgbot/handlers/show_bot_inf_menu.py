from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message

from tgbot.keyboards.reply import bot_inf_menu, btn_back, main_menu, btn_bot_inf, btn_show_bot_inf
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import BotInfMenuStates


@rate_limit(5, key=btn_show_bot_inf.text)
async def show_bot_inf_menu(message: Message):
    await message.answer('Что хотите узнать?', reply_markup=bot_inf_menu)
    await BotInfMenuStates.bot_inf_state.set()


@rate_limit(5, key=btn_bot_inf.text)
async def bot_inf(message: Message):
    await message.answer('Здесь будет инфа обо мне', reply_markup=bot_inf_menu)
    await message.bot.send_sticker(message.chat.id,
                                   'CAACAgIAAxkBAAMRYj7tTaXGWTKSBxdW6mtoSDRwyTIAAioAA7SEmBj9IhaQyPilryME')


async def bot_inf_back(message: Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=main_menu)
    await state.finish()


def register_show_bot_inf_menu(dp: Dispatcher):
    dp.register_message_handler(show_bot_inf_menu, ChatTypeFilter(types.ChatType.PRIVATE), text=btn_show_bot_inf.text,
                                state='*')
    dp.register_message_handler(bot_inf, ChatTypeFilter(types.ChatType.PRIVATE), text=btn_bot_inf.text,
                                state=BotInfMenuStates.bot_inf_state)
    dp.register_message_handler(bot_inf_back, ChatTypeFilter(types.ChatType.PRIVATE), text=btn_back.text,
                                state=BotInfMenuStates.bot_inf_state)
