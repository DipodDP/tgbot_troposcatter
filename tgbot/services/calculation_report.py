import datetime
import os
import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from environs import Env

from tgbot.keyboards.reply import main_menu
from trace_calc import TraceAnalyzerAPI
from trace_calc.domain.exceptions import APIException
from trace_calc.domain.constants import OUTPUT_DATA_DIR
from trace_calc.infrastructure.storage import FilePathStorage

logger = logging.getLogger(__name__)


async def calc_report(message: Message, state: FSMContext):
    os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)
    bot_mode = message.bot['config'].tg_bot.bot_mode
    env = Env()
    env.read_env('.env')
    analyzer = TraceAnalyzerAPI.create_from_env(env)
    storage = FilePathStorage(output_dir=OUTPUT_DATA_DIR)

    try:
        async with state.proxy() as data:
            s_names_text = ' '.join(data['s_names'])
            s_coords_text = ' '.join(data['s_coords'])

            # Determine path name
            if not data['s_names']:
                path_name = 'Точка А Точка Б'
            elif len(data['s_names']) == 1:
                path_name = f'{data["s_names"][0]} Точка Б'
            else:
                path_name = f'{data["s_names"][0]} {data["s_names"][1]}'

            if not s_coords_text:
                try:
                    path_data = await storage.load(path_name)
                    coords = path_data.coordinates
                    s_coords_text = (
                        f'{coords[0][0]} {coords[0][1]} {coords[-1][0]} {coords[-1][1]}'
                    )
                except (FileNotFoundError, IndexError, ValueError) as e:
                    logger.error(
                        f'Could not load coordinates from file for {path_name}: {e}'
                    )
                    await message.answer('Не удалось загрузить сохраненные координаты.')
                    return

            s_name, coords_dec, coords = await analyzer.parse_sites(
                s_names_text, s_coords_text
            )

        # Send coordinate information
        await types.ChatActions.typing()
        await message.bot.send_message(
            message.from_user.id,
            text='Координаты точек: \n\n'
            + s_name[0]
            + ':\nШирота: '
            + coords[0]
            + '\nДолгота: '
            + coords[1]
            + '\n\n'
            + s_name[1]
            + ':\nШирота: '
            + coords[2]
            + '\nДолгота: '
            + coords[3],
        )

        # Get and send azimuth data
        await types.ChatActions.typing()
        geo_data = await analyzer.get_azimuths(
            coords_dec
        )
        azimuth = (
            'Азимут на точку '
            + s_name[1]
            + ': '
            + str(geo_data.true_azimuth_a_b)
            + '°\n'
            + 'Магнитное склонение: '
            + str(geo_data.mag_declination_a)
            + '°\n'
            + 'Магнитный азимут на точку '
            + s_name[1]
            + ': '
            + str(geo_data.mag_azimuth_a_b)
            + '°\n'
            + '-----------------------------------------------\n'
            + 'Азимут на точку '
            + s_name[0]
            + ': '
            + str(geo_data.true_azimuth_b_a)
            + '°\n'
            + 'Магнитное склонение : '
            + str(geo_data.mag_declination_b)
            + '°\n'
            + 'Магнитный азимут на точку '
            + s_name[0]
            + ': '
            + str(geo_data.mag_azimuth_b_a)
            + '°\n'
        )
        await message.bot.send_message(message.from_user.id, text=azimuth)

        await types.ChatActions.typing()

        print(f'{datetime.datetime.now()} {s_name[0]} - {s_name[1]}')

        # Perform trace analysis
        if bot_mode == 0:  # Groza analysis
            (
                L0,
                Lmed,
                Lr,
                trace_dist,
                b1_max,
                b2_max,
                b_sum,
                Ltot,
                dL,
                speed,
                sp_pref,
            ) = await analyzer.analyze_groza(
                coord_a=coords_dec[0:2],
                coord_b=coords_dec[2:4],
                path_filename=path_name,
                geo_data=geo_data,
            )
            logger.debug(
                f'Groza analysis result: L0={L0}, Lmed={Lmed}, Lr={Lr}, trace_dist={trace_dist}, b1_max={b1_max}, b2_max={b2_max}, b_sum={b_sum}, Ltot={Ltot}, dL={dL}, speed={speed}, sp_pref={sp_pref}'
            )
            await message.bot.send_message(
                message.from_user.id,
                text=f"""Протяженность трассы = {trace_dist:.2f} км
Угол закрытия {s_name[0]} = {b1_max:.2f}°
Угол закрытия {s_name[1]} = {b2_max:.2f}°
Суммарный угол закрытия = {b_sum:.2f}°

Потери:
L0 = {L0:.1f} dB, Lmed = {Lmed:.1f} dB, Lr = {Lr:.1f} dB
Суммарные потери = {Ltot:.1f} dB
Дополнительные потери энергетики по сравнению с референсной трассой = {dL:.1f} dB

Ожидаемая медианная скорость = {speed:.1f} {sp_pref}bits/s""",
            )

        elif bot_mode == 1:  # Sosnik analysis
            (
                trace_dist,
                extra_dist,
                b1_max,
                b2_max,
                b_sum,
                Lr,
                speed,
                sp_pref,
            ) = await analyzer.analyze_sosnik(
                coord_a=coords_dec[0:2],
                coord_b=coords_dec[2:4],
                path_filename=path_name,
                geo_data=geo_data,
            )
            logger.debug(
                f'Sosnik analysis result: trace_dist={trace_dist}, extra_dist={extra_dist}, b1_max={b1_max}, b2_max={b2_max}, b_sum={b_sum}, Lr={Lr}, speed={speed}, sp_pref={sp_pref}'
            )
            equiv_dist = trace_dist + extra_dist
            await message.bot.send_message(
                message.from_user.id,
                text=f"""Протяженность трассы = {trace_dist:.2f} км
Угол закрытия {s_name[0]} = {b1_max:.2f}°
Угол закрытия {s_name[1]} = {b2_max:.2f}°
Суммарный угол закрытия = {b_sum:.2f}°

Дополнительные потери энергетики за счет наличия углов закрытия = {-Lr:.1f} dB
Эквивалентная дальность с учетом углов закрытия = {equiv_dist:.2f} км
Ожидаемая скорость = {speed:.1f} {sp_pref}bits/s""",
            )

        plot_path = os.path.join(OUTPUT_DATA_DIR, f'{path_name}.png')
        logger.debug(f"Attempting to send plot from path: '{plot_path}'")

        # Send plot
        await types.ChatActions.typing()
        with open(plot_path, 'rb') as photo:
            await message.bot.send_document(
                message.chat.id,
                photo,
                caption=f'Профиль трассы {s_name[0]} - {s_name[1]}',
                reply_markup=main_menu,
            )
        await state.finish()

        try:
            os.remove(plot_path)
            logger.debug(f"Successfully removed plot file: '{plot_path}'")
        except FileNotFoundError:
            logger.warning(
                f"Could not remove plot file, as it was not found at '{plot_path}' (it might have been deleted already)."
            )
        except Exception as file_error:
            logger.error(f"Error removing plot file '{plot_path}': {file_error}")

    except APIException as e:
        logger.error(f'API Exception in calc_report: {e}')
        await message.bot.send_message(
            message.from_user.id,
            text=f'Ошибка получения данных внешнего сервера,\
            попробуйте позже.\n\n{e}',
            reply_markup=main_menu,
        )

    except (IndexError, ValueError) as e:
        logger.error(f'Coordinate parsing or data access error in calc_report: {e}')
        await message.bot.send_message(
            message.from_user.id,
            text=f'Неизвестный формат координат, попробуйте указать\
            координаты иначе.\n{e}\n'
            '\nВ координатах должна быть указана хотя бы одна '
            'цифра после десятичного разделителя '
            '(например 12.3456789° или 12\'34"56.7°)\n',
            reply_markup=main_menu,
        )
    except Exception as e:
        logger.exception('An unexpected error occurred in calc_report')
        await message.bot.send_message(
            message.from_user.id,
            text=f'Произошла непредвиденная ошибка: {e}',
            reply_markup=main_menu,
        )
