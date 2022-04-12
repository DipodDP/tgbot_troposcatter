from aiogram import Dispatcher
from aiogram.types import Message


async def get_my_id(message: Message):
    await message.reply("Your ID: " + str(message.from_user.id))


def register_my_id(dp: Dispatcher):
    dp.register_message_handler(get_my_id, commands=["my_id"], state="*")