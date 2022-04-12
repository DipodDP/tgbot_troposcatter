from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Command

from tgbot.misc.allow_access import allow_access
from tgbot.models.models import User


@allow_access()
async def block_me(message: types.Message, user: User):
    await message.answer(f"User block status: {user.allowed}. Now access deny.\n"
                         f"Comand to unblock: /unblock_me")
    user.block()


@allow_access()
async def unblock_me(message: types.Message, user: User):
    await message.answer(f"User block status: {user.allowed}. Now access granted. \n"
                         f"Comand to block: /block_me")
    user.allow()


def register_acl_test(dp: Dispatcher):
    dp.register_message_handler(block_me, Command('block_me'), state="*", is_admin=False)
    dp.register_message_handler(unblock_me, Command('unblock_me'), state="*", is_admin=False)
