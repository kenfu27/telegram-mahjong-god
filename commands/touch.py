import json
import random

from sqlalchemy.orm import joinedload
from telegram import Chat

from commands import MJGCommands
from db import get_db_session, DB
from helpers.game import advance_game_status
from helpers.inline_keyboard import send_fan_select_keyboard
from schema import EventType, GameStatus, Game, PRICE_LIST
from strings import String


@MJGCommands.command('touch')
def self_touch(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    user = update.message.from_user

    chat = update.message.chat

    if chat.type == Chat.PRIVATE:
        bot.send_message(update.message.chat_id, String.ERROR_PRIVATE_CHAT)
    else:
        session = get_db_session()

        game = DB.get_player_current_game(session, user, status=GameStatus.STARTED,
                                          options=[joinedload(Game.player_1),
                                                   joinedload(Game.player_2),
                                                   joinedload(Game.player_3),
                                                   joinedload(Game.player_4)])

        if game:
            player = DB.get_player(session, user.username)
            description = json.dumps({'winner': user.username})
            event = DB.create_event(session,
                                    game_id=game.id,
                                    message_id=update.message.message_id,
                                    type=EventType.SELF_TOUCH,
                                    description=description)

            send_fan_select_keyboard(bot=bot,
                                     game_id=event.game_id,
                                     event_id=event.id,
                                     action=String.ACTION_SELF_TOUCH_SELECT_FAN,
                                     chat_id=player.chat_id,
                                     text=String.EAT_ASK_PRICE)


@MJGCommands.callback(String.ACTION_SELF_TOUCH_SELECT_FAN)
def self_touch_fan(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    data = json.loads(update.callback_query.data)
    event_id = data['e']
    session = get_db_session()

    event = DB.get_event(session, event_id=event_id)
    game = DB.get_game(session, event.game_id)

    if event and not event.completed:
        fan = data['f']
        amount = int(PRICE_LIST.get(game.price).get(int(fan)) * 0.5)
        update_dict = json.loads(event.description)
        update_dict['fan'] = int(fan)
        update_dict['amount'] = amount

        DB.update_event(session, event_id, {'description': json.dumps(update_dict), 'completed': 1})

        # Create Transaction
        for i in range(1, 5):
            player_id = game.__getattribute__('player_{0}_id'.format(i))
            if player_id != update_dict['winner']:
                DB.create_transaction(session, event_id=event_id, from_id=player_id, to_id=update_dict['winner'],
                                      fan_no=fan, amount=amount, self_touch=1)

        # Update Message in Individual Chat
        message = update.callback_query.message
        bot.editMessageText(text=String.EAT_CONFIRM,
                            chat_id=message.chat_id,
                            message_id=message.message_id)

        # Send Message to Group
        to_player = DB.get_player(session, update_dict['winner'])

        text = random.choice(String.SELF_TOUCH_MESSAGES).format(winner_first=to_player.first_name,
                                                                winner_last=to_player.last_name,
                                                                fan=fan, amount=amount)

        bot.send_message(chat_id=game.chat_id, text=text)

        # Advance Game
        advance_game_status(bot, game_id=game.id, winner=update_dict['winner'])
