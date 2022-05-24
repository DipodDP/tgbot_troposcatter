from os import remove

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, CallbackQuery

from tgbot.services.calculation_report import calc_report
from tgbot.keyboards import reply, inline
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import CalcMenuStates
from tgbot.services.async_get_sites import path_sites


@rate_limit(1, key=reply.btn_next.text)
async def btn_next_handler(message: Message, state: FSMContext):
    curr_state = await state.get_state('CalcMenuStates')

    if curr_state == 'CalcMenuStates:s_names':
        await message.answer('Введите координаты точек:')
        await CalcMenuStates.s_coords.set()

    elif curr_state == 'CalcMenuStates:got_s_names':
        async with state.proxy() as data:
            s_names: list = data['s_names']
            # Если точки были переданы в одном сообщении, то разделяю их по разделителям, если они есть
            if len(s_names) == 1:
                s_names = s_names[0].split(';')
            if len(s_names) == 1:
                s_names = s_names[0].split(',')
            if len(s_names) == 1:
                s_names = s_names[0].split(' — ')
            if len(s_names) == 1:
                s_names = s_names[0].split(' - ')
            # Если разделителей нет, то разделяю их по " "
            if len(s_names) == 1:
                s_names = s_names[0].split(' ')
                data['s_names'] = s_names
            # У переданных точек заменяем " " на "_" в названии точки
            else:
                for i in range(len(s_names)):
                    s_names[i] = s_names[i].removeprefix(' ')
                    s_names[i] = s_names[i].replace(' ', '_')
                data['s_names'] = s_names

        try:
            if len(s_names) == 1:
                with open(path_sites(f'{s_names[0]} Точка Б.trlc'), 'r') as f:
                    f.close()
            else:
                with open(path_sites(f'{s_names[0]} {s_names[1]}.trlc'), 'r') as f:
                    f.close()
            await message.bot.send_message(message.chat.id,
                                           "Нашел координаты этих точек!"
                                           " Использовать или удалить эти координаты?",
                                           reply_markup=inline.use_file)
        except FileNotFoundError:
            await message.answer("Сохраненные данные для этих точек не найдены."
                                 " Введите координаты точек: ")
            await CalcMenuStates.s_coords.set()

    elif curr_state == 'CalcMenuStates:s_coords':
        await message.answer('Нажмите кнопку ' + reply.btn_next.text + ' для начала расчета',
                             reply_markup=reply.calc_t_menu)
        await CalcMenuStates.got_s_coords.set()

    elif curr_state == 'CalcMenuStates:got_s_coords':
        await message.answer('Рассчитываю трассу...')
        await CalcMenuStates.got_s_coords.set()
        await calc_report(message, state)


@rate_limit(1, key=reply.btn_back.text)
async def btn_back_handler(message: Message, state: FSMContext):
    curr_state = await state.get_state()

    if curr_state == 'CalcMenuStates:s_names':
        await state.finish()
        await message.answer('Главное меню: ', reply_markup=reply.main_menu)

    elif curr_state == 'CalcMenuStates:got_s_names' or curr_state == 'CalcMenuStates:s_coords':
        async with state.proxy() as data:
            data['s_names'] = []
            data['s_coords'] = []
        await CalcMenuStates.s_names.set()
        await message.answer('Введите названия точек заново: ')

    elif curr_state == 'CalcMenuStates:got_s_coords':
        async with state.proxy() as data:
            data['s_coords'] = []
        await CalcMenuStates.s_coords.set()
        await message.answer('Введите координаты точек заново: ')


async def use_del_file(call: CallbackQuery, state: FSMContext):
    if call.data == 'use_file':
        await call.bot.send_message(
            call.message.chat.id,
            "Использую сохраненые координаты. \nНажмите кнопку " + reply.btn_next.text +
            ' для начала расчета, ' + ' или ' + reply.btn_back.text +
            " для ввода новых координат этих точек",
            reply_markup=reply.calc_t_menu
        )
        await call.message.edit_reply_markup()
        await CalcMenuStates.got_s_coords.set()

    elif call.data == 'del_file':
        data = await state.get_data()
        s_names = data['s_names']
        try:
            if len(s_names) == 1:
                remove(path_sites(f'{s_names[0]} Точка Б.trlc'))
                remove(path_sites(f'{s_names[0]} Точка Б.path'))
                remove(path_sites(f'{s_names[0]} Точка Б.png'))
            else:
                remove(path_sites(f'{s_names[0]} {s_names[1]}.trlc'))
                remove(path_sites(f'{s_names[0]} {s_names[1]}.path'))
                remove(path_sites(f'{s_names[0]} {s_names[1]}.png'))
            await call.bot.send_message(call.message.chat.id, "Сохраненые координаты удалены."
                                                              " Введите координаты точек: ")
        except FileNotFoundError:
            await call.bot.send_message(call.message.chat.id, "Ошибка удаления."
                                                              " Введите координаты точек: ")

        await call.message.edit_reply_markup()
        await CalcMenuStates.s_coords.set()


def register_calc_t_menu_buttons(dp: Dispatcher):
    dp.register_message_handler(btn_next_handler, ChatTypeFilter(types.ChatType.PRIVATE),
                                text=reply.btn_next.text, state=CalcMenuStates)

    dp.register_message_handler(btn_back_handler, ChatTypeFilter(types.ChatType.PRIVATE),
                                text=reply.btn_back.text, state=CalcMenuStates)

    dp.register_callback_query_handler(use_del_file, ChatTypeFilter(types.ChatType.PRIVATE),
                                       state=CalcMenuStates.got_s_names)
