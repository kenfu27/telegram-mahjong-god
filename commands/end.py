import json

from telegram import Chat
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from commands import MJGCommands
from db import get_db_session, DB
from helpers.game import end_game, get_player_seat_no
from schema import GameStatus, EventType
from strings import String


@MJGCommands.command('end')
def end(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    user = update.message.from_user
    message = update.message
    chat = message.chat

    if chat.type == Chat.PRIVATE:
        bot.send_message(update.message.chat_id, String.ERROR_PRIVATE_CHAT)
    else:
        session = get_db_session()

        game = DB.get_player_current_game(session, user, status=GameStatus.STARTED)

        if game:
            event = DB.create_event(session,
                                    game_id=game.id,
                                    message_id=update.message.message_id,
                                    type=EventType.END,
                                    created_by=user.username)

            btn_text = String.END_GAME_MESSAGE

            callback_data = json.dumps({'a': String.ACTION_END_GAME_CONFIRM, 'e': event.id})

            inline_keyboard_buttons = [
                [InlineKeyboardButton(text=btn_text, callback_data=callback_data)]
            ]

            bot.send_message(chat_id=game.chat_id,
                             text=String.END_GAME_CONFIRM,
                             reply_to_message_id=message.message_id,
                             reply_markup=InlineKeyboardMarkup(inline_keyboard_buttons))


@MJGCommands.callback(String.ACTION_END_GAME_CONFIRM)
def end_game_confirm(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    current_user = update.callback_query.from_user
    data = json.loads(update.callback_query.data)
    session = get_db_session()
    event_id = data['e']
    event = DB.get_event(session, event_id=event_id)

    if not event.completed and get_player_seat_no(current_user.username,
                                                  event.game) != 0 and current_user.username != event.created_by:
        end_game(bot, event.game_id, message=update.callback_query.message)
