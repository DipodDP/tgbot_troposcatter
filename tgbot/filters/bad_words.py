import typing

from aiogram.dispatcher.filters import BoundFilter

from tgbot.config import Config


class BadWordsRU(BoundFilter):
    key = 'bad_words_ru'

    def __init__(self, bad_words_ru: typing.Optional[bool] = None):
        self.bad_words_ru = bad_words_ru

    async def check(self, obj):
        config: Config = obj.bot.get('config')
        bw_list_ru = config.misc.bad_words_ru

        if self.bad_words_ru is None:
            return False

        return (any(map(obj.text.lower().__contains__, map(str.lower, bw_list_ru)))) == self.bad_words_ru


class BadWordsEN(BoundFilter):
    key = 'bad_words_en'

    def __init__(self, bad_words_en: typing.Optional[bool] = None):
        self.bad_words_en = bad_words_en

    async def check(self, obj):
        config: Config = obj.bot.get('config')
        bw_list_en = config.misc.bad_words_en

        if self.bad_words_en is None:
            return False

        return (any(map(obj.text.lower().__contains__, map(str.lower, bw_list_en)))) == self.bad_words_en
