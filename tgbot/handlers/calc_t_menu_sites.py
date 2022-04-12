from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import CallbackQuery, Message

from tgbot.handlers.calc_t_menu_buttons import btn_next_handler
from tgbot.keyboards import reply, inline
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import CalcMenuStates


@rate_limit(5, key=reply.btn_calc_t.text)
async def calc_t_menu(message: Message, state: FSMContext = '*'):
    async with state.proxy() as data:
        data['s_names'] = []
        data['s_coords'] = []
    await message.bot.send_message(message.chat.id, 'Введите названия точек: ', reply_markup=reply.calc_t_menu)
    await CalcMenuStates.s_names.set()


async def calc_t_menu_s_names_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['s_names']: list = data['s_names'] + [message.text]
    await message.bot.send_message(message.chat.id, "Добавить еще точку?", reply_markup=inline.add_names)


async def add_names(call: CallbackQuery, state: FSMContext):
    if call.data == 'yes_names':
        await call.message.edit_reply_markup()  # удаляем кнопки у последнего сообщения
        await call.message.answer("Введите название следующей точки:")
        await CalcMenuStates.s_names.set()
    elif call.data == 'no_names':
        await call.message.edit_reply_markup()
        await CalcMenuStates.next()
        await btn_next_handler(call.message, state)


async def calc_t_menu_s_coords_get(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['s_coords'] = data['s_coords'] + [message.text]
    await message.answer('Добавить координаты следующей точки?', reply_markup=inline.add_coords)


async def add_coords(call: CallbackQuery, state: FSMContext):
    if call.data == 'yes_coords':
        await call.message.edit_reply_markup()
        await call.message.answer("Введите координаты следующей точки:")
        await CalcMenuStates.s_coords.set()
    elif call.data == 'no_coords':
        await call.message.edit_reply_markup()
        # await CalcMenuStates.next()
        await btn_next_handler(call.message, state)


def register_calc_t_menu_sites(dp: Dispatcher):
    dp.register_message_handler(calc_t_menu, ChatTypeFilter(types.ChatType.PRIVATE), text=reply.btn_calc_t.text,
                                state='*')
    dp.register_message_handler(calc_t_menu_s_names_get, ChatTypeFilter(types.ChatType.PRIVATE),
                                state=CalcMenuStates.s_names)
    dp.register_message_handler(calc_t_menu_s_coords_get, ChatTypeFilter(types.ChatType.PRIVATE),
                                state=CalcMenuStates.s_coords)

    dp.register_callback_query_handler(add_names, ChatTypeFilter(types.ChatType.PRIVATE),
                                       state=CalcMenuStates.s_names)
    dp.register_callback_query_handler(add_coords, ChatTypeFilter(types.ChatType.PRIVATE),
                                       state=CalcMenuStates.s_coords)
