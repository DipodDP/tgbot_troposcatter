from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import CallbackQuery, Message

from tgbot.handlers.calc_t_menu_buttons import btn_next_handler
from tgbot.i18n import t_bot
from tgbot.keyboards import reply, inline
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import CalcMenuStates


@rate_limit(5, key='calc_t')
async def calc_t_menu(message: Message, state: FSMContext = '*', lang: str = 'en'):
    await state.finish()
    async with state.proxy() as data:
        data['s_names'] = []
        data['s_coords'] = []
        data['lang'] = lang
    await message.bot.send_message(
        message.chat.id,
        t_bot('enter_site_names', lang),
        reply_markup=reply.get_calc_t_menu(lang),
    )
    await CalcMenuStates.s_names.set()


async def calc_t_menu_s_names_get(message: Message, state: FSMContext, lang: str = 'en'):
    async with state.proxy() as data:
        data['s_names']: list = data['s_names'] + [message.text]
    await message.bot.send_message(
        message.chat.id,
        t_bot('add_another_site', lang),
        reply_markup=inline.get_add_names_keyboard(lang),
    )


async def add_names(call: CallbackQuery, state: FSMContext, lang: str = 'en'):
    if call.data == 'yes_names':
        await call.message.edit_reply_markup()  # remove buttons from last message
        await call.message.answer(t_bot('enter_next_site_name', lang))
        await CalcMenuStates.s_names.set()
    elif call.data == 'no_names':
        await call.message.edit_reply_markup()
        await CalcMenuStates.next()
        await btn_next_handler(call.message, state, lang=lang)


async def calc_t_menu_s_coords_get(message: Message, state: FSMContext, lang: str = 'en'):
    async with state.proxy() as data:
        data['s_coords'] = data['s_coords'] + [message.text]
    await message.answer(
        t_bot('add_next_coords', lang),
        reply_markup=inline.get_add_coords_keyboard(lang),
    )


async def add_coords(call: CallbackQuery, state: FSMContext, lang: str = 'en'):
    if call.data == 'yes_coords':
        await call.message.edit_reply_markup()
        await call.message.answer(t_bot('enter_next_coords', lang))
        await CalcMenuStates.s_coords.set()
    elif call.data == 'no_coords':
        await call.message.edit_reply_markup()
        btn_next = t_bot('btn_next', lang)
        await call.message.answer(
            t_bot('coords_entered_default_heights', lang, btn_next=btn_next),
            reply_markup=reply.get_calc_t_menu(lang),
        )
        await call.message.answer(
            t_bot('or_set_heights', lang),
            reply_markup=inline.get_offer_set_heights_keyboard(lang),
        )
        await CalcMenuStates.got_s_coords.set()


def register_calc_t_menu_sites(dp: Dispatcher):
    dp.register_message_handler(
        calc_t_menu,
        ChatTypeFilter(types.ChatType.PRIVATE),
        text=reply.ALL_BTN_CALC_T,
        state='*',
    )
    dp.register_message_handler(
        calc_t_menu_s_names_get,
        ChatTypeFilter(types.ChatType.PRIVATE),
        state=CalcMenuStates.s_names,
    )
    dp.register_message_handler(
        calc_t_menu_s_coords_get,
        ChatTypeFilter(types.ChatType.PRIVATE),
        state=CalcMenuStates.s_coords,
    )

    dp.register_callback_query_handler(
        add_names, ChatTypeFilter(types.ChatType.PRIVATE), state=CalcMenuStates.s_names
    )
    dp.register_callback_query_handler(
        add_coords,
        ChatTypeFilter(types.ChatType.PRIVATE),
        state=CalcMenuStates.s_coords,
    )
