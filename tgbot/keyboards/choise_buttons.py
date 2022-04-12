from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.callback_datas import buy_callback

choice = InlineKeyboardMarkup(row_width=2,
                              inline_keyboard=[
                                  [
                                      InlineKeyboardButton(
                                          text='Buy sweet pear',
                                          callback_data=buy_callback.new(item_name='pear', quantity=1)),
                                      InlineKeyboardButton(
                                          text='Buy red apples',
                                          callback_data='buy:apple:5',
                                      )
                                  ],
                                  [
                                      InlineKeyboardButton(
                                          text='Cancel your buys',
                                          callback_data='cancel'
                                      )
                                  ]
                              ])
pear_keyboard = InlineKeyboardMarkup()

PEAR_LINK = 'https://www.ozon.ru/product/grusha-konferentsiya-krupnaya-otbornaya-500-g-248896976/?sh=NyQ_epTaEw'

pear_link = InlineKeyboardButton(text="Buy here", url=PEAR_LINK)
pear_keyboard.insert(pear_link)
