import codecs

from telegram.ext.dispatcher import run_async

from commands import MJGCommands


@MJGCommands.command('help')
@run_async
def help(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    with codecs.open('templates/help.html', 'r', 'utf-8') as f:
        html = f.read()

    bot.send_message(update.message.chat_id, html, parse_mode='HTML')
