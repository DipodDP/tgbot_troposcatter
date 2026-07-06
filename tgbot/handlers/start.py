from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.types import Message

from tgbot.i18n import t_bot
from tgbot.keyboards.reply import ALL_BTN_BACK, get_main_menu
from tgbot.misc.rate_limit import rate_limit


@rate_limit(5, key='start')
async def user_start(message: Message, lang: str = 'en'):
    bot_mode = message.bot['config'].tg_bot.bot_mode

    match bot_mode:
        case 0:
            answer_message = (
                t_bot('hello', lang) + message.chat.first_name + t_bot('start_groza', lang)
            )
        case 1:
            answer_message = (
                t_bot('hello', lang) + message.chat.first_name + t_bot('start_sosnik_pm', lang)
            )
        case _:
            answer_message = (
                t_bot('hello', lang) + message.chat.first_name + t_bot('start_error', lang)
            )

    await message.bot.send_message(
        message.chat.id, answer_message, reply_markup=get_main_menu(lang)
    )


async def user_help(message: Message, lang: str = 'en'):
    btn_calc_t = t_bot('btn_calc_t', lang)
    btn_show_climate_zone = t_bot('btn_show_climate_zone', lang)
    help1 = t_bot('help_msg1', lang, btn_calc_t=btn_calc_t)
    help2 = t_bot('help_msg2', lang, btn_show_climate_zone=btn_show_climate_zone)
    await message.bot.send_message(message.chat.id, help1, reply_markup=get_main_menu(lang))
    await message.bot.send_message(message.chat.id, help2, reply_markup=get_main_menu(lang))


def register_start(dp: Dispatcher):
    dp.register_message_handler(user_start, CommandStart(), state='*')
    dp.register_message_handler(user_help, Command('help'), state='*')
