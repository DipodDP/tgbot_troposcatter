"""Bot-level i18n translations.

Provides translations for all user-facing bot strings (messages, keyboard labels).
Calculation report strings are handled by trace_calc.infrastructure.i18n.
"""

SUPPORTED_LANGS = ('ru', 'en')
DEFAULT_LANG = 'en'

TRANSLATIONS: dict[str, dict[str, str]] = {
    'ru': {
        # Greeting / start
        'hello': 'Привет, ',
        'start_groza': (
            '! Этот бот может рассчитать параметры тропосферной '
            'линии для станции "Гроза 1,5" и, '
            'даже, её скорость (но это не точно). '
            '\nПосмотреть статус и запустить бота: http://troposcatterbot.eu.pythonanywhere.com'
        ),
        'start_sosnik_pm': (
            '! Этот бот может рассчитать параметры тропосферной '
            'линии для станции "С-ПМ". '
            '\nПосмотреть статус и запустить бота:'
            '\nhttp://stropobot.eu.pythonanywhere.com'
        ),
        'start_error': '! Необходимо определить режим работы бота',

        # Help
        'help_msg1': (
            'Для начала расчета нажмите кнопку '
            '{btn_calc_t}'
            ' и следуйте инструкциям.\n\n'
            'Названия точек и их координаты можно вводить в одном сообщении '
            'или в нескольких (попорядку).\n'
            'Формат ввода координат - любой, вида ггг_мм_сс,с или ггг,г.\n\n'
            'Расчет производится для северной широты и восточной долготы, '
            'если в заданных координатах не определено иначе'
        ),
        'help_msg2': (
            'В меню '
            '{btn_show_climate_zone}'
            ' можно узнать значение климатической поправки для региона.'
        ),

        # Reply keyboard button labels
        'btn_calc_t': '⚡️ Рассчитать трассу',
        'btn_show_climate_zone': '🌤 Показать климатические зоны',
        'btn_show_bot_inf': '📗 Показать информацию',
        'btn_next': '➡️ Дальше',
        'btn_back': '↩️ Назад',
        'btn_climate_zones': '🌍 Карта климатических зон',
        'btn_bot_inf': '🤖 About Troposcatter bot',
        'btn_saved_sites': '🧭 Показать сохраненные точки',
        'btn_like': '',

        # Inline keyboard button labels
        'btn_use_file': 'Использовать',
        'btn_del_file': 'Удалить',
        'btn_yes': 'Да',
        'btn_no': 'Нет',
        'btn_set_heights': 'Задать высоту',
        'btn_show_volume': 'Показать данные об объеме',
        'btn_show_report': 'Показать расчет потерь',

        # Calc flow messages
        'enter_site_names': 'Введите названия точек: ',
        'add_another_site': 'Добавить еще точку?',
        'enter_next_site_name': 'Введите название следующей точки:',
        'enter_coords': 'Введите координаты точек:',
        'add_next_coords': 'Добавить координаты следующей точки?',
        'enter_next_coords': 'Введите координаты следующей точки:',
        'coords_entered_default_heights': (
            'Координаты введены. Нажмите "{btn_next}" '
            'для расчета с высотами по умолчанию (2м).'
        ),
        'or_set_heights': 'Или задайте свои высоты.',
        'found_coords_use_or_delete': (
            'Нашел координаты этих точек! '
            'Использовать или удалить эти координаты?'
        ),
        'coords_not_found': (
            'Сохраненные данные для этих точек не найдены. '
            'Введите координаты точек: '
        ),
        'calculating_default': 'Рассчитываю трассу с высотами по умолчанию...',
        'calculating': 'Рассчитываю трассу...',
        'enter_height_for': (
            'Введите высоту подвеса антенны для точки "{name}" (в метрах):'
        ),
        'invalid_height': (
            'Некорректное значение. Пожалуйста, '
            'введите высоту в метрах (целое число от 1 до 999).'
        ),
        'press_next_to_calc': 'Нажмите кнопку {btn_next} для начала расчета',
        'use_saved_coords': (
            'Использую сохраненные координаты. Нажмите "{btn_next}" '
            'для расчета с высотами по умолчанию (2м).'
        ),
        'coords_deleted': (
            'Сохраненые координаты удалены. Введите координаты точек: '
        ),
        'delete_error': 'Ошибка удаления. Введите координаты точек: ',
        'main_menu': 'Главное меню: ',
        'enter_site_names_again': 'Введите названия точек заново: ',

        # Bot info / saved sites
        'what_to_know': 'Что хотите узнать?',
        'know_coords_for': 'Я знаю координаты точек для этих трасс:',
        'sites_list_hidden': 'Список сохранненых точек скрыт!',
        'no_info': 'No information',
        'thanks': 'Спасибо:)',
        'main_menu_label': 'Главное меню',

        # Climate zone
        'climate_zone_info': (
            'Здесь можно скачать карту климатических зон в формате .PDF'
        ),
        'climate_map_caption': 'Карта климатических зон',
        'file_id_saved': (
            'Id файла сохранен для более быстрой загрузки.\n'
            'Id для переменной окружения CLIMATE\\_ZONES\\_FILE\\_ID:\n{file_id}'
        ),

        # Volume / report view switching
        'volume_not_found': 'Данные об объеме рассеяния не найдены.',
        'report_not_found': 'Данные отчета не найдены.',

        # Sticker / file handlers
        'sticker_id': 'Вот id твоего стикера:\n{sticker_id}',
        'file_id': 'Вот id твоего файла:\n{file_id}',

        # Wrong / unknown
        'bad_words_ru': 'Фу таким быть',
        'unknown_command': 'Неизвестная команда',

        # Calculation report
        'latitude': 'Широта: ',
        'longitude': 'Долгота: ',
        'extra_losses_hca': 'Дополнительные потери энергетики за счет наличия углов закрытия',
        'volume_data_unavailable': 'Данные об объеме рассеяния недоступны для этого расчета.',
        'path_profile_caption': 'Профиль трассы {name1} - {name2}',
        'profile_not_found': 'Файл с профилем трассы не найден.',
        'path_too_long': 'Слишком длинная трасса для API. Попробуйте уменьшить расстояние между точками.',
        'elevation_error': 'Ошибка при получении данных о высотах. Попробуйте позже.',
        'occurred_error': 'Произошла ошибка: {error}',
        'load_coords_error': 'Не удалось загрузить сохраненные координаты.',

        # Admin
        'admin_hello': 'Привет, админ! Это tropobot.\n Нажмите /stop, чтобы остановить бота\n {mware_data}',
        'admin_button': 'Просто кнопка',
        'admin_troposcatter_calc': 'Расчет тропосферной трассы',
        'admin_stopping': 'Остановка бота...',
        'admin_button_pressed': 'Вы нажали кнопку',
    },
    'en': {
        # Greeting / start
        'hello': 'Hello, ',
        'start_groza': (
            '! This bot can calculate troposcatter link parameters '
            'for the "Groza 1.5" station and even its speed (but that is not certain). '
            '\nView status and run the bot: http://troposcatterbot.eu.pythonanywhere.com'
        ),
        'start_sosnik_pm': (
            '! This bot can calculate troposcatter link parameters '
            'for the "S-PM" station. '
            '\nView status and run the bot:'
            '\nhttp://stropobot.eu.pythonanywhere.com'
        ),
        'start_error': '! Bot operating mode is not defined',

        # Help
        'help_msg1': (
            'To start the calculation press the button '
            '{btn_calc_t}'
            ' and follow the instructions.\n\n'
            'Site names and their coordinates can be entered in one message '
            'or in several (in order).\n'
            'Coordinate input format — any, like ddd_mm_ss.s or ddd.d.\n\n'
            'Calculation is done for north latitude and east longitude '
            'unless otherwise specified in the given coordinates'
        ),
        'help_msg2': (
            'In the '
            '{btn_show_climate_zone}'
            ' menu you can find the climate correction value for the region.'
        ),

        # Reply keyboard button labels
        'btn_calc_t': '⚡️ Calculate path',
        'btn_show_climate_zone': '🌤 Show climate zones',
        'btn_show_bot_inf': '📗 Show information',
        'btn_next': '➡️ Next',
        'btn_back': '↩️ Back',
        'btn_climate_zones': '🌍 Climate zones map',
        'btn_bot_inf': '🤖 About Troposcatter bot',
        'btn_saved_sites': '🧭 Show saved sites',
        'btn_like': '',

        # Inline keyboard button labels
        'btn_use_file': 'Use',
        'btn_del_file': 'Delete',
        'btn_yes': 'Yes',
        'btn_no': 'No',
        'btn_set_heights': 'Set height',
        'btn_show_volume': 'Show scatter volume data',
        'btn_show_report': 'Show loss calculation',

        # Calc flow messages
        'enter_site_names': 'Enter site names: ',
        'add_another_site': 'Add another site?',
        'enter_next_site_name': 'Enter the next site name:',
        'enter_coords': 'Enter site coordinates:',
        'add_next_coords': 'Add coordinates for the next site?',
        'enter_next_coords': 'Enter coordinates for the next site:',
        'coords_entered_default_heights': (
            'Coordinates entered. Press "{btn_next}" '
            'to calculate with default heights (2m).'
        ),
        'or_set_heights': 'Or set custom antenna heights.',
        'found_coords_use_or_delete': (
            'Found coordinates for these sites! '
            'Use or delete these coordinates?'
        ),
        'coords_not_found': (
            'No saved data found for these sites. '
            'Enter coordinates: '
        ),
        'calculating_default': 'Calculating path with default heights...',
        'calculating': 'Calculating path...',
        'enter_height_for': (
            'Enter antenna height for site "{name}" (in meters):'
        ),
        'invalid_height': (
            'Invalid value. Please enter the height '
            'in meters (integer from 1 to 999).'
        ),
        'press_next_to_calc': 'Press button {btn_next} to start calculation',
        'use_saved_coords': (
            'Using saved coordinates. Press "{btn_next}" '
            'to calculate with default heights (2m).'
        ),
        'coords_deleted': 'Saved coordinates deleted. Enter coordinates: ',
        'delete_error': 'Delete error. Enter coordinates: ',
        'main_menu': 'Main menu: ',
        'enter_site_names_again': 'Enter site names again: ',

        # Bot info / saved sites
        'what_to_know': 'What would you like to know?',
        'know_coords_for': 'I know coordinates for these paths:',
        'sites_list_hidden': 'The list of saved sites is hidden!',
        'no_info': 'No information',
        'thanks': 'Thank you :)',
        'main_menu_label': 'Main menu',

        # Climate zone
        'climate_zone_info': (
            'Here you can download the climate zones map in .PDF format'
        ),
        'climate_map_caption': 'Climate zones map',
        'file_id_saved': (
            'File ID saved for faster loading.\n'
            'ID for env variable CLIMATE\\_ZONES\\_FILE\\_ID:\n{file_id}'
        ),

        # Volume / report view switching
        'volume_not_found': 'Scatter volume data not found.',
        'report_not_found': 'Report data not found.',

        # Sticker / file handlers
        'sticker_id': 'Here is your sticker id:\n{sticker_id}',
        'file_id': 'Here is your file id:\n{file_id}',

        # Wrong / unknown
        'bad_words_ru': 'Shame on you',
        'unknown_command': 'Unknown command',

        # Calculation report
        'latitude': 'Latitude: ',
        'longitude': 'Longitude: ',
        'extra_losses_hca': 'Additional path losses due to horizon close angles',
        'volume_data_unavailable': 'Scatter volume data is unavailable for this calculation.',
        'path_profile_caption': 'Path profile {name1} - {name2}',
        'profile_not_found': 'Path profile file not found.',
        'path_too_long': 'Path is too long for the API. Try reducing the distance between sites.',
        'elevation_error': 'Error retrieving elevation data. Please try again later.',
        'occurred_error': 'An error occurred: {error}',
        'load_coords_error': 'Could not load saved coordinates.',

        # Admin
        'admin_hello': "Hello, admin! It's tropobot.\n Press /stop to stop bot\n {mware_data}",
        'admin_button': 'Just button',
        'admin_troposcatter_calc': 'Troposcatter calculation',
        'admin_stopping': 'Stopping bot...',
        'admin_button_pressed': 'You pressed the button',
    },
}


def get_lang(language_code: str | None) -> str:
    """Resolve a Telegram language_code to a supported bot language.

    Any language_code that starts with 'ru' maps to Russian.
    All other codes (including None) fall back to English.
    """
    if language_code and language_code.startswith('ru'):
        return 'ru'
    return DEFAULT_LANG


def t_bot(key: str, lang: str = DEFAULT_LANG, **kwargs: object) -> str:
    """Return a translated bot UI string for the given language.

    Falls back to the DEFAULT_LANG translation if the requested lang is
    missing, and returns the raw key if no translation exists at all.
    """
    lang_map = TRANSLATIONS.get(lang) or TRANSLATIONS[DEFAULT_LANG]
    text = lang_map.get(key) or TRANSLATIONS[DEFAULT_LANG].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text
