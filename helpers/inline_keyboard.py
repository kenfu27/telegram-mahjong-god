import json

from sqlalchemy.orm import joinedload
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from db import get_db_session, DB
from schema import Game, PRICE_LIST
from strings import String


def send_seat_select_keyboard(bot, game_id, text, parse_mode=None, message=None):
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
        bot.editMessageText(text=text,
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                            parse_mode=parse_mode,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons))
    else:
        # Send New Keyboard
        bot.send_message(text=text,
                         chat_id=game.chat_id,
                         parse_mode=parse_mode,
                         reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons))


def send_player_select_keyboard(bot, game_id, event_id, action, chat_id, text, parse_mode=None, exclude_id=None,
                                message=None):
    """
    :type bot: telegram.bot.Bot
    :type game_id: int
    :type event_id: int
    :type action: str
    :type chat_id: int
    :type text: str | unicode
    :type parse_mode: str
    :type exclude_id: str | unicode | set | list
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

            callback_data = json.dumps(
                {'a': action, 'e': event_id, 't': player.username})

            inline_keyboard_buttons.append([
                InlineKeyboardButton(text=btn_text, callback_data=callback_data)
            ])

    inline_keyboard_buttons.append([
        InlineKeyboardButton(text=String.CANCEL, callback_data=json.dumps(
            {'a': String.ACTION_EVENT_CANCEL, 'e': int(event_id)}))])

    if message:
        # Update Existing Keyboard
        bot.editMessageText(text=text,
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                            parse_mode=parse_mode,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons))
    else:
        # Send New Keyboard
        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=parse_mode,
                         reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons))


def send_fan_select_keyboard(bot, game_id, event_id, action, chat_id, text, parse_mode=None, message=None):
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
        bot.editMessageText(text=text,
                            chat_id=message.chat_id,
                            message_id=message.message_id,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons))
    else:
        # Send New Keyboard
        bot.send_message(chat_id=chat_id,
                         text=text,
                         parse_mode=parse_mode,
                         reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons))
