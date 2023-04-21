from dataclasses import dataclass
from pathlib import Path
from environs import Env


@dataclass
class DbConfig:
    host: str | None = None
    password: str | None = None
    user: str | None = None
    database: str | None = None


@dataclass
class TgBot:
    token: str
    bot_mode: int
    admin_ids: list[int]
    use_redis: bool
    proxy: str
    uptime_limit: float


@dataclass
class Miscellaneous:
    bad_words_ru: list | None = None
    bad_words_en: list | None = None
    c_zones_file_id: str | None = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str | None = None):
    env = Env()
    env.read_env(path)

    # Get bad ru and en words lists from file
    try:
        with open(Path(Path.cwd(), 'tgbot', 'filters', 'badwords.txt'), encoding='utf8') as f:
            bw_list = f.readlines()
            bw_list_ru = bw_list[0].replace('\n', '').split(', ')
            bw_list_en = bw_list[1].replace('\n', '').split(', ')
    except (FileNotFoundError, IndexError):
        bw_list_ru = []
        bw_list_en = []

    return Config(
        tg_bot = TgBot(
            bot_mode = env.int("BOT_MODE"),
            token = env.str("BOT_TOKEN"),
            admin_ids = list(map(int, env.list("ADMINS"))),
            use_redis = env.bool("USE_REDIS"),
            proxy = env.str("PROXY_URL"),
            uptime_limit = env.float("UPTIME_LIMIT")
        ),
        db = DbConfig(
            host = env.str('DB_HOST'),
            password = env.str('DB_PASS'),
            user = env.str('DB_USER'),
            database = env.str('DB_NAME')
        ),
        misc = Miscellaneous(
            bad_words_ru = bw_list_ru,
            bad_words_en = bw_list_en,
            c_zones_file_id = env.str('CLIMATE_ZONES_FILE_ID')
        ),
    )
