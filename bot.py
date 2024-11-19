import asyncio
import logging

from aiogram import Bot, Dispatcher, sys
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.utils.executor import start_webhook

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.filters.bad_words import BadWordsEN, BadWordsRU
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
from tgbot.misc.notify_admins import on_down_notify, on_startup_notify
from tgbot.misc.setting_comands import set_all_default_commands

WEBHOOK_PATH = "/webhook"

# webserver settings
WEBAPP_HOST = "localhost"  # or ip
WEBAPP_PORT = 5000


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


async def on_startup(dp):
    if url := dp.bot.get("config").tg_bot.webhook_host:
        await dp.bot.set_webhook(url + WEBHOOK_PATH)

    await set_all_default_commands(dp.bot)
    await on_startup_notify(dp)

    # insert code here to run it after start


async def on_shutdown(dp):
    logging.warning("Shutting down...")

    await on_down_notify(dp)
    await dp.bot.close()

    # Remove webhook (not acceptable in some cases)
    # await dp.bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    # insert code here to run it before shutdown

    logging.warning("Bye!")


def run_main(url=None):
    logging.basicConfig(
        # filename='log.txt',
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger.info("Starting bot")
    config = load_config(".env")
    setattr(config, "webhook_host", url)

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML", proxy=config.tg_bot.proxy)
    # await bot.get_session()
    # setattr(bot, 'config', config)
    bot["config"] = config

    dp = Dispatcher(bot, storage=storage)

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    if url or (url := config.tg_bot.webhook_host):
        logger.info(f"Using webhook: {url + WEBHOOK_PATH}")
        config.tg_bot.webhook_host = url

        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=config.tg_bot.webapp_host,
            port=config.tg_bot.webapp_port,
        )

    else:
        asyncio.run(main(dp, config))


async def main(dp, config):
    try:
        await on_startup(dp)
        # getting runtime limit in seconds
        uptime_limit = config.tg_bot.uptime_limit * 3600
        if uptime_limit != 0:
            await asyncio.wait_for(dp.start_polling(), timeout=uptime_limit)
        else:
            await dp.start_polling()

    except TimeoutError:
        pass

    finally:
        await on_shutdown(dp)


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            run_main(sys.argv[1])
        else:
            run_main()
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot stopped!")
    except RuntimeError as e:
        print(f"{e}")
