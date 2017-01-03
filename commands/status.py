from commands import MJGCommands
from db import get_db_session, DB
from helpers.game import get_game_status
from schema import GameStatus


@MJGCommands.command('status')
def status(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    user = update.message.from_user
    message = update.message

    session = get_db_session()

    game = DB.get_player_current_game(session, user, status=GameStatus.STARTED)

    if game:
        status_text = get_game_status(game.id)

        bot.send_message(chat_id=message.chat_id,
                         text=status_text,
                         parse_mode='HTML',
                         reply_to_message_id=message.message_id)
    else:
        with open('assets/eatshit.jpg', 'rb') as f:
            update.message.reply_photo(photo=f, caption=String.ERROR_NO_GAME_EAT.encode('utf8'))