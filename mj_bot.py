import ConfigParser
import json
import logging

from telegram.ext import CallbackQueryHandler
from telegram.ext import Updater, CommandHandler

from commands import MJGCommands


# Error Handler
def error_handler(bot, update, error):
    logging.warning('Update "%s" caused error "%s"' % (update, error))


# Callback Query
def callback_handler(bot, update):
    query = update.callback_query
    data = json.loads(query.data)
    action = data['a'] if 'a' in data else data['action']

    if action in MJGCommands.CALLBACK_HANDLERS:
        MJGCommands.CALLBACK_HANDLERS[action](bot, update)
    else:
        logging.info('Unregistered Action: {0}'.format(action))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')

    config = ConfigParser.RawConfigParser()
    config.read("config.conf")

    updater = Updater(config.get('MJG', 'BOT_TOKEN'))

    for command, handler in MJGCommands.COMMANDS.iteritems():
        logging.debug('Registering Command Handler: {0}'.format(command))
        updater.dispatcher.add_handler(CommandHandler(command, handler))

    for action, handler in MJGCommands.CALLBACK_HANDLERS.iteritems():
        logging.debug('Registering Query Callback Handler: {0}'.format(action))

    updater.dispatcher.add_error_handler(error_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_handler))

    updater.start_polling()
    updater.idle()
