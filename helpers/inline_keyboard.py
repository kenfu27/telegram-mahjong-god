import json

import datetime
from sqlalchemy.orm import joinedload
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from db import get_db_session, DB
from helpers.game import get_event_description
from schema import Game, PRICE_LIST, EventType
from strings import String


def send_seat_select_keyboard(bot, game_id, text, parse_mode=None, message=None, disable_notification=True):
    """
    :type bot: telegram.bot.Bot
    :type game_id: int
    :type text: str | unicode
    :type parse_mode: str
    :type message: telegram.message.Message
    :return:
    """
    session = get_db_session()

    game = DB.get_game(session, game_id=game_id,
                       options=[joinedload(Game.player_1),
                                joinedload(Game.player_2),
                                joinedload(Game.player_3),
                                joinedload(Game.player_4)])

    inline_keyboard_buttons = []

    for i in range(1, 5):
        player = game.__getattribute__('player_{0}'.format(i))

        btn_text = String.__dict__.get('SEAT_{0}'.format(i)) + u' - ' + (
            (player.first_name + u" " + player.last_name) if player else String.NO_ONE)

        callback_data = json.dumps({'a': String.ACTION_SELECT_SEAT, 'g': int(game.id), 'seat': i})

        inline_keyboard_buttons.append([InlineKeyboardButton(text=btn_text, callback_data=callback_data)])

    inline_keyboard_buttons.append([InlineKeyboardButton(String.START_GAME, callback_data=json.dumps(
        {'a': String.ACTION_START_GAME, 'g': int(game.id)}))])

    if message:
        # Update Existing Keyboard
        bot.editMessageText(timeout=5, text=text,
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                            parse_mode=parse_mode,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons),
                            disable_notification=disable_notification)
    else:
        # Send New Keyboard
        bot.sendMessage(text=text,
                        chat_id=game.chat_id,
                        parse_mode=parse_mode,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons),
                        disable_notification=disable_notification,
                        timeout=5)


def send_player_select_keyboard(bot, game_id, event_id, action, chat_id, text, parse_mode=None, exclude_id=None,
                                reply_to_message_id=None, message=None, disable_notification=True):
    """
    :type bot: telegram.bot.Bot
    :type game_id: int
    :type event_id: int
    :type action: str
    :type chat_id: int
    :type text: str | unicode
    :type parse_mode: str
    :type exclude_id: str | unicode | set | list
    :type reply_to_message_id: int
    :type message: telegram.message.Message
    """

    if not exclude_id:
        exclude_id = set()
    if isinstance(exclude_id, (str, unicode)):
        exclude_id = {exclude_id}

    session = get_db_session()

    game = DB.get_game(session, game_id=game_id,
                       options=[joinedload(Game.player_1),
                                joinedload(Game.player_2),
                                joinedload(Game.player_3),
                                joinedload(Game.player_4)])

    inline_keyboard_buttons = []

    for i in range(1, 5):
        player = game.__getattribute__('player_{0}'.format(i))

        if player and player.username not in exclude_id:
            btn_text = u'{0} {1}'.format(player.first_name, player.last_name)

            callback_data = json.dumps({'a': action, 'e': event_id, 't': player.username})

            inline_keyboard_buttons.append([
                InlineKeyboardButton(text=btn_text, callback_data=callback_data)
            ])

    inline_keyboard_buttons.append([
        InlineKeyboardButton(text=String.CANCEL, callback_data=json.dumps(
            {'a': String.ACTION_EVENT_CANCEL, 'e': int(event_id)}))])

    if message:
        # Update Existing Keyboard
        bot.editMessageText(timeout=5, text=text,
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                            parse_mode=parse_mode,
                            reply_to_message_id=reply_to_message_id,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons),
                            disable_notification=disable_notification)
    else:
        # Send New Keyboard
        bot.sendMessage(chat_id=chat_id,
                        text=text,
                        parse_mode=parse_mode,
                        reply_to_message_id=reply_to_message_id,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons),
                        disable_notification=disable_notification,
                        timeout=5)


