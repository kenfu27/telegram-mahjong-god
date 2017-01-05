import json

from telegram import Chat

from commands import MJGCommands
from db import get_db_session, DB
from helpers.inline_keyboard import send_event_select_keyboard, send_wind_select_keyboard
from schema import GameStatus, EventType
from strings import String


@MJGCommands.command('delete')
def delete(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    user = update.message.from_user
    message = update.message
    chat = message.chat

    if chat.type == Chat.PRIVATE:
        bot.sendMessage(update.message.chat_id, String.ERROR_PRIVATE_CHAT, timeout=5)
    else:
        session = get_db_session()

        game = DB.get_player_current_game(session, user, status=GameStatus.STARTED)

        if game:
            event = DB.create_event(session,
                                    game_id=game.id,
                                    message_id=update.message.message_id,
                                    type=EventType.DELETE,
                                    created_by=user.username)

            target_events = DB.get_events(session, game_id=game.id)

            send_event_select_keyboard(bot,
                                       chat_id=message.chat_id,
                                       text=String.DELETE_ASK_EVENT,
                                       event_id=event.id,
                                       action=String.ACTION_DELETE_SELECT_EVENT,
                                       events=target_events)
        else:
            with open('assets/eatshit.jpg', 'rb') as f:
                update.message.reply_photo(photo=f, caption=String.ERROR_NO_GAME_EAT.encode('utf8'))


@MJGCommands.callback(String.ACTION_DELETE_SELECT_EVENT)
def delete_event(bot, update):
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
        target_event_id = data['t']

        update_dict = json.loads(event.description)
        update_dict['event_id'] = target_event_id

        DB.update_event(session, event_id, {'description': json.dumps(update_dict)})

        # Send Set Select Keyboard
        message = update.callback_query.message
        send_wind_select_keyboard(bot,
                                  chat_id=message.chat_id,
                                  text=String.DELETE_ASK_SET,
                                  event_id=event_id,
                                  action=String.ACTION_DELETE_ASK_SET,
                                  message=message)


@MJGCommands.callback(String.ACTION_DELETE_ASK_SET)
def delete_set(bot, update):
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
        set_no = data['t']

        update_dict = json.loads(event.description)
        update_dict['set_no'] = int(set_no)

        DB.update_event(session, event_id, {'description': json.dumps(update_dict)})

        # Send Set Select Keyboard
        message = update.callback_query.message
        send_wind_select_keyboard(bot,
                                  chat_id=message.chat_id,
                                  text=String.DELETE_ASK_ROUND,
                                  event_id=event_id,
                                  action=String.ACTION_DELETE_ASK_ROUND,
                                  message=message)


@MJGCommands.callback(String.ACTION_DELETE_ASK_ROUND)
def delete_round(bot, update):
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
        round_no = data['t']

        update_dict = json.loads(event.description)

        # Update Game Status
        DB.update_game(session,
                       game_id=event.game_id,
                       update_dict={'set_no': update_dict['set_no'], 'round_no': round_no})

        # Delete Events
        DB.delete_event(session, event_id=update_dict['event_id'])
        DB.delete_event(session, event_id=event_id)

        # Update Message
        message = update.callback_query.message
        bot.editMessageText(timeout=5, text=String.DELETE_CONFIRM,
                            chat_id=message.chat_id,
                            message_id=message.message_id
                            )
