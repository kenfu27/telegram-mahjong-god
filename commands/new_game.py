import codecs
import json

from telegram import Chat
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from commands import MJGCommands
from db import get_db_session, DB
from helpers.game import get_player_seat_no, get_game_player_no
from helpers.inline_keyboard import send_seat_select_keyboard
from schema import GameStatus, EventType
from strings import String


@MJGCommands.command('new_game')
def new_game(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    chat = update.message.chat

    if chat.type == Chat.PRIVATE:
        bot.sendMessage(update.message.chat_id, String.ERROR_PRIVATE_CHAT, timeout=5)
    else:
        user = update.message.from_user
        session = get_db_session()

        if DB.is_user_registered(session, user):
            player = DB.get_player(session, user.username)

            existing_game = DB.get_player_current_game(session, user)

            if existing_game:
                bot.sendMessage(chat_id=update.message.chat_id,
                                text=String.ERROR_EXISTING_GAME.format(user.first_name, user.last_name),
                                reply_to_message_id=update.message.message_id,
                                timeout=5)
            else:
                game = DB.create_game(session, chat_id=chat.id, player_1_id=user.username)

                event = DB.create_event(session,
                                        game_id=game.id,
                                        message_id=update.message.message_id,
                                        type=EventType.NEW_GAME,
                                        created_by=user.username)

                inline_keyboard_buttons = [
                    InlineKeyboardButton(String.PRICE_8f64, callback_data=json.dumps(
                        {'a': String.ACTION_ASK_PRICE, 'g': int(game.id), 'p': '8f64', 'e': event.id})),
                    InlineKeyboardButton(String.PRICE_8f128, callback_data=json.dumps(
                        {'a': String.ACTION_ASK_PRICE, 'g': int(game.id), 'p': '8f128', 'e': event.id})),
                    InlineKeyboardButton(String.PRICE_10f128, callback_data=json.dumps(
                        {'a': String.ACTION_ASK_PRICE, 'g': int(game.id), 'p': '10f128', 'e': event.id})),
                    InlineKeyboardButton(String.PRICE_10f256, callback_data=json.dumps(
                        {'a': String.ACTION_ASK_PRICE, 'g': int(game.id), 'p': '10f256', 'e': event.id}))
                ]

                bot.sendMessage(chat_id=game.chat_id, text=String.START_GAME_ASK_PRICE,
                                reply_markup=InlineKeyboardMarkup([inline_keyboard_buttons]),
                                timeout=5)
        else:
            update.message.reply_text(String.ERROR_NOT_REGISTERED)


@MJGCommands.callback(String.ACTION_ASK_PRICE)
def ask_price_callback(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    current_user = update.callback_query.from_user
    data = json.loads(update.callback_query.data)
    session = get_db_session()
    event_id = data['e']
    event = DB.get_event(session, event_id=event_id)

    if event and not event.completed and current_user.username == event.created_by:
        price = data['p']
        DB.update_game(session,
                       game_id=event.game_id,
                       update_dict={'price': price, 'status': GameStatus.WAITING_FOR_PLAYER})
        bot.editMessageText(timeout=5, text=String.__dict__.get('PRICE_' + price),
                            chat_id=update.callback_query.message.chat_id,
                            message_id=update.callback_query.message.message_id)

        with codecs.open('templates/wait_for_players.html', 'r', 'utf-8') as f:
            html = f.read().format(String.__dict__.get('PRICE_' + price), String.START_GAME_SELECT_SEAT)

        send_seat_select_keyboard(bot, game_id=event.game_id, text=html, parse_mode='HTML')


@MJGCommands.callback(String.ACTION_SELECT_SEAT)
def select_seat_callback(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    session = get_db_session()

    data = json.loads(update.callback_query.data)
    game = DB.get_game(session, data['g'])

    if game:
        user = update.callback_query.from_user
        if DB.is_user_registered(session, user):
            seat_no = data['seat']
            existing_seat_no = get_player_seat_no(user, game)
            seated_player = game.__getattribute__('player_{0}_id'.format(seat_no))
            current_game = DB.get_player_current_game(session, user)
            if current_game and current_game.id != game.id:
                # Player has another active game
                extra_msg = String.ERROR_EXISTING_GAME.format(user.first_name, user.last_name)
            elif seated_player:
                if seated_player == user.username:
                    # Player already sitting at that seat
                    update_dict = {'player_{0}_id'.format(existing_seat_no): None}
                    DB.update_game(session, game.id, update_dict)
                    extra_msg = String.ERROR_SAME_SEAT.format(user.first_name, user.last_name)
                else:
                    # Seat has already been taken by other player
                    extra_msg = String.ERROR_SEAT_TAKEN.format(user.first_name, user.last_name)
            elif existing_seat_no:
                # Change Seat
                update_dict = {'player_{0}_id'.format(existing_seat_no): None,
                               'player_{0}_id'.format(seat_no): user.username}
                DB.update_game(session, game.id, update_dict)
                extra_msg = String.START_GAME_CHANGE_SEAT.format(user.first_name,
                                                                 user.last_name,
                                                                 String.__dict__.get('SEAT_{0}'.format(seat_no)),
                                                                 String.__dict__.get(
                                                                     'SEAT_{0}'.format(existing_seat_no)))
            else:
                # Normal Sit
                update_dict = {'player_{0}_id'.format(seat_no): user.username}
                DB.update_game(session, game.id, update_dict)
                extra_msg = String.START_GAME_CHOSE_SEAT.format(user.first_name,
                                                                user.last_name,
                                                                String.__dict__.get('SEAT_{0}'.format(seat_no)))

            with codecs.open('templates/wait_for_players.html', 'r', 'utf-8') as f:
                html = f.read().format(String.__dict__.get('PRICE_' + game.price), extra_msg)
        else:
            with codecs.open('templates/wait_for_players.html', 'r', 'utf-8') as f:
                html = f.read().format(String.__dict__.get('PRICE_' + game.price), String.ERROR_NOT_REGISTERED)

        send_seat_select_keyboard(bot, game_id=game.id, text=html, parse_mode='HTML',
                                  message=update.callback_query.message)


@MJGCommands.callback(String.ACTION_START_GAME)
def start_game(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    data = json.loads(update.callback_query.data)

    session = get_db_session()

    game = DB.get_game(session, data['g'])

    if game:
        if get_game_player_no(game) == 4:
            update_dict = {'status': GameStatus.STARTED, 'set_no': 1, 'round_no': 1}
            DB.update_game(session, game.id, update_dict)

            with codecs.open('templates/game_start.html', 'r', 'utf-8') as f:
                html = f.read()

            bot.editMessageText(timeout=5, text=html, chat_id=game.chat_id,
                                message_id=update.callback_query.message.message_id,
                                parse_mode='HTML', reply_markup=None)
        else:
            extra_msg = String.ERROR_NOT_ENOUGH_PLAYER

            with codecs.open('templates/wait_for_players.html', 'r', 'utf-8') as f:
                html = f.read().format(String.__dict__.get('PRICE_' + game.price), extra_msg)

            send_seat_select_keyboard(bot, game_id=game.id, text=html, parse_mode='HTML',
                                      message=update.callback_query.message)


@MJGCommands.callback(String.ACTION_CANCEL_GAME)
def cancel_game(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    current_user = update.callback_query.from_user
    data = json.loads(update.callback_query.data)
    session = get_db_session()
    game_id = data['g']

    game = DB.get_game(session, game_id=game_id)

    if game and game.status == GameStatus.WAITING_FOR_PLAYER and get_player_seat_no(current_user, game):
        DB.delete_game(session, game_id=game_id)

        bot.editMessageText(text=String.CANCEL_GAME_MESSAGE, chat_id=update.callback_query.message.chat_id,
                            message_id=update.callback_query.message.message_id)
