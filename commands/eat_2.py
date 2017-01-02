import json
import random

from commands import MJGCommands
from db import DB
from db import get_db_session
from helpers.game import advance_game_status
from helpers.inline_keyboard import send_player_select_keyboard, send_fan_select_keyboard
from schema import EventType, PRICE_LIST
from schema import GameStatus
from strings import String


@MJGCommands.command('2eat')
def eat_2(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    user = update.message.from_user

    session = get_db_session()

    game = DB.get_player_current_game(session, user, status=GameStatus.STARTED)

    if game:
        event = DB.create_event(session,
                                game_id=game.id,
                                message_id=update.message.message_id,
                                type=EventType.EAT_2,
                                created_by=user.username)

        send_player_select_keyboard(bot=bot,
                                    game_id=game.id,
                                    event_id=event.id,
                                    action=String.ACTION_2_EAT_SELECT_WIN_1,
                                    chat_id=game.chat_id,
                                    reply_to_message_id=event.message_id,
                                    text=String.EAT_2_ASK_WINNER_1)


@MJGCommands.callback(String.ACTION_2_EAT_SELECT_WIN_1)
def eat_2_winner_1(bot, update):
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
        target_id = data['t']
        update_dict = json.loads(event.description)
        update_dict['winner_1'] = target_id
        DB.update_event(session, event_id, {'description': json.dumps(update_dict)})

        # Send Price Select Keyboard
        message = update.callback_query.message

        send_fan_select_keyboard(bot=bot,
                                 game_id=event.game_id,
                                 event_id=event_id,
                                 action=String.ACTION_2_EAT_SELECT_FAN_1,
                                 chat_id=message.chat_id,
                                 text=String.EAT_2_ASK_PRICE_1,
                                 message=message)


@MJGCommands.callback(String.ACTION_2_EAT_SELECT_FAN_1)
def eat_2_fan_1(bot, update):
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
        fan = data['f']
        amount = PRICE_LIST.get(event.game.price).get(int(fan))
        update_dict = json.loads(event.description)
        update_dict['fan_1'] = int(fan)
        update_dict['amount_1'] = amount
        DB.update_event(session, event_id, {'description': json.dumps(update_dict)})

        send_player_select_keyboard(bot=bot,
                                    game_id=event.game_id,
                                    event_id=event.id,
                                    action=String.ACTION_2_EAT_SELECT_WIN_2,
                                    chat_id=update.callback_query.message.chat_id,
                                    text=String.EAT_2_ASK_WINNER_2,
                                    exclude_id=update_dict['winner_1'],
                                    message=update.callback_query.message)


@MJGCommands.callback(String.ACTION_2_EAT_SELECT_WIN_2)
def eat_2_win_2(bot, update):
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
        target_id = data['t']
        update_dict = json.loads(event.description)
        update_dict['winner_2'] = target_id
        DB.update_event(session, event_id, {'description': json.dumps(update_dict)})

        # Send Price Select Keyboard
        message = update.callback_query.message

        send_fan_select_keyboard(bot=bot,
                                 game_id=event.game_id,
                                 event_id=event_id,
                                 action=String.ACTION_2_EAT_SELECT_FAN_2,
                                 chat_id=message.chat_id,
                                 text=String.EAT_ASK_PRICE,
                                 message=message)


@MJGCommands.callback(String.ACTION_2_EAT_SELECT_FAN_2)
def eat_2_fan_2(bot, update):
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
        fan = data['f']
        amount = PRICE_LIST.get(event.game.price).get(int(fan))
        update_dict = json.loads(event.description)
        update_dict['fan_2'] = int(fan)
        update_dict['amount_2'] = amount
        DB.update_event(session, event_id, {'description': json.dumps(update_dict)})

        send_player_select_keyboard(bot=bot,
                                    game_id=event.game_id,
                                    event_id=event.id,
                                    action=String.ACTION_2_EAT_SELECT_TARGET,
                                    chat_id=update.callback_query.message.chat_id,
                                    text=String.EAT_2_ASK_TARGET,
                                    exclude_id=[update_dict['winner_1'], update_dict['winner_2']],
                                    message=update.callback_query.message)


@MJGCommands.callback(String.ACTION_2_EAT_SELECT_TARGET)
def eat_2_target(bot, update):
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
        target_id = data['t']
        update_dict = json.loads(event.description)
        update_dict['loser'] = target_id
        DB.update_event(session, event_id, {'description': json.dumps(update_dict), 'completed': 1})

        # Create Transaction
        DB.create_transaction(session, event_id,
                              from_id=update_dict['loser'],
                              to_id=update_dict['winner_1'],
                              fan_no=update_dict['fan_1'],
                              amount=update_dict['amount_1'])
        DB.create_transaction(session, event_id,
                              from_id=update_dict['loser'],
                              to_id=update_dict['winner_2'],
                              fan_no=update_dict['fan_2'],
                              amount=update_dict['amount_2'])

        # Send Message to Group
        win_player_1 = DB.get_player(session, update_dict['winner_1'])
        win_player_2 = DB.get_player(session, update_dict['winner_2'])
        target_player = DB.get_player(session, update_dict['loser'])

        text = random.choice(String.EAT_2_MESSAGES).format(
            loser_first=target_player.first_name,
            loser_last=target_player.last_name,
            winner_1_first=win_player_1.first_name,
            winner_1_last=win_player_1.last_name,
            winner_2_first=win_player_2.first_name,
            winner_2_last=win_player_2.last_name,
            fan_1=update_dict['fan_1'],
            fan_2=update_dict['fan_2']
        )

        message = update.callback_query.message
        bot.editMessageText(text=text,
                            chat_id=message.chat_id,
                            message_id=message.message_id)

        # Advance Game
        advance_game_status(bot, game_id=event.game_id, winner=[update_dict['winner_1'], update_dict['winner_2']])
