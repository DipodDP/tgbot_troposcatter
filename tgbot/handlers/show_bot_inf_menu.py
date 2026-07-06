from os import listdir

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, ChatType
from aiogram.utils.markdown import code, text

from tgbot.i18n import t_bot
from tgbot.keyboards.reply import (
    get_bot_inf_menu,
    get_main_menu,
    ALL_BTN_BACK,
    ALL_BTN_BOT_INF,
    ALL_BTN_SHOW_BOT_INF,
    ALL_BTN_SAVED_SITES,
    ALL_BTN_LIKE,
)
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import BotInfMenuStates
from trace_calc.async_get_sites import path_sites


async def get_saved_sites(message: Message, lang: str = 'en') -> str:
    await message.answer(t_bot('know_coords_for', lang))
    files = listdir(path_sites(''))
    sites = list(filter(lambda x: x.endswith('.path'), files))
    sites.sort()

    try:
        sites.remove('Точка А Точка Б.path')
    except ValueError:
        pass

    for i in range(len(sites)):
        sites[i] = sites[i].replace('.path', '')
        sites[i] = sites[i].replace(' ', ' — ')
        sites[i] = sites[i].replace('_', ' ')
        sites[i] = text('\n', code(sites[i]), '\n')
        sites[i] = sites[i].replace('\\-', '-')
        sites[i] = sites[i].replace('\\.', '.')

    msg_text = ''.join(sites)

    return msg_text


@rate_limit(5, key='show_bot_inf')
async def show_bot_inf_menu(message: Message, lang: str = 'en'):
    await message.answer(
        t_bot('what_to_know', lang), reply_markup=get_bot_inf_menu(lang)
    )
    await BotInfMenuStates.bot_inf_state.set()


@rate_limit(5, key='saved_sites')
async def saved_sites(message: Message, lang: str = 'en'):
    bot_mode = message.bot['config'].tg_bot.bot_mode

    match bot_mode:
        case 1:
            if message.from_id in message.bot['config'].tg_bot.admin_ids:
                msg_text = await get_saved_sites(message, lang)
            else:
                msg_text = t_bot('sites_list_hidden', lang)

        case _:
            msg_text = await get_saved_sites(message, lang)
    await message.bot.send_message(message.chat.id, msg_text, 'Markdown')


@rate_limit(5, key='bot_inf')
async def bot_inf(message: Message, lang: str = 'en'):
    bot_mode = message.bot['config'].tg_bot.bot_mode

    match bot_mode:
        case 0:
            with open('README.md') as f:
                text_info = f.read()
        case 1:
            with open('README_ru_s.md') as f:
                text_info = f.read()
        case _:
            text_info = t_bot('no_info', lang)

    await message.answer(
        text_info, disable_web_page_preview=True, reply_markup=get_bot_inf_menu(lang)
    )


@rate_limit(5, key='like')
async def like(message: Message, lang: str = 'en'):
    await message.answer(t_bot('thanks', lang))
    await message.bot.send_sticker(
        message.chat.id,
        'CAACAgIAAxkBAAIDf2I0sruXeS-rJxeSNhmhjXBp0B93AAIfAANZu_wl6jl0G9k9NpkjBA',
    )
    with open('tgbot/like.cnt', 'r') as f:
        c = int(f.read())
        c += 1
    with open('tgbot/like.cnt', 'w') as f:
        f.write(str(c))


async def bot_inf_back(message: Message, state: FSMContext, lang: str = 'en'):
    await message.answer(t_bot('main_menu_label', lang), reply_markup=get_main_menu(lang))
    await state.finish()


def register_show_bot_inf_menu(dp: Dispatcher):
    dp.register_message_handler(
        show_bot_inf_menu,
        ChatTypeFilter(ChatType.PRIVATE),
        text=ALL_BTN_SHOW_BOT_INF,
        state='*',
    )
    dp.register_message_handler(
        saved_sites,
        ChatTypeFilter(ChatType.PRIVATE),
        text=ALL_BTN_SAVED_SITES,
        state=BotInfMenuStates.bot_inf_state,
    )
    dp.register_message_handler(
        bot_inf,
        ChatTypeFilter(ChatType.PRIVATE),
        text=ALL_BTN_BOT_INF,
        state=BotInfMenuStates.bot_inf_state,
    )
    dp.register_message_handler(
        like,
        ChatTypeFilter(ChatType.PRIVATE),
        text=ALL_BTN_LIKE,
        state=BotInfMenuStates.bot_inf_state,
    )
    dp.register_message_handler(
        bot_inf_back,
        ChatTypeFilter(ChatType.PRIVATE),
        text=ALL_BTN_BACK,
        state=BotInfMenuStates.bot_inf_state,
    )
