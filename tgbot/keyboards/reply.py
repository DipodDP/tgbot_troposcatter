# main menu
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

btn_calc_t = KeyboardButton('⚡️ Рассчитать трассу')
btn_show_climate_zone = KeyboardButton('🌤 Показать климатические зоны')
btn_show_bot_inf = KeyboardButton('📗 Показать информацию')
main_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    btn_calc_t, btn_show_climate_zone, btn_show_bot_inf
)

btn_next = KeyboardButton('➡️ Дальше')
btn_back = KeyboardButton('↩️ Назад')

# calc troposcatter menu
calc_t_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    btn_next, btn_back
)

# climate menu
btn_climate_zones = KeyboardButton('🌍 Карта климатических зон')
climate_zone_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    btn_climate_zones, btn_back
)

# bot info menu
btn_bot_inf = KeyboardButton('🤖 About Troposcatter bot')
# btn_like = KeyboardButton('❤️ Лайк!')
btn_like = KeyboardButton('')
btn_saved_sites = KeyboardButton('🧭 Показать сохраненные точки')
bot_inf_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    btn_saved_sites, btn_bot_inf, btn_like, btn_back
)
