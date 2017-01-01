import codecs

from telegram import Chat

from commands import MJGCommands
from db import get_db_session, DB


@MJGCommands.command('start')
def start(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    chat = update.message.chat

    if chat.type == Chat.PRIVATE:
        # Register User
        user = update.message.from_user
        DB.try_register_player(get_db_session(), user, chat)

    # Display Help Message
    with codecs.open('templates/help.html', 'r', 'utf-8') as f:
        html = f.read()

    bot.send_message(update.message.chat_id, html, parse_mode='HTML')
