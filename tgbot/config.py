from dataclasses import dataclass

from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str


@dataclass
class TgBot:
    token: str
    admin_ids: list[int]
    use_redis: bool
    proxy: str
    uptime_limit: float


@dataclass
class Miscellaneous:
    # other_params: str = None
    bad_words_ru: list = None
    bad_words_en: list = None
    c_zones_file_id: str = None


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    # Get bad ru and en words lists from file
    try:
        with open('tgbot/filters/badwords.txt', encoding='utf8') as f:
            bw_list = f.readlines()
    except FileNotFoundError:
        bw_list = []
    bw_list_ru = bw_list[0].replace('\n', '').split(', ')
    bw_list_en = bw_list[1].replace('\n', '').split(', ')

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
            proxy=env.str("PROXY_URL"),
            uptime_limit=env.float("UPTIME_LIMIT")
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME')
        ),
        misc=Miscellaneous(
            bad_words_ru=bw_list_ru,
            bad_words_en=bw_list_en,
            c_zones_file_id=env.str('CLIMATE_ZONES_FILE_ID')
        ),
    )
