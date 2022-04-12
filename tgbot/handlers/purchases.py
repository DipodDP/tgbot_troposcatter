import logging

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.callback_datas import buy_callback
from tgbot.keyboards.choise_buttons import choice, pear_keyboard


async def purchases(message: Message):
    await message.answer('Buy what you want \n'
                         'Or you may cancel your order', reply_markup=choice)


async def buying_pear(call: CallbackQuery, callback_data: dict):
    # await call.bot.answer_callback_query(callback_query_id=call.id) simple equivalent:
    await call.answer(cache_time=60)
    logging.info(f'Callback data = {call.data}')
    logging.info(f'Callback data dict = {callback_data}')
    quantity = callback_data.get('quantity')
    await call.message.answer(f'Your choice is {quantity} of pears.', reply_markup=pear_keyboard)


async def buying_apple(call: CallbackQuery, callback_data: dict):
    await call.answer(cache_time=60)
    logging.info(f'Callback data = {call.data}')
    logging.info(f'Callback data dict = {callback_data}')
    quantity = callback_data.get('quantity')
    await call.message.answer(f'Your choice is {quantity} of apples.')


async def cancel(call: CallbackQuery):
    await call.answer('You cancelled your order', show_alert=True)
    await call.message.edit_reply_markup()


def register_purchase(dp: Dispatcher):
    dp.register_message_handler(purchases, Command('item'))
    dp.register_callback_query_handler(buying_pear, buy_callback.filter(item_name='pear'))
    dp.register_callback_query_handler(buying_apple, buy_callback.filter(item_name='apple'))
    dp.register_callback_query_handler(cancel, text='cancel')