def send_fan_select_keyboard(bot, game_id, event_id, action, chat_id, text, parse_mode=None, message=None,
                             disable_notification=True):
    """
    
    :type bot: telegram.bot.Bot
    :type game_id: int
    :type event_id: int
    :type action: str
    :type chat_id: int
    :type text: str | unicode
    :type parse_mode: str
    :type message: telegram.message.Message
    :return: 
    """
    session = get_db_session()

    game = DB.get_game(session, game_id=game_id)

    prices = PRICE_LIST.get(game.price, None)

    inline_keyboard_buttons = []

    for fan, price in prices.iteritems():
        btn_text = u'{0} {1}'.format(String.__dict__.get('FAN_{0}'.format(fan)), price)
        callback_data = json.dumps({'a': action, 'e': event_id, 'f': fan})

        inline_keyboard_buttons.append([
            InlineKeyboardButton(text=btn_text, callback_data=callback_data)
        ])

    inline_keyboard_buttons.append([
        InlineKeyboardButton(text=String.CANCEL, callback_data=json.dumps(
            {'a': String.ACTION_EVENT_CANCEL, 'e': event_id}))])

    if message:
        # Update Existing Keyboard
        bot.editMessageText(timeout=5, text=text,
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons),
                            disable_notification=disable_notification)
    else:
        # Send New Keyboard
        bot.sendMessage(chat_id=chat_id,
                        text=text,
                        parse_mode=parse_mode,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons),
                        disable_notification=disable_notification,
                        timeout=5)


def send_game_select_keyboard(bot, chat_id, text, action, games, message=None, disable_notification=False):
    """
    :type bot: telegram.bot.Bot
    :type chat_id: int
    :type text:
    :type action: str
    :type games: list[schema.Game]
    :param message:
    :param disable_notification:
    """
    inline_keyboard_buttons = []

    for game in games:
        date_str = datetime.datetime.fromtimestamp(
            int(game.end_date)
        ).strftime('%Y-%m-%d')

        player_str = u','.join([
                                   game.__getattribute__('player_{0}'.format(i)).first_name + u' '
                                   + game.__getattribute__('player_{0}'.format(i)).last_name
                                   for i in range(1, 5)])

        btn_text = u'{0} - {1}'.format(date_str, player_str)

        callback_data = json.dumps({'a': action, 'g': game.id})

        inline_keyboard_buttons.append([
            InlineKeyboardButton(text=btn_text, callback_data=callback_data)
        ])

    cancel_btn = InlineKeyboardButton(text=String.CANCEL, callback_data=json.dumps({'a': String.ACTION_CANCEL}))

    inline_keyboard_buttons.append([cancel_btn])

    if message:
        bot.editMessageText(timeout=5, chat_id=message.chat_id,
                            message_id=message.message_id,
                            text=text,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons),
                            disable_notification=disable_notification)
    else:
        bot.sendMessage(chat_id=chat_id,
                        text=text,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons),
                        disable_notification=disable_notification,
                        timeout=5)


def send_event_select_keyboard(bot, chat_id, text, event_id, action, events, message=None):
    """
    :type bot: telegram.bot.Bot
    :type chat_id: int
    :type text:
    :type event_id: int
    :type action: str
    :type events: list[schema.Event]
    :type message: 
    :return: 
    """
    inline_keyboard_buttons = []

    for event in events:
        if event.type not in [EventType.DELETE, EventType.END, EventType.NEW_GAME]:
            btn_text = get_event_description(event)

            callback_data = json.dumps({'a': action, 't': event.id, 'e': event_id})

            inline_keyboard_buttons.append([
                InlineKeyboardButton(text=btn_text, callback_data=callback_data)
            ])

    cancel_btn = InlineKeyboardButton(text=String.CANCEL,
                                      callback_data=json.dumps({'a': String.ACTION_CANCEL, 'e': event_id}))

    inline_keyboard_buttons.append([cancel_btn])

    if message:
        bot.editMessageText(timeout=5, chat_id=message.chat_id,
                            message_id=message.message_id,
                            text=text,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons))
    else:
        bot.sendMessage(chat_id=chat_id,
                        text=text,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons),
                        timeout=5)


def send_wind_select_keyboard(bot, chat_id, text, event_id, action, message=None):
    """
    :type bot: telegram.bot.Bot
    :type chat_id: int
    :type text:
    :type event_id: int
    :type action: str
    :type message:
    :return:
    """
    inline_keyboard_buttons = []

    for i in range(1, 5):
        btn_text = String.__dict__.get('SEAT_{0}'.format(i))

        callback_data = json.dumps({'a': action, 'e': event_id, 't': i})

        inline_keyboard_buttons.append([
            InlineKeyboardButton(text=btn_text, callback_data=callback_data)
        ])

    cancel_btn = InlineKeyboardButton(text=String.CANCEL,
                                      callback_data=json.dumps({'a': String.ACTION_CANCEL, 'e': event_id}))

    inline_keyboard_buttons.append([cancel_btn])

    if message:
        bot.editMessageText(timeout=5, chat_id=message.chat_id,
                            message_id=message.message_id,
                            text=text,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons))
    else:
        bot.sendMessage(chat_id=chat_id,
                        text=text,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons),
                        timeout=5)
