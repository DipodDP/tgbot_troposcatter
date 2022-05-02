import re
from os import remove
from pathlib import Path

import tgbot.services.async_great_circles as gc
from tgbot.services.async_path_profiler import coord_min2dec


def path_name(file_name: str):
    return Path(Path.cwd(), 'tgbot', 'services', 'sites coords', file_name)


async def get_sites(s_name: str, coords: str):
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
        remove(path_name('Точка А Точка Б.trlc'))
        remove(path_name('Точка А Точка Б.path'))
    except FileNotFoundError:
        pass

    path = str(path_name(f'{s_name[0]} {s_name[1]}'))
    if coords == '' or '?':
        try:
            with open(path + '.trlc', 'r') as f:
                coords = f.readlines()[0]

        except FileNotFoundError or IndexError:
            if coords == '?':
                coords = input('Введите координаты точек (Широта Долгота):')

    # Тестовые форматы ввода координат:
    # 55,3672698 91,646198; 005,9896421 92,8998994
    # #55,3672698 91,646198 55,9896421 92,8998994
    # 55°59'37.13"С  92°54'5.54"В  55°23'0.53"С 91°37'41.09"В
    # 55 59 37.13,  92 54 5.54,  55 23 0.53, 91 37 41.09
    # 51°58'12.12"С  85°56'35.96"В 51° 0'50.39"С  85°35'17.76"В
    # 55, 59, 37,13,  92, 54, 5,54,  55, 23, 0.53, 91, 37, 41,09
    # Регулярка ниже преобразует координаты, введенные в любом формате к ггг_мм_сс.с...
    coords = coords.replace(',', '.')
    coords = re.sub(r'\D?(\d?\d?\d)?\D*\s*(\d?\d)?\D*\s*(\d?\d?\d\.\d+)\D*', r'\1_\2_\3 ', coords)
    # Если градусы в десятичном формате удаляем получившиеся лишние "__" и двойные пробелы
    coords = coords.replace('__', '')
    coords = coords.replace('  ', ' ')
    # Получаем список[ггг_мм_сс,ггг_мм_сс...]
    coords = coords.split(' ')

    # Удаляем лишние символы и возвращаем пробелы из координат в списке
    for i in range(len(coords)):
        # coords[i] = coords[i].replace("_", ' ')
        coords[i] = re.sub(r'[^0-9._]|\.$', '', coords[i])

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
        coords_dec[i] = list(coords_dec[i].split('_'))
        if len(coords_dec[i]) <= 1:
            coords_dec[i] = float(coords_dec[i][0])
        else:
            for j in range(len(coords_dec[i])):
                coords_dec[i][j] = float(coords_dec[i][j])
            coords_dec[i] = coord_min2dec(coords_dec[i][0], coords_dec[i][1], coords_dec[i][2])

    for i in range(len(coords)):
        coords[i] = str.split(coords[i], '_')

        if coords[i].__len__() == 1:
            coords[i] = coords[i][0] + '° '

        else:
            coords[i] = coords[i][0] + '° ' + coords[i][1] + "' " + coords[i][2] + '"'

    return s_name, coords_dec, coords


async def get_azim(coords):
    azim1 = await gc.get_dist_azim(coords[0:2], coords[2:4])
    azim1 = round(azim1[1], 2)
    azim2 = await gc.get_dist_azim(coords[2:4], coords[0:2])
    azim2 = round(azim2[1], 2)
    mazim1 = round(azim1 - await gc.get_magdec(coords[0:2]), 2)
    mazim2 = round(azim2 - await gc.get_magdec(coords[2:4]), 2)

    return azim1, azim2, mazim1, mazim2
