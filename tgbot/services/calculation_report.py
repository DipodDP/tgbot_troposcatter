import datetime
import os
import logging

import numpy as np
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
import aiogram.utils.markdown as md

from paths import OUTPUT_DATA_DIR
from tgbot.keyboards.reply import main_menu
from tgbot.keyboards.inline import show_volume_keyboard


logger = logging.getLogger(__name__)


def format_common_volume_results(profile) -> str:
    sight_lines = profile.lines_of_sight
    intersections = profile.intersections
    common_volume = profile.volume

    output = []

    # Common Volume metrics
    output.append(md.bold('\nМетрики общего объема:\n'))
    output.append(
        md.text(
            md.bold('  Общий объем рассеяния:'),
            md.escape_md(f' {common_volume.cone_intersection_volume_m3 / 1e9:.2f} км³'),
        )
    )
    output.append(
        md.text(
            md.bold('  Верхняя граница объема рассеяния:'),
            md.escape_md(
                f' {intersections.upper.distance_km:.2f} км, '
                f'{intersections.upper.elevation_terrain / 1000:.2f} км над рельефом, '
                f'{intersections.upper.elevation_sea_level / 1000:.2f} км над уровнем моря'
            ),
        )
    )
    output.append(
        md.text(
            md.bold('  Нижняя граница объема рассеяния:'),
            md.escape_md(
                f' {intersections.lower.distance_km:.2f} км, '
                f'{intersections.lower.elevation_terrain / 1000:.2f} км над рельефом, '
                f'{intersections.lower.elevation_sea_level / 1000:.2f} км над уровнем моря'
            ),
        )
    )
    output.append(
        md.text(
            '  Расстояние от А до Верх А x Низ Б:',
            md.escape_md(f' {common_volume.distance_a_to_cross_ab:.2f} км'),
        )
    )
    output.append(
        md.text(
            '  Расстояние от Б до Верх Б x Низ А:',
            md.escape_md(f' {common_volume.distance_b_to_cross_ba:.2f} км'),
        )
    )
    output.append(
        md.text(
            '  Расстояние между границами объема рассеяния:',
            md.escape_md(f' {common_volume.distance_between_crosses:.2f} км'),
        )
    )

    # Beam Intersection Point
    if intersections.beam_intersection_point:
        output.append(md.bold('\nТочка пересечения лучей:'))
        output.append(
            md.text(
                '  Расстояние:',
                md.escape_md(
                    f' {intersections.beam_intersection_point.distance_km:.2f} км, '
                    f'Высота над уровнем моря: {intersections.beam_intersection_point.elevation_sea_level / 1000:.2f} км, '
                    f'Высота над рельефом: {intersections.beam_intersection_point.elevation_terrain / 1000:.2f} км, '
                    f'Угол пересечения: {intersections.beam_intersection_point.angle:.2f}°'
                    if intersections.beam_intersection_point.angle is not None
                    else ' N/A'
                ),
            )
        )
    else:
        output.append(
            md.text(
                md.bold('\nТочка пересечения лучей:'),
                md.escape_md(' Не найдена в пределах трассы.'),
            )
        )

    # Antenna Elevation Angles
    output.append(md.bold('\nУглы возвышения антенн:'))
    output.append(
        md.text(
            '  Угол возвышения антенны А:',
            md.escape_md(f' {common_volume.antenna_elevation_angle_a:.2f}°'),
        )
    )
    output.append(
        md.text(
            '  Угол возвышения антенны Б:',
            md.escape_md(f' {common_volume.antenna_elevation_angle_b:.2f}°'),
        )
    )

    # Lower sight lines
    output.append(md.bold('\nНижние линии визирования:'))
    angle_a = np.degrees(np.arctan(sight_lines.lower_a[0] / 1000))
    angle_b = np.degrees(np.arctan(-sight_lines.lower_b[0] / 1000))
    output.append(
        md.text(
            md.escape_md('  Точка А -> Препятствие:'),
            md.escape_md(f' наклон={sight_lines.lower_a[0]:.4f}, угол={angle_a:.2f}°'),
        )
    )
    output.append(
        md.text(
            md.escape_md('  Точка Б -> Препятствие:'),
            md.escape_md(f' наклон={-sight_lines.lower_b[0]:.4f}, угол={angle_b:.2f}°'),
        )
    )

    # Upper sight lines
    output.append(md.bold('\nВерхние линии визирования:'))
    angle_upper_a = np.degrees(np.arctan(sight_lines.upper_a[0] / 1000))
    angle_upper_b = np.degrees(np.arctan(-sight_lines.upper_b[0] / 1000))
    output.append(
        md.text(
            md.escape_md('  Точка А (верхняя):'),
            md.escape_md(
                f' наклон={sight_lines.upper_a[0]:.4f}, угол={angle_upper_a:.2f}°'
            ),
        )
    )
    output.append(
        md.text(
            md.escape_md('  Точка Б (верхняя):'),
            md.escape_md(
                f' наклон={-sight_lines.upper_b[0]:.4f}, угол={angle_upper_b:.2f}°'
            ),
        )
    )

    # Cross intersections
    output.append(md.bold('\nГраницы пересечения:'))
    output.append(
        md.text(
            '  Верх А x Низ Б:',
            md.escape_md(
                f' {intersections.cross_ab.distance_km:.2f} км, '
                f'{intersections.cross_ab.elevation_sea_level / 1000:.2f} км над уровнем моря, '
                f'{intersections.cross_ab.elevation_terrain / 1000:.2f} км над рельефом'
            ),
        )
    )
    output.append(
        md.text(
            '  Верх Б x Низ А:',
            md.escape_md(
                f' {intersections.cross_ba.distance_km:.2f} км, '
                f'{intersections.cross_ba.elevation_sea_level / 1000:.2f} км над уровнем моря, '
                f'{intersections.cross_ba.elevation_terrain / 1000:.2f} км над рельефом'
            ),
        )
    )

    # Distance metrics to lower/upper intersections
    output.append(md.bold('\nРасстояния до нижних/верхних пересечений:'))
    output.append(
        md.text(
            '  Расстояние от А до нижнего пересечения:',
            md.escape_md(f' {common_volume.distance_a_to_lower_intersection:.2f} км'),
        )
    )
    output.append(
        md.text(
            '  Расстояние от Б до нижнего пересечения:',
            md.escape_md(f' {common_volume.distance_b_to_lower_intersection:.2f} км'),
        )
    )
    output.append(
        md.text(
            '  Расстояние от А до верхнего пересечения:',
            md.escape_md(f' {common_volume.distance_a_to_upper_intersection:.2f} км'),
        )
    )
    output.append(
        md.text(
            '  Расстояние от Б до верхнего пересечения:',
            md.escape_md(f' {common_volume.distance_b_to_upper_intersection:.2f} км'),
        )
    )
    output.append(
        md.text(
            '  Расстояние между нижним и верхним пересечениями:',
            md.escape_md(
                f' {common_volume.distance_between_lower_upper_intersections:.2f} км'
            ),
        )
    )
    return '\n'.join(output)


