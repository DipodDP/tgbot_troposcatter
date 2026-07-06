import datetime
import os
import logging
import re
from typing import Any

import numpy as np
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
import aiogram.utils.markdown as md

from trace_calc.domain import APIException, InvalidResponseException
from trace_calc.infrastructure.i18n import t, set_language

from paths import OUTPUT_DATA_DIR
from tgbot.keyboards.reply import main_menu
from tgbot.keyboards.inline import show_volume_keyboard


logger = logging.getLogger(__name__)


def esc(text: Any) -> str:
    """Escape characters for Telegram MarkdownV2."""
    if text is None:
        return ''
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', str(text))


def bold(text: Any) -> str:
    """Bold text for Telegram MarkdownV2."""
    return f'*{esc(text)}*'


def format_common_volume_results(profile) -> str:
    sight_lines = profile.lines_of_sight
    intersections = profile.intersections
    common_volume = profile.volume

    output = []

    # Common Volume metrics
    output.append(bold(t('common_volume_metrics').strip()))
    output.append(
        md.text(
            esc(
                t(
                    'common_scatter_volume',
                    common_volume.cone_intersection_volume_m3 / 1e9,
                ).strip()
            )
        )
    )
    output.append(
        md.text(
            esc(
                t(
                    'common_volume_top',
                    intersections.upper.distance_km,
                    intersections.upper.elevation_terrain / 1000,
                    intersections.upper.elevation_sea_level / 1000,
                ).strip()
            )
        )
    )
    output.append(
        md.text(
            esc(
                t(
                    'common_volume_bottom',
                    intersections.lower.distance_km,
                    intersections.lower.elevation_terrain / 1000,
                    intersections.lower.elevation_sea_level / 1000,
                ).strip()
            )
        )
    )
    output.append(
        md.text(
            esc(t('dist_a_cross_ab', common_volume.distance_a_to_cross_ab).strip())
        )
    )
    output.append(
        md.text(
            esc(t('dist_b_cross_ba', common_volume.distance_b_to_cross_ba).strip())
        )
    )
    output.append(
        md.text(
            esc(t('dist_between_crosses', common_volume.distance_between_crosses).strip())
        )
    )
    output.append(esc(''))

    # Beam Intersection Point
    if intersections.beam_intersection_point:
        output.append(bold(t('beam_intersection_point').strip()))
        output.append(
            md.text(
                esc(
                    t(
                        'beam_intersection_details',
                        intersections.beam_intersection_point.distance_km,
                        intersections.beam_intersection_point.elevation_sea_level
                        / 1000,
                        intersections.beam_intersection_point.elevation_terrain / 1000,
                        intersections.beam_intersection_point.angle or 0.0,
                    ).strip()
                )
            )
        )
    else:
        output.append(bold(t('beam_intersection_not_found').strip()))
    output.append('')

    # Antenna Elevation Angles
    output.append(bold(t('antenna_elevation_angles').strip()))
    output.append(
        md.text(
            esc(
                t(
                    'antenna_elevation_angle_a',
                    common_volume.antenna_elevation_angle_a,
                ).strip()
            )
        )
    )
    output.append(
        md.text(
            esc(
                t(
                    'antenna_elevation_angle_b',
                    common_volume.antenna_elevation_angle_b,
                ).strip()
            )
        )
    )
    output.append('')

    # Lower sight lines
    output.append(bold(t('lower_sight_lines').strip()))
    angle_a = np.degrees(np.arctan(sight_lines.lower_a[0] / 1000))
    angle_b = np.degrees(np.arctan(-sight_lines.lower_b[0] / 1000))
    output.append(
        md.text(
            esc(t('site_a_obstacle', sight_lines.lower_a[0], angle_a).strip())
        )
    )
    output.append(
        md.text(
            esc(t('site_b_obstacle', -sight_lines.lower_b[0], angle_b).strip())
        )
    )
    output.append('')

    # Upper sight lines
    output.append(bold(t('upper_sight_lines').strip()))
    angle_upper_a = np.degrees(np.arctan(sight_lines.upper_a[0] / 1000))
    angle_upper_b = np.degrees(np.arctan(-sight_lines.upper_b[0] / 1000))
    output.append(
        md.text(
            esc(t('site_a_upper', sight_lines.upper_a[0], angle_upper_a).strip())
        )
    )
    output.append(
        md.text(
            esc(t('site_b_upper', -sight_lines.upper_b[0], angle_upper_b).strip())
        )
    )
    output.append('')

    # Cross intersections
    output.append(bold(t('cross_intersections').strip()))
    output.append(
        md.text(
            esc(
                t(
                    'upper_a_lower_b',
                    intersections.cross_ab.distance_km,
                    intersections.cross_ab.elevation_sea_level / 1000,
                    intersections.cross_ab.elevation_terrain / 1000,
                ).strip()
            )
        )
    )
    output.append(
        md.text(
            esc(
                t(
                    'upper_b_lower_a',
                    intersections.cross_ba.distance_km,
                    intersections.cross_ba.elevation_sea_level / 1000,
                    intersections.cross_ba.elevation_terrain / 1000,
                ).strip()
            )
        )
    )
    output.append(esc(''))

    # Distance metrics to lower/upper intersections
    output.append(bold(t('distance_metrics').strip()))
    output.append(
        md.text(
            esc(t('dist_a_lower', common_volume.distance_a_to_lower_intersection).strip())
        )
    )
    output.append(
        md.text(
            esc(t('dist_b_lower', common_volume.distance_b_to_lower_intersection).strip())
        )
    )
    output.append(
        md.text(
            esc(t('dist_a_upper', common_volume.distance_a_to_upper_intersection).strip())
        )
    )
    output.append(
        md.text(
            esc(t('dist_b_upper', common_volume.distance_b_to_upper_intersection).strip())
        )
    )
    output.append(
        md.text(
            esc(
                t(
                    'dist_lower_upper',
                    common_volume.distance_between_lower_upper_intersections,
                ).strip()
            )
        )
    )
    return '\n'.join(output)


