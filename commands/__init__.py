import json
import logging
import pkgutil

from db import get_db_session, DB
from strings import String

logger = logging.getLogger('MJG')


class MJGCommands(object):
    COMMANDS = {}
    CALLBACK_HANDLERS = {}

    def __init__(self):
        super(MJGCommands, self).__init__()

    @classmethod
    def callback(cls, action):
        def func_wrapper(func):
            def inner_wrapper(bot, update):
                logger.debug('Start Processing Update for Callback Query Action "{0}"'.format(action))
                func(bot, update)
                logger.debug('Finish Processing Update for Callback Query Action "{0}"'.format(action))

            cls.CALLBACK_HANDLERS[action] = inner_wrapper

        return func_wrapper

    @classmethod
    def command(cls, cmd):
        def func_wrapper(func):
            def inner_wrapper(bot, update):
                logger.debug('Start Processing Update for Command "{0}"'.format(cmd))
                func(bot, update)
                logger.debug('Finish Processing Update for Command "{0}"'.format(cmd))

            cls.COMMANDS[cmd] = inner_wrapper

        return func_wrapper


@MJGCommands.callback(String.ACTION_CANCEL)
def cancel(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    data = json.loads(update.callback_query.data)
    event_id = data.get('event_id', None)

    if event_id:
        DB.delete_event(get_db_session(), event_id)

    message = update.callback_query.message
    bot.editMessageText(timeout=5, text=String.CANCEL_CONFIRM, chat_id=message.chat_id, message_id=message.message_id)


@MJGCommands.callback(String.ACTION_EVENT_CANCEL)
def event_cancel(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    data = json.loads(update.callback_query.data)
    user = update.callback_query.from_user

    session = get_db_session()
    event_id = data['e']

    event = DB.get_event(session, event_id=event_id)

    if event:
        DB.delete_event(session, event_id)
        text = u'{0} {1}: {2}'.format(user.first_name, user.last_name, String.CANCEL)
        message = update.callback_query.message
        bot.editMessageText(timeout=5, text=text, chat_id=message.chat_id, message_id=message.message_id)


__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    module = loader.find_module(module_name).load_module(module_name)
    exec ('%s = module' % module_name)
