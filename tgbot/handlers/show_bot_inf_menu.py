from os import listdir

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, ChatType
from aiogram.utils.markdown import code, text

from tgbot.keyboards.reply import bot_inf_menu, btn_back, main_menu, btn_bot_inf, btn_show_bot_inf, btn_saved_sites, \
    btn_like
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import BotInfMenuStates
from tgbot.services.async_get_sites import path_sites


@rate_limit(5, key=btn_show_bot_inf.text)
async def show_bot_inf_menu(message: Message):
    await message.answer('Что хотите узнать?', reply_markup=bot_inf_menu)
    await BotInfMenuStates.bot_inf_state.set()


@rate_limit(5, key=btn_saved_sites.text)
async def saved_sites(message: Message):
    await message.answer('Я знаю координаты точек для этих трасс:')
    files = listdir(path_sites(''))
    sites = list(filter(lambda x: x.endswith('.trlc'), files))
    sites.sort()

    try:
        sites.remove("Точка А Точка Б.trlc")
    except ValueError:
        pass

    for i in range(len(sites)):
        sites[i] = sites[i].replace('.trlc', "")
        sites[i] = sites[i].replace(' ', " — ")
        sites[i] = sites[i].replace('_', " ")
        sites[i] = text('\n', code(sites[i]), '\n')
        sites[i] = sites[i].replace("\\-", "-")
        sites[i] = sites[i].replace("\\.", ".")

    msg_text = ''.join(sites)
    await message.bot.send_message(message.chat.id, msg_text, 'Markdown')


@rate_limit(5, key=btn_bot_inf.text)
async def bot_inf(message: Message):
    with open('README.md') as f:
        text_info = f.read()
    await message.answer(text_info, disable_web_page_preview=True, reply_markup=bot_inf_menu)
    await message.bot.send_sticker(message.chat.id,
                                   'CAACAgIAAxkBAAMRYj7tTaXGWTKSBxdW6mtoSDRwyTIAAioAA7SEmBj9IhaQyPilryME')


@rate_limit(5, key=btn_like.text)
async def like(message: Message):
    await message.answer('Спасибо:)')
    await message.bot.send_sticker(message.chat.id,
                                   'CAACAgIAAxkBAAIDf2I0sruXeS-rJxeSNhmhjXBp0B93AAIfAANZu_wl6jl0G9k9NpkjBA')
    with open('tgbot/like.cnt', 'r') as f:
        c = int(f.read())
        c += 1
    with open('tgbot/like.cnt', 'w') as f:
        f.write(str(c))


async def bot_inf_back(message: Message, state: FSMContext):
    await message.answer('Главное меню', reply_markup=main_menu)
    await state.finish()


def register_show_bot_inf_menu(dp: Dispatcher):
    dp.register_message_handler(show_bot_inf_menu, ChatTypeFilter(ChatType.PRIVATE), text=btn_show_bot_inf.text,
                                state='*')
    dp.register_message_handler(saved_sites, ChatTypeFilter(ChatType.PRIVATE), text=btn_saved_sites.text,
                                state=BotInfMenuStates.bot_inf_state)
    dp.register_message_handler(bot_inf, ChatTypeFilter(ChatType.PRIVATE), text=btn_bot_inf.text,
                                state=BotInfMenuStates.bot_inf_state)
    dp.register_message_handler(like, ChatTypeFilter(ChatType.PRIVATE), text=btn_like.text,
                                state=BotInfMenuStates.bot_inf_state)
    dp.register_message_handler(bot_inf_back, ChatTypeFilter(ChatType.PRIVATE), text=btn_back.text,
                                state=BotInfMenuStates.bot_inf_state)
