import logging

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from tgbot.i18n import get_lang
from trace_calc.infrastructure.i18n import set_language


class BigBrother(BaseMiddleware):
    # async def on_point_event_type:
    # 1
    async def on_pre_process_update(self, update: types.Update, data: dict):
        logging.debug('---------------New_update---------------')
        logging.debug('1. pre process update')
        logging.debug('Next: process update')
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
        logging.debug(f'2. process update {data=}')
        logging.debug('Next: pre process message')

    # 3
    async def on_pre_process_message(self, message: types.Message, data: dict):
        logging.debug(f'3. preprocess message {data=}')
        logging.debug('Next: filters, process message')
        data['mware_data'] = "Send to on_process_message"

        lang = get_lang(
            message.from_user.language_code if message.from_user else None
        )
        logging.debug(
            f"Message from user_id={message.from_user.id if message.from_user else 'unknown'}, "
            f"client_language_code={message.from_user.language_code if message.from_user else 'None'}, "
            f"resolved_lang={lang}"
        )
        data['lang'] = lang
        set_language(lang)

    # 4 filters
    # 5
    async def on_process_message(self, message: types.Message, data: dict):
        logging.debug(f'5. process message')
        logging.debug('Next: handler')
        data['mware_data'] = "Send to hadnler"

    # 6 handler
    # 7
    async def on_post_process_message(self, message: types.Message, data_from_handler: list, data: dict):
        logging.debug(f'7. post process message{data=}{data_from_handler=}')
        logging.debug('Next: post process update')
        data['mware_data'] = "Send to hadnler"

    # 8
    async def on_post_process_update(self, update: types.Update, data_from_handler: list, data: dict):
        logging.debug(f'8. post process update{data=}, {data_from_handler=}')
        logging.debug('-----------------Exit-----------------')

    # Get rid of clocks on inline buttons + inject language
    async def on_pre_process_callback_query(self, cq: types.CallbackQuery, data: dict):
        lang = get_lang(cq.from_user.language_code if cq.from_user else None)
        logging.debug(
            f"CallbackQuery from user_id={cq.from_user.id if cq.from_user else 'unknown'}, "
            f"client_language_code={cq.from_user.language_code if cq.from_user else 'None'}, "
            f"resolved_lang={lang}"
        )
        data['lang'] = lang
        set_language(lang)
        await cq.answer()
