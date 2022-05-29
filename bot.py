import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.filters.bad_words import BadWordsEN
from tgbot.filters.bad_words import BadWordsRU
from tgbot.handlers.admin import register_admin
from tgbot.handlers.calc_t_menu_buttons import register_calc_t_menu_buttons
from tgbot.handlers.calc_t_menu_sites import register_calc_t_menu_sites
from tgbot.handlers.climate_zone_menu import register_climate_zone_menu
from tgbot.handlers.error_handler import register_errors
from tgbot.handlers.file import register_file
from tgbot.handlers.my_id import register_my_id
from tgbot.handlers.show_bot_inf_menu import register_show_bot_inf_menu
from tgbot.handlers.start import register_start
from tgbot.handlers.sticker import register_sticker
from tgbot.handlers.wrong import register_wrong
from tgbot.middlewares.big_brother import BigBrother
from tgbot.middlewares.rate_limit import RateLimitMiddleware
from tgbot.misc.notify_admins import on_startup_notify, on_down_notify
from tgbot.misc.setting_comands import set_all_default_commands

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    dp.setup_middleware(RateLimitMiddleware())
    dp.setup_middleware(BigBrother())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(BadWordsEN)
    dp.filters_factory.bind(BadWordsRU)


def register_all_handlers(dp):
    register_admin(dp)
    register_start(dp)
    register_calc_t_menu_buttons(dp)
    register_calc_t_menu_sites(dp)
    register_climate_zone_menu(dp)
    register_show_bot_inf_menu(dp)
    register_my_id(dp)
    register_sticker(dp)
    register_file(dp)
    register_wrong(dp)
    register_errors(dp)


async def main():
    logging.basicConfig(
        # filename='log.txt',
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML', proxy=config.tg_bot.proxy)
    await bot.get_session()
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)
    await on_startup_notify(dp)
    await set_all_default_commands(bot)

    # start
    await set_all_default_commands(bot)

    try:
        await dp.start_polling()
    finally:

        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()
        await on_down_notify(dp)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