async def calc_report(message: Message, state: FSMContext):
    os.makedirs(OUTPUT_DATA_DIR, exist_ok=True)
    bot_mode = message.bot['config'].tg_bot.bot_mode
    analyzer = message.bot['analyzer']
    storage = message.bot['file_storage']
    lang = (message.from_user.language_code or 'en')[:2]
    set_language(lang)

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
            bold(t('site_coordinates').strip()),
            '',
            md.text(bold(s_name[0]), esc(':'), sep=''),
            md.text(esc('Широта:'), esc(coords[0])),
            md.text(esc('Долгота:'), esc(coords[1])),
            '',
            md.text(bold(s_name[1]), esc(':'), sep=''),
            md.text(esc('Широта:'), esc(coords[2])),
            md.text(esc('Долгота:'), esc(coords[3])),
            sep='\n',
        )
        await message.bot.send_message(
            message.from_user.id,
            text=coords_text,
            parse_mode=types.ParseMode.MARKDOWN_V2,
        )
        azimuth = md.text(
            bold(t('geographic_data').strip()),
            '',
            md.text(
                bold(f"{t('true_azimuth_a_b').strip()} {s_name[1]}:"),
                esc(f' {geo_data.true_azimuth_a_b}°'),
            ),
            md.text(
                md.text(esc(t('mag_declination_a').strip())),
                esc(f' {geo_data.mag_declination_a}°'),
            ),
            md.text(
                bold(f"{t('mag_azimuth_a_b').strip()} {s_name[1]}:"),
                esc(f' {geo_data.mag_azimuth_a_b}°'),
            ),
            bold('-' * 47),
            md.text(
                bold(f"{t('true_azimuth_b_a').strip()} {s_name[0]}:"),
                esc(f' {geo_data.true_azimuth_b_a}°'),
            ),
            md.text(
                md.text(esc(t('mag_declination_b').strip())),
                esc(f' {geo_data.mag_declination_b}°'),
            ),
            md.text(
                bold(f"{t('mag_azimuth_b_a').strip()} {s_name[0]}:"),
                esc(f' {geo_data.mag_azimuth_b_a}°'),
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
                lang=lang,
            )
            report_text = md.text(
                md.text(
                    bold(t('distance_km').strip()),
                    esc(f' = {trace_dist:.2f}'),
                ),
                md.text(
                    bold(f"{t('site_a_hca').strip()} {s_name[0]}"),
                    esc(f' = {b1_max:.2f}°'),
                ),
                md.text(
                    bold(f"{t('site_b_hca').strip()} {s_name[1]}"),
                    esc(f' = {b2_max:.2f}°'),
                ),
                md.text(
                    bold(t('hca_sum').strip()),
                    esc(f' = {b_sum:.2f}°'),
                ),
                '',
                bold(t('propagation_loss_parameters').strip()),
                esc(
                    f"{t('free_space_loss').strip()} = {L0:.1f} dB\n{t('atmospheric_loss').strip()} = {Lmed:.1f} dB\n{t('refraction_loss').strip()} = {Lr:.1f} dB\n"
                ),
                md.text(
                    bold(t('total_path_loss').strip()),
                    esc(f' = {Ltot:.1f} dB'),
                ),
                md.text(
                    bold('Дополнительные потери энергетики по сравнению с референсной трассой'),
                    esc(f' = {dL:.1f} dB'),
                ),
                '',
                md.text(
                    bold(t('estimated_speed').strip()),
                    esc(f' = {speed:.1f} {t("mbps") if sp_pref == "M" else t("kbps")}'),
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
                lang=lang,
            )
            equiv_dist = trace_dist + extra_dist
            report_text = md.text(
                md.text(
                    bold(t('distance_km').strip()),
                    esc(f' = {trace_dist:.2f}'),
                ),
                md.text(
                    bold(f"{t('site_a_hca').strip()} {s_name[0]}"),
                    esc(f' = {b1_max:.2f}°'),
                ),
                md.text(
                    bold(f"{t('site_b_hca').strip()} {s_name[1]}"),
                    esc(f' = {b2_max:.2f}°'),
                ),
                md.text(
                    bold(t('hca_sum').strip()),
                    esc(f' = {b_sum:.2f}°'),
                ),
                '',
                md.text(
                    esc('Дополнительные потери энергетики за счет наличия углов закрытия'),
                    esc(f' = {-Lr:.1f} dB'),
                ),
                md.text(
                    bold(t('equal_dist').strip()),
                    esc(f' = {equiv_dist:.2f}'),
                ),
                md.text(
                    bold(t('estimated_speed').strip()),
                    esc(f' = {speed:.1f} {t("mbps") if sp_pref == "M" else t("kbps")}'),
                ),
                sep='\n',
            )

        if analysis_result and analysis_result.profile_data:
            volume_text = format_common_volume_results(analysis_result.profile_data)
        else:
            volume_text = esc(
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
                    caption=bold(f'Профиль трассы {s_name[0]} - {s_name[1]}'),
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

        if isinstance(e, InvalidResponseException) and "414" in str(e):
            user_message = (
                "Слишком длинная трасса для API. "
                "Попробуйте уменьшить расстояние между точками."
            )
        elif isinstance(e, APIException):
            user_message = "Ошибка при получении данных о высотах. Попробуйте позже."
        else:
            user_message = f'Произошла ошибка: {e}'

        await message.answer(user_message, reply_markup=main_menu)
        if await state.get_state() is not None:
            await state.finish()
