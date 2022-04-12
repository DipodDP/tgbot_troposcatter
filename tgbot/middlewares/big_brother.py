import logging

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class BigBrother(BaseMiddleware):
    # async def on_point_event_type:
    # 1
    async def on_pre_process_update(self, update: types.Update, data: dict):
        logging.info('---------------New_update---------------')
        logging.info('1. pre process update')
        logging.info('Next: process update')
        data['mware_data'] = "Send to on_post_process_update"

        banned_users = []
        if update.message:
            user = update.message.from_user.id
        elif update.callback_query:
            user = update.callback_query.from_user.id

        else:
            return

        if user in banned_users:
            raise CancelHandler()

    # 2
    async def on_process_update(self, update: types.Update, data: dict):
        logging.info(f'2. process update {data=}')
        logging.info('Next: pre process message')

    # 3
    async def on_pre_process_message(self, message: types.Message, data: dict):
        logging.info(f'3. preprocess message {data=}')
        logging.info('Next: filters, process message')
        data['mware_data'] = "Send to on_process_message"

    # 4 filters
    # 5
    async def on_process_message(self, message: types.Message, data: dict):
        logging.info(f'5. process message')
        logging.info('Next: handler')
        data['mware_data'] = "Send to hadnler"

    # 6 handler
    # 7
    async def on_post_process_message(self, message: types.Message, data_from_handler: list, data: dict):
        logging.info(f'7. post process message{data=}{data_from_handler=}')
        logging.info('Next: post process update')
        data['mware_data'] = "Send to hadnler"

    # 8
    async def on_post_process_update(self, update: types.Update, data_from_handler: list, data: dict):
        logging.info(f'8. post process update{data=}, {data_from_handler=}')
        logging.info('-----------------Exit-----------------')

    # Get rid of clocks on inline buttons
    async def on_pre_process_callback_query(self, cq: types.CallbackQuery, data: dict):
        await cq.answer()
