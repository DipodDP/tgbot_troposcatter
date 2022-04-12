import typing

from aiogram.dispatcher.filters import BoundFilter


class BadWords(BoundFilter):
    key = 'bad_words'

    def __init__(self, bad_words: typing.Optional[bool] = None):
        self.bad_words = bad_words

    async def check(self, obj):
        if self.bad_words is None:
            return False
        # bwlist = list(map(str, badwords.txt.list("ADMINS")))
        bwlist = ["Хуй", "Хуев", "Хуё", "Блят", "Бляд", "Пизд", "Гандон", "Ебан", "Ёбан"]

        return (any(map(obj.text.lower().__contains__, map(str.lower, bwlist)))) == self.bad_words
