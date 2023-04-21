import datetime
import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message


from tgbot.keyboards.reply import main_menu
from tgbot.services.async_get_sites import get_sites, get_azim, path_sites
from tgbot.services.async_path_profiler import APIException
from tgbot.services.async_tropo import coords_analyzis_groza, coords_analyzis_sosnik


async def calc_report(message: Message, state: FSMContext):
    # для отладки вывод того, что получили в calc_t_menu:
    # data = await state.get_data()
    # s_names = data.get('s_names')
    # s_coords = data.get('s_coords')
    # await message.answer(f'Названия и координаты: {s_names}, {s_coords}')
    # # await  state.reset_state(with_data=False)
    # await state.finish()
    # await message.answer(f'Состояние: {await state.get_state()}', reply_markup=main_menu)
    bot_mode = message.bot['config'].tg_bot.bot_mode
    try:
        async with state.proxy() as data:
            data['s_names']: list
            data['s_coords']: list
            s_names = data['s_names']
            if not s_names:
                path = path_sites('Точка А Точка Б')
            elif len(s_names) == 1:
                path = path_sites(f'{s_names[0]} Точка Б')
            else:
                path = path_sites(f'{s_names[0]} {s_names[1]}')
            sites = await get_sites(' '.join(data['s_names']), ' '.join(data['s_coords']))

        sites = tuple(sites)
        s_name = sites[0]
        coords_dec = sites[1]
        coords = sites[2]

        await types.ChatActions.typing()
        await message.bot.send_message(message.from_user.id,
                                       text='Координаты точек: \n\n'
                                            + s_name[0] + ':\nШирота: ' + coords[0] + '\nДолгота: ' + coords[1] + '\n\n'
                                            + s_name[1] + ':\nШирота: ' + coords[2] + '\nДолгота: ' + coords[3])

        await types.ChatActions.typing()
        azim1, azim2, dec1, dec2, mazim1, mazim2 = await get_azim(coords_dec)
        azimuth = str(
            'Азимут на точку ' + s_name[1] + ': ' + str(azim1) + '°\n' +
            'Магнитное склонение: ' + str(dec1) + '°\n' +
            'Магнитный азимут на точку ' + s_name[1] + ': ' + str(mazim1) + '°\n' +
            '-----------------------------------------------\n' +
            'Азимут на точку ' + s_name[0] + ': ' + str(azim2) + '°\n' +
            'Магнитное склонение : ' + str(dec2) + '°\n' +
            'Магнитный азимут на точку ' + s_name[0] + ': ' + str(mazim2) + '°\n'
        )
        await message.bot.send_message(message.from_user.id, text=azimuth)

        await types.ChatActions.typing()

        print(f"{datetime.datetime.now()} {s_name[0]} - {s_name[1]}")

        if bot_mode == 0:
            
            L0, Lmed, Lr, trace_dist, b1_max, b2_max, b_sum, \
            Ltot, dL, speed, sp_pref = await coords_analyzis_groza(
                coords_dec[0:2], coords_dec[2:4], 0, str(path), bot_mode
            )

            await message.bot.send_message(message.from_user.id, text=
            f'''Протяженность трассы = {trace_dist:.1f} км
Угол закрытия {s_name[0]} = {b1_max:.2f}°
Угол закрытия {s_name[1]} = {b2_max:.2f}°
Суммарный угол закрытия = {b_sum:.2f}°

Потери:
L0 = {L0:.1f} dB, Lmed = {Lmed:.1f} dB, Lr = {Lr:.1f} dB
Суммарные потери = {Ltot:.1f} dB
Дополнительные потери энергетики по сравнению с референсной трассой = {dL:.1f} dB

Ожидаемая медианная скорость = {speed:.1f} {sp_pref}bits/s''')

        elif bot_mode == 1:

            trace_dist, extra_dist, b1_max, b2_max, b_sum, Lr, speed, sp_pref \
            = await coords_analyzis_sosnik(
                    coords_dec[0:2], coords_dec[2:4], 0, str(path), bot_mode
            )
            await message.bot.send_message(message.from_user.id, text=
            f'''Протяженность трассы = {trace_dist:.1f} км
Угол закрытия {s_name[0]} = {b1_max:.2f}°
Угол закрытия {s_name[1]} = {b2_max:.2f}°
Суммарный угол закрытия = {b_sum:.2f}°

Дополнительные потери энергетики за счет наличия углов закрытия = {-Lr:.1f} dB
Эквивалентная дальность с учетом углов закрытия = {trace_dist + extra_dist:.2f} км
Ожидаемая скорость = {speed:.1f} {sp_pref}bits/s''')

        await types.ChatActions.typing()
        await message.bot.send_document(message.chat.id, open(str(path) + '.png', 'rb'),
                                        caption=f'Профиль трассы {s_name[0]} - {s_name[1]}',
                                        reply_markup=main_menu)
        # await  state.reset_state(with_data=False)
        await state.finish()

        os.remove(str(path)+'.png')

    except APIException as e:
        await message.bot.send_message(message.from_user.id,
                                       text=f"Ошибка получения данных внешнего сервера, попробуйте позже.\n\n{e}",
                                       reply_markup=main_menu)

    except (IndexError, ValueError) as e:
        await message.bot.send_message(message.from_user.id,
                                       text=f"Неизвестный формат координат, попробуйте указать координаты иначе.\n{e}\n"
                                              "\nВ координатах должна быть указана хотя бы одна "
                                              "цифра после десятичного разделителя "
                                              "(например 12.3456789° или 12'34\"56.7°)\n",
                                       reply_markup=main_menu)

