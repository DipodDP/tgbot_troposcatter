import logging
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters import ChatTypeFilter

from tgbot.i18n import t_bot
from tgbot.keyboards.inline import get_show_volume_keyboard, get_show_report_keyboard
from tgbot.misc.states import CalcMenuStates

logger = logging.getLogger(__name__)


async def switch_view(call: CallbackQuery, state: FSMContext, lang: str = 'en'):
    await call.answer()

    async with state.proxy() as data:
        current_view = data.get('current_view', 'report')

        if call.data == 'show_volume' and current_view == 'report':
            volume_text = data.get('volume_view_text')
            if volume_text:
                await call.message.edit_text(
                    volume_text,
                    reply_markup=get_show_report_keyboard(lang),
                    parse_mode='MarkdownV2',
                )
                data['current_view'] = 'volume'
            else:
                await call.answer(
                    t_bot('volume_not_found', lang), show_alert=True
                )
                logger.warning(
                    f'volume_view_text not found in state for user {call.from_user.id}'
                )

        elif call.data == 'show_report' and current_view == 'volume':
            report_text = data.get('report_view_text')
            if report_text:
                await call.message.edit_text(
                    report_text,
                    reply_markup=get_show_volume_keyboard(lang),
                    parse_mode='MarkdownV2',
                )
                data['current_view'] = 'report'
            else:
                await call.answer(t_bot('report_not_found', lang), show_alert=True)
                logger.warning(
                    f'report_view_text not found in state for user {call.from_user.id}'
                )


def register_view_switch_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        switch_view,
        ChatTypeFilter(types.ChatType.PRIVATE),
        lambda c: c.data in ['show_report', 'show_volume'],
        state=[CalcMenuStates.got_s_coords, CalcMenuStates.got_s_heights],
    )
