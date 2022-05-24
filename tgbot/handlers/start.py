from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.types import Message

from tgbot.keyboards.reply import btn_calc_t, btn_show_climate_zone, main_menu
from tgbot.misc.rate_limit import rate_limit


@rate_limit(5, key='start')
async def user_start(message: Message):
    answer_message = '  Привет, ' + message.chat.first_name + '! Этот бот может рассчитать параметры тропосферной линии ' \
                                                            'для станции "Гроза 1,5" и, даже, её скорость (но это не ' \
                                                            'точно). '
    # bot.send_message(message.chat.id, answer_message, reply_markup=mainMenu)
    await message.bot.send_message(message.chat.id, answer_message, reply_markup=main_menu)


@rate_limit(5, key='help')
async def user_help(message: Message):
    answer_message1 = ' Для начала расчета нажмите кнопку ' + btn_calc_t.text +\
                      ' и следуйте инструкциям.\n\n' \
                      '   Названия точек и их координаты можно вводить в одном сообщении' \
                      ' или в нескольких (попорядку).\n' \
                      ' Формат ввода координат - любой'
    answer_message2 = ' В меню ' + btn_show_climate_zone.text +\
                      ' можно узнать значение климатической поправки для региона.'
    await message.bot.send_message(message.chat.id, answer_message1, reply_markup=main_menu)
    await message.bot.send_message(message.chat.id, answer_message2, reply_markup=main_menu)


def register_start(dp: Dispatcher):
    dp.register_message_handler(user_start, CommandStart(), state='*')
    dp.register_message_handler(user_help, Command('help'), state='*')
