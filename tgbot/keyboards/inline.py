from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

use_file = InlineKeyboardMarkup(row_width=2,
                                inline_keyboard=[
                                    [
                                        InlineKeyboardButton(
                                            text='Использовать',
                                            callback_data='use_file'
                                        ),
                                        InlineKeyboardButton(
                                            text='Удалить',
                                            callback_data='del_file'
                                        )
                                    ]

                                ])

add_names = InlineKeyboardMarkup(row_width=2,
                                 inline_keyboard=[
                                     [
                                         InlineKeyboardButton(
                                             text='Да',
                                             callback_data='yes_names'
                                         ),
                                         InlineKeyboardButton(
                                             text='Нет',
                                             callback_data='no_names'
                                         )
                                     ]
                                 ])

add_coords = InlineKeyboardMarkup(row_width=2,
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(
                                              text='Да',
                                              callback_data='yes_coords'
                                          ),
                                          InlineKeyboardButton(
                                              text='Нет',
                                              callback_data='no_coords'
                                          )
                                      ]
                                  ])
