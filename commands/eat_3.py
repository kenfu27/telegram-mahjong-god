import json
import random

from sqlalchemy.orm import joinedload

from commands import MJGCommands
from db import DB
from db import get_db_session
from helpers.game import get_player_seat_no, advance_game_status
from helpers.inline_keyboard import send_player_select_keyboard, send_fan_select_keyboard
from schema import EventType, PRICE_LIST, Game
from schema import GameStatus
from strings import String


@MJGCommands.command('3eat')
def _3eat(bot, update):
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
                                type=EventType.EAT_3,
                                created_by=user.username)

        send_player_select_keyboard(bot=bot,
                                    game_id=game.id,
                                    event_id=event.id,
                                    action=String.ACTION_3_SELECT_TARGET,
                                    chat_id=game.chat_id,
                                    reply_to_message_id=event.message_id,
                                    text=String.EAT_3_ASK_TARGET)


@MJGCommands.callback(String.ACTION_3_SELECT_TARGET)
def eat_3_target(bot, update):
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

        game = DB.get_game(session, event.game_id, options=[joinedload(Game.player_1),
                                                            joinedload(Game.player_2),
                                                            joinedload(Game.player_3),
                                                            joinedload(Game.player_4)])

        target_seat_no = get_player_seat_no(user=target_id, game=game)
        winner_ids = []
        for i in range(1, 5):
            if i != target_seat_no:
                winner_ids.append(game.__getattribute__('player_{0}'.format(i)).username)
        for i in range(0, len(winner_ids)):
            update_dict['winner_{0}'.format(i + 1)] = winner_ids[i]

        DB.update_event(session, event_id, {'description': json.dumps(update_dict)})

        # Send Price Select Keyboard
        send_3eat_fan_select_keyboard(bot=bot,
                                      session=session,
                                      winner_id=update_dict['winner_{0}'.format(1)],
                                      event=event,
                                      message=update.callback_query.message,
                                      index=1)


def send_3eat_fan_select_keyboard(bot, session, winner_id, event, message, index):
    winner = DB.get_player(session, winner_id)

    text = String.EAT_3_ASK_PRICE.format(winner_first=winner.first_name, winner_last=winner.last_name)

    send_fan_select_keyboard(bot=bot,
                             game_id=event.game_id,
                             event_id=event.id,
                             action=String.__dict__.get('ACTION_3_EAT_SELECT_FAN_{0}'.format(index)),
                             chat_id=message.chat_id,
                             text=text,
                             message=message)


@MJGCommands.callback(String.ACTION_3_EAT_SELECT_FAN_1)
def eat_3_fan_1(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    handle_eat_3_select_fan_callback(bot, update, 1)


@MJGCommands.callback(String.ACTION_3_EAT_SELECT_FAN_2)
def eat_3_fan_2(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    handle_eat_3_select_fan_callback(bot, update, 2)


@MJGCommands.callback(String.ACTION_3_EAT_SELECT_FAN_3)
def eat_3_fan_3(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    handle_eat_3_select_fan_callback(bot, update, 3)


def handle_eat_3_select_fan_callback(bot, update, index):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    :type index: int
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
        update_dict['fan_{0}'.format(index)] = int(fan)
        update_dict['amount_{0}'.format(index)] = amount
        DB.update_event(session, event_id, {'description': json.dumps(update_dict)})

        if index != 3:
            # Ask Next Winner
            send_3eat_fan_select_keyboard(bot=bot,
                                          session=session,
                                          winner_id=update_dict['winner_{0}'.format(index + 1)],
                                          event=event,
                                          message=update.callback_query.message,
                                          index=index + 1)
        else:
            DB.update_event(session, event_id, {'completed': 1})

            # Create Transactions
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
            DB.create_transaction(session, event_id,
                                  from_id=update_dict['loser'],
                                  to_id=update_dict['winner_3'],
                                  fan_no=update_dict['fan_3'],
                                  amount=update_dict['amount_3'])

            # Send Message to Group
            game = DB.get_game(session, event.game_id)
            loser = DB.get_player(session, update_dict['loser'])
            winner_1 = DB.get_player(session, update_dict['winner_1'])
            winner_2 = DB.get_player(session, update_dict['winner_2'])
            winner_3 = DB.get_player(session, update_dict['winner_3'])

            text = random.choice(String.EAT_3_MESSAGES).format(
                loser_first=loser.first_name,
                loser_last=loser.last_name,
                winner_1_first=winner_1.first_name,
                winner_1_last=winner_1.last_name,
                winner_2_first=winner_2.first_name,
                winner_2_last=winner_2.last_name,
                winner_3_first=winner_3.first_name,
                winner_3_last=winner_3.last_name,
                fan_1=update_dict['fan_1'],
                fan_2=update_dict['fan_2'],
                fan_3=update_dict['fan_3']
            )

            message = update.callback_query.message
            bot.editMessageText(timeout=5, text=text,
                                chat_id=message.chat_id,
                                message_id=message.message_id)

            # Advance Game
            advance_game_status(bot, game_id=game.id,
                                winner=[update_dict['winner_1'], update_dict['winner_2'], update_dict['winner_3']])
