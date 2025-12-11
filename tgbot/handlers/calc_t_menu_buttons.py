import logging
from os import remove

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.types import Message, CallbackQuery

from tgbot.services.calculation_report import calc_report
from tgbot.keyboards import reply, inline
from tgbot.misc.rate_limit import rate_limit
from tgbot.misc.states import CalcMenuStates
from trace_calc.async_get_sites import path_sites

logger = logging.getLogger(__name__)


@rate_limit(1, key=reply.btn_next.text)
async def btn_next_handler(message: Message, state: FSMContext):
    curr_state = await state.get_state()

    if curr_state == 'CalcMenuStates:s_names':
        await message.answer('Введите координаты точек:')
        await CalcMenuStates.s_coords.set()

    elif curr_state == 'CalcMenuStates:got_s_names':
        async with state.proxy() as data:
            s_names: list = data['s_names']
            if len(s_names) == 1:
                s_names = s_names[0].split('\n')
            if len(s_names) == 1:
                s_names = s_names[0].split(';')
            if len(s_names) == 1:
                s_names = s_names[0].split(',')
            if len(s_names) == 1:
                s_names = s_names[0].split(' — ')
            if len(s_names) == 1:
                s_names = s_names[0].split(' - ')
            if len(s_names) == 1:
                s_names = s_names[0].split(' ')
                data['s_names'] = s_names
            for i in range(len(s_names)):
                s_names[i] = s_names[i].removeprefix(' ')
                s_names[i] = s_names[i].replace(' ', '_')
            data['s_names'] = s_names

        try:
            if len(s_names) == 1:
                with open(path_sites(f'{s_names[0]} Точка Б.path'), 'r') as f:
                    f.close()
            else:
                with open(path_sites(f'{s_names[0]} {s_names[1]}.path'), 'r') as f:
                    f.close()
            await message.bot.send_message(
                message.chat.id,
                'Нашел координаты этих точек! Использовать или удалить эти координаты?',
                reply_markup=inline.use_file,
            )
        except FileNotFoundError:
            await message.answer(
                'Сохраненные данные для этих точек не найдены. Введите координаты точек: '
            )
            await CalcMenuStates.s_coords.set()

    elif curr_state == 'CalcMenuStates:got_s_coords':
        async with state.proxy() as data:
            data['s_heights'] = [2.0, 2.0]
        await message.answer('Рассчитываю трассу с высотами по умолчанию...')
        await calc_report(message, state)

    elif curr_state == 'CalcMenuStates:got_s_heights':
        await message.answer('Рассчитываю трассу...')
        await calc_report(message, state)


async def set_custom_heights_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_reply_markup()  # remove inline button
    async with state.proxy() as data:
        data['s_heights'] = []
        s_names = data.get('s_names', ['первой', 'второй'])
        site_name = s_names[0] if s_names else 'первой'
    await call.message.answer(
        f'Введите высоту подвеса антенны для точки "{site_name}" (в метрах):'
    )
    await CalcMenuStates.s_heights.set()


async def calc_t_menu_s_heights_get(message: Message, state: FSMContext):
    try:
        height = int(message.text)
        if not (0 < height < 1000):
            raise ValueError
    except (ValueError, TypeError):
        await message.answer(
            'Некорректное значение. Пожалуйста, введите высоту в метрах (целое число от 1 до 999).'
        )
        return

    async with state.proxy() as data:
        if 's_heights' not in data:
            data['s_heights'] = []
        data['s_heights'].append(height)
        s_names = data.get('s_names', ['первой', 'второй'])
        if len(data['s_heights']) == 1:
            site_name = s_names[1] if len(s_names) > 1 else 'второй'
            await message.answer(
                f'Введите высоту подвеса антенны для точки "{site_name}" (в метрах):'
            )
            await CalcMenuStates.s_heights.set()
        else:
            await message.answer(
                'Нажмите кнопку ' + reply.btn_next.text + ' для начала расчета',
                reply_markup=reply.calc_t_menu,
            )
            await CalcMenuStates.got_s_heights.set()


