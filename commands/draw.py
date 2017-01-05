import random

from telegram import Chat

from commands import MJGCommands
from db import DB, get_db_session
from helpers.game import advance_game_status
from schema import EventType, GameStatus
from strings import String


@MJGCommands.command('draw')
def draw(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    user = update.message.from_user

    chat = update.message.chat

    if chat.type == Chat.PRIVATE:
        bot.sendMessage(update.message.chat_id, String.ERROR_PRIVATE_CHAT, timeout=5)
    else:
        session = get_db_session()

        game = DB.get_player_current_game(session, user, status=GameStatus.STARTED)

        if game:
            DB.create_event(session,
                            game_id=game.id,
                            message_id=update.message.message_id,
                            type=EventType.DRAW,
                            created_by=user.username,
                            completed=1)

            # Send Message to Chat Room
            bot.sendMessage(chat_id=game.chat_id, text=random.choice(String.DRAW_MESSAGES), timeout=5)

            advance_game_status(bot, game_id=game.id)
        else:
            with open('assets/eatshit.jpg', 'rb') as f:
                update.message.reply_photo(photo=f, caption=String.ERROR_NO_GAME_EAT.encode('utf8'))
