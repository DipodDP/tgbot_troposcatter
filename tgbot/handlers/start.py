from aiogram import Dispatcher
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.types import Message
from .answer_messages import user_start_message_groza, user_start_message_sosnik_pm, user_start_message_error, user_help_message1, user_help_message2
from tgbot.keyboards.reply import main_menu
from tgbot.misc.rate_limit import rate_limit


@rate_limit(5, key='start')
async def user_start(message: Message):
   
    bot_mode = message.bot['config'].tg_bot.bot_mode

    match bot_mode:
        case 0:
            answer_message = 'Привет, ' + message.chat.first_name + user_start_message_groza
        case 1:
            answer_message = 'Привет, ' + message.chat.first_name + user_start_message_sosnik_pm
        case _:
            answer_message = 'Привет, ' + message.chat.first_name + user_start_message_error

    await message.bot.send_message(message.chat.id, answer_message, reply_markup=main_menu)


async def user_help(message: Message):
    await message.bot.send_message(message.chat.id, user_help_message1, reply_markup=main_menu)
    await message.bot.send_message(message.chat.id, user_help_message2, reply_markup=main_menu)


def register_start(dp: Dispatcher):
    dp.register_message_handler(user_start, CommandStart(), state='*')
    dp.register_message_handler(user_help, Command('help'), state='*')