@rate_limit(1, key=reply.btn_back.text)
async def btn_back_handler(message: Message, state: FSMContext):
    curr_state = await state.get_state()

    if curr_state in ['CalcMenuStates:s_names', 'CalcMenuStates:got_s_coords']:
        await state.finish()
        await message.answer('Главное меню: ', reply_markup=reply.main_menu)

    elif curr_state in ['CalcMenuStates:got_s_names', 'CalcMenuStates:s_coords']:
        async with state.proxy() as data:
            data['s_names'] = []
            data['s_coords'] = []
        await CalcMenuStates.s_names.set()
        await message.answer('Введите названия точек заново: ')

    elif curr_state == 'CalcMenuStates:s_heights':
        async with state.proxy() as data:
            if not data.get('s_heights'):
                await message.answer(
                    'Координаты введены. Нажмите "'
                    + reply.btn_next.text
                    + '" для расчета с высотами по умолчанию (2м).',
                    reply_markup=reply.calc_t_menu,
                )
                await message.answer(
                    'Или задайте свои высоты.', reply_markup=inline.offer_set_heights
                )
                await CalcMenuStates.got_s_coords.set()
            else:
                data['s_heights'] = []
                s_names = data.get('s_names', ['первой', 'второй'])
                site_name = s_names[0] if s_names else 'первой'
                await message.answer(
                    f'Введите высоту подвеса антенны для точки "{site_name}" (в метрах):'
                )

    elif curr_state == 'CalcMenuStates:got_s_heights':
        async with state.proxy() as data:
            data['s_heights'] = []
        s_names = data.get('s_names', ['первой', 'второй'])
        site_name = s_names[0] if s_names else 'первой'
        await CalcMenuStates.s_heights.set()
        await message.answer(
            f'Введите высоту подвеса антенны для точки "{site_name}" (в метрах):'
        )


async def use_del_file(call: CallbackQuery, state: FSMContext):
    if call.data == 'use_file':
        await call.message.edit_reply_markup()
        await call.message.answer(
            'Использую сохраненные координаты. Нажмите "'
            + reply.btn_next.text
            + '" для расчета с высотами по умолчанию (2м).',
            reply_markup=reply.calc_t_menu,
        )
        await call.message.answer(
            'Или задайте свои высоты.', reply_markup=inline.offer_set_heights
        )
        await CalcMenuStates.got_s_coords.set()

    elif call.data == 'del_file':
        data = await state.get_data()
        s_names = data['s_names']
        path_name = (
            f'{s_names[0]} {s_names[1]}'
            if len(s_names) > 1
            else f'{s_names[0]} Точка Б'
        )
        path_file = path_sites(f'{path_name}.path')
        png_file = path_sites(f'{path_name}.png')
        try:
            logger.debug(f'Deleting path file: {path_file}')
            remove(path_file)
            try:
                logger.debug(f'Deleting png file: {png_file}')
                remove(png_file)
            except FileNotFoundError:
                logger.debug(f'PNG file not found, skipping: {png_file}')
        except FileNotFoundError:
            logger.error(f'Could not find path file to delete: {path_file}')
            await call.bot.send_message(
                call.message.chat.id, 'Ошибка удаления. Введите координаты точек: '
            )
        else:
            await call.bot.send_message(
                call.message.chat.id,
                'Сохраненые координаты удалены. Введите координаты точек: ',
            )

        await call.message.edit_reply_markup()
        await CalcMenuStates.s_coords.set()


def register_calc_t_menu_buttons(dp: Dispatcher):
    dp.register_message_handler(
        btn_next_handler,
        ChatTypeFilter(types.ChatType.PRIVATE),
        text=reply.btn_next.text,
        state=CalcMenuStates,
    )
    dp.register_message_handler(
        btn_back_handler,
        ChatTypeFilter(types.ChatType.PRIVATE),
        text=reply.btn_back.text,
        state=CalcMenuStates,
    )
    dp.register_callback_query_handler(
        use_del_file,
        ChatTypeFilter(types.ChatType.PRIVATE),
        state=CalcMenuStates.got_s_names,
    )
    dp.register_callback_query_handler(
        set_custom_heights_handler,
        ChatTypeFilter(types.ChatType.PRIVATE),
        lambda c: c.data == 'set_custom_heights',
        state=CalcMenuStates.got_s_coords,
    )
    dp.register_message_handler(
        calc_t_menu_s_heights_get,
        ChatTypeFilter(types.ChatType.PRIVATE),
        state=CalcMenuStates.s_heights,
    )
