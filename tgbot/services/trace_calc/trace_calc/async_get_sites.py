import re
from os import remove
from environs import Env
from pathlib import Path

import trace_calc.async_great_circles as gc
from trace_calc.profile_analysis import coord_min2dec


def path_sites(file_name: str):
    env = Env()
    env.read_env(".env")
    path_to_sites = env('SITES_PATH').split('/')
    return Path(Path.cwd(), *path_to_sites, file_name)


async def get_sites(s_name: str, coords: str): # -> s_name: list(str), coords_dec: list(float), coords: list(str)
    if s_name == '?':
        s_name = input('Введите названия точек (Точка(А) Точка(Б))')

    s_name = s_name.replace(',', ' ')
    s_name = s_name.replace(';', ' ')
    s_name = s_name.split(' ')

    s_name = list(filter(None, s_name))

    if not s_name:
        s_name = ['Точка А', 'Точка Б']
    elif len(s_name) == 1:
        s_name.append('Точка Б')

    try:
        remove(path_sites('Точка А Точка Б.trlc'))
        remove(path_sites('Точка А Точка Б.path'))
    except FileNotFoundError:
        pass

    path = str(path_sites(f'{s_name[0]} {s_name[1]}'))
    if coords == '' or '?':
        try:
            with open(path + '.trlc', 'r') as f:
                coords = f.readlines()[0]

        except FileNotFoundError or IndexError:
            if coords == '?':
                coords = input('Введите координаты точек (Широта Долгота):')

    # Тестовые форматы ввода координат:
    # 55,3672698 91,646198; 5,9896421 92,8998994
    # #55,3672698 91,646198 55,9896421 92,8998994
    # 55°59'37.13"С  92°54'5.54"В  55°23'0.53"С 91°37'41.09"В
    # 55 59 37.13,  92 54 5.54,  55 23 0.53, 91 37 41.09
    # 64° 44' 20.37"С  177° 29' 11.64"В  66° 18' 47.69"С  179° 8' 49.12"З
    # 55, 59, 37,13,  92, 54, 5,54,  55, 23, 0.53, 91, 37, 41,09
    # Регулярка ниже преобразует координаты, введенные в любом формате к ггг_мм_сс.с...
    coords = coords.replace(',', '.')
    coords = coords.replace('\n', ' ')
    coords = coords.replace('  ', ' ')

    coords = re.sub(r'\D*\b(\d?\d?\d)?\D*\s*(\d?\d)?\D*\s*(\d?\d?\d\.\d+)_?(\D*\s*[sSwWсСвВюЮзЗ])?\D*',
                    r'\1_\2_\3_\4: ', coords)

    # Удаляем лишние символы
    coords = re.sub(r'[^0-9._sSwWсСвВюЮзЗ: ]|\.$', '', coords)
    # Если градусы в десятичном формате удаляем получившиеся лишние "__" и двойные пробелы
    coords = coords.replace('__', '')
    coords = coords.replace('  ', ' ')
    coords = coords.replace('_ ', '_')
    coords = coords.replace(':', '')

    # Получаем список[ггг_мм_сс,ггг_мм_сс...]
    coords = coords.split(' ')

    # # Возвращаем пробелы для координат в списке
    # for i in range(len(coords)):
    #     coords[i] = re.sub(r'[^0-9._nNeEsSwWсСвВюЮзЗ]|\.$', '', coords[i])

    coords = list(filter(None, coords))

    try:
        with open(path + '.trlc', 'x') as f:
            f.writelines(coords[0] + ' ' + coords[1] + ' ' + coords[2] + ' ' + coords[3])

    except FileExistsError:
        pass

    # Форматирование данных для вывода
    # Возвращием обратно " " (если есть) в название точки
    for i in range(len(s_name)):
        s_name[i] = s_name[i].replace('_', ' ')

    # Преобразуем формат координаты в десятичный (возвращаем также исходный формат (coords)
    # для проверки правильности ввода)
    coords_dec = list(coords)
    for i in range(len(coords_dec)):
        coords_dec[i] = coords_dec[i].split('_')
        if len(coords_dec[i]) <= 2:
            coords_dec[i] = float(coords_dec[i][0]) if re.match(r'[sSwWюЮзЗ]', coords_dec[i][-1]) is None \
                else -float(coords_dec[i][0])
        else:
            for j in range(len(coords_dec[i]) - 1):
                coords_dec[i][j] = float(coords_dec[i][j])

            if re.match(r'[sSwWюЮзЗ]', coords_dec[i][-1]) is None:
                coords_dec[i] = coord_min2dec(coords_dec[i][0], coords_dec[i][1], coords_dec[i][2])
            else:
                coords_dec[i] = -coord_min2dec(coords_dec[i][0], coords_dec[i][1], coords_dec[i][2])

    for i in range(len(coords)):
        coords[i] = str.split(coords[i], '_')

        if len(coords[i]) == 2:
            if coords[i][-1] == '':
                if i % 2 == 0:
                    coords[i][1] = "N"
                else:
                    coords[i][1] = "E"
            coords[i] = coords[i][0] + '° ' + coords[i][1]

        else:
            if coords[i][-1] == '':
                if i % 2 == 0:
                    coords[i][3] = "N"
                else:
                    coords[i][3] = "E"
            coords[i] = coords[i][0] + '° ' + coords[i][1] + "' " + coords[i][2] + '" ' + coords[i][3]

    return s_name, coords_dec, coords


async def get_azim(coords):
    azim1 = await gc.get_dist_azim(coords[0:2], coords[2:4])
    azim1 = round(azim1[1], 2)
    azim2 = await gc.get_dist_azim(coords[2:4], coords[0:2])
    azim2 = round(azim2[1], 2)
    dec1 = round(await gc.get_magdec(coords[0:2]), 2)
    dec2 = round(await gc.get_magdec(coords[2:4]), 2)
    m_azim1 = round(azim1 - dec1, 2)
    m_azim2 = round(azim2 - dec2, 2)

    return azim1, azim2, dec1, dec2, m_azim1, m_azim2