async def calc_report(message: Message, state: FSMContext):
    os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)
    bot_mode = message.bot['config'].tg_bot.bot_mode
    analyzer = message.bot['analyzer']
    storage = message.bot['file_storage']

    try:
        async with state.proxy() as data:
            s_names_text = ' '.join(data['s_names'])
            s_coords_text = ' '.join(data['s_coords'])
            s_heights = data.get('s_heights', [2.0, 2.0])
            antenna_a_height = float(s_heights[0]) if s_heights else 2.0
            antenna_b_height = float(s_heights[1]) if len(s_heights) > 1 else 2.0

            if not data['s_names']:
                path_name = 'Точка А Точка Б'
            elif len(data['s_names']) == 1:
                path_name = f'{data["s_names"][0]} Точка Б'
            else:
                path_name = f'{data["s_names"][0]} {data["s_names"][1]}'

            if not s_coords_text:
                try:
                    path_data_from_storage = await storage.load(path_name)
                    coords = path_data_from_storage.coordinates
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
            geo_data = await analyzer.get_azimuths(coords_dec)

            data['s_name'] = s_name
            data['path_name'] = path_name
            data['current_view'] = 'report'

        coords_text = md.text(
            md.bold('Координаты точек:'),
            '',
            md.text(md.bold(s_name[0]), ':', sep=''),
            md.text('Широта:', md.escape_md(coords[0])),
            md.text('Долгота:', md.escape_md(coords[1])),
            '',
            md.text(md.bold(s_name[1]), ':', sep=''),
            md.text('Широта:', md.escape_md(coords[2])),
            md.text('Долгота:', md.escape_md(coords[3])),
            sep='\n',
        )
        await message.bot.send_message(
            message.from_user.id,
            text=coords_text,
            parse_mode=types.ParseMode.MARKDOWN_V2,
        )
        azimuth = md.text(
            md.text(
                md.bold('Азимут на точку ', s_name[1], ':'),
                md.escape_md(f' {geo_data.true_azimuth_a_b}°'),
            ),
            md.text(
                'Магнитное склонение:',
                md.escape_md(f' {geo_data.mag_declination_a}°'),
            ),
            md.text(
                md.bold('Магнитный азимут на точку ', s_name[1], ':'),
                md.escape_md(f' {geo_data.mag_azimuth_a_b}°'),
            ),
            md.bold('-' * 47),
            md.text(
                md.bold('Азимут на точку ', s_name[0], ':'),
                md.escape_md(f' {geo_data.true_azimuth_b_a}°'),
            ),
            md.text(
                'Магнитное склонение :',
                md.escape_md(f' {geo_data.mag_declination_b}°'),
            ),
            md.text(
                md.bold('Магнитный азимут на точку ', s_name[0], ':'),
                md.escape_md(f' {geo_data.mag_azimuth_b_a}°'),
            ),
            sep='\n',
        )
        await message.bot.send_message(
            message.from_user.id, text=azimuth, parse_mode=types.ParseMode.MARKDOWN_V2
        )

        print(f'{datetime.datetime.now()} {s_name[0]} - {s_name[1]}')

        report_text = ''
        volume_text = ''
        analysis_result = None

        if bot_mode == 0:
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
                analysis_result,
            ) = await analyzer.analyze_groza(
                coord_a=coords_dec[0:2],
                coord_b=coords_dec[2:4],
                path_filename=path_name,
                geo_data=geo_data,
                antenna_a_height=antenna_a_height,
                antenna_b_height=antenna_b_height,
            )
            report_text = md.text(
                md.text(
                    md.bold('Протяженность трассы'),
                    md.escape_md(f' = {trace_dist:.2f} км'),
                ),
                md.text(
                    md.bold('Угол закрытия ', s_name[0]),
                    md.escape_md(f' = {b1_max:.2f}°'),
                ),
                md.text(
                    md.bold('Угол закрытия ', s_name[1]),
                    md.escape_md(f' = {b2_max:.2f}°'),
                ),
                md.text(
                    md.bold('Суммарный угол закрытия'),
                    md.escape_md(f' = {b_sum:.2f}°'),
                ),
                '',
                md.bold('Потери:'),
                md.escape_md(
                    f' L0 = {L0:.1f} dB, Lmed = {Lmed:.1f} dB, Lr = {Lr:.1f} dB'
                ),
                md.text(md.bold('Суммарные потери'), md.escape_md(f' = {Ltot:.1f} dB')),
                md.text(
                    md.bold(
                        'Дополнительные потери энергетики по сравнению с референсной трассой'
                    ),
                    md.escape_md(f' = {dL:.1f} dB'),
                ),
                '',
                md.text(
                    md.bold('Ожидаемая медианная скорость'),
                    md.escape_md(f' = {speed:.1f} {sp_pref}bits/s'),
                ),
                sep='\n',
            )

        elif bot_mode == 1:
            (
                trace_dist,
                extra_dist,
                b1_max,
                b2_max,
                b_sum,
                Lr,
                speed,
                sp_pref,
                analysis_result,
            ) = await analyzer.analyze_sosnik(
                coord_a=coords_dec[0:2],
                coord_b=coords_dec[2:4],
                path_filename=path_name,
                geo_data=geo_data,
                antenna_a_height=antenna_a_height,
                antenna_b_height=antenna_b_height,
            )
            equiv_dist = trace_dist + extra_dist
            report_text = md.text(
                md.text(
                    md.bold('Протяженность трассы'),
                    md.escape_md(f' = {trace_dist:.2f} км'),
                ),
                md.text(
                    'Угол закрытия ',
                    md.bold(s_name[0]),
                    md.escape_md(f' = {b1_max:.2f}°'),
                ),
                md.text(
                    'Угол закрытия ',
                    md.bold(s_name[1]),
                    md.escape_md(f' = {b2_max:.2f}°'),
                ),
                md.text(
                    md.bold('Суммарный угол закрытия'),
                    md.escape_md(f' = {b_sum:.2f}°'),
                ),
                '',
                md.text(
                    'Дополнительные потери энергетики за счет наличия углов закрытия',
                    md.escape_md(f' = {-Lr:.1f} dB'),
                ),
                md.text(
                    'Эквивалентная дальность с учетом углов закрытия',
                    md.escape_md(f' = {equiv_dist:.2f} км'),
                ),
                md.text(
                    md.bold('Ожидаемая скорость'),
                    md.escape_md(f' = {speed:.1f} {sp_pref}bits/s'),
                ),
                sep='\n',
            )

        if analysis_result and analysis_result.profile_data:
            volume_text = format_common_volume_results(analysis_result.profile_data)
        else:
            volume_text = md.escape_md(
                'Данные об объеме рассеяния недоступны для этого расчета.'
            )

        async with state.proxy() as data:
            data['report_view_text'] = report_text
            data['volume_view_text'] = volume_text

        await message.bot.send_message(
            message.from_user.id,
            text=report_text,
            reply_markup=show_volume_keyboard,
            parse_mode=types.ParseMode.MARKDOWN_V2,
        )

        plot_path = os.path.join(OUTPUT_DATA_DIR, f'{path_name}.png')
        try:
            with open(plot_path, 'rb') as photo:
                await message.bot.send_document(
                    message.chat.id,
                    photo,
                    caption=md.bold('Профиль трассы ', s_name[0], ' - ', s_name[1]),
                    reply_markup=main_menu,
                    parse_mode=types.ParseMode.MARKDOWN_V2,
                )
        except FileNotFoundError:
            logger.warning(f"Plot file not found at '{plot_path}'")
            await message.answer(
                'Файл с профилем трассы не найден.', reply_markup=main_menu
            )
        finally:
            if os.path.exists(plot_path):
                os.remove(plot_path)

    except Exception as e:
        logger.exception('Error in calc_report')
        await message.answer(f'Произошла ошибка: {e}', reply_markup=main_menu)
        if await state.get_state() is not None:
            await state.finish()
