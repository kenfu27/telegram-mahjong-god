import json

from sqlalchemy.orm import joinedload

from commands import MJGCommands
from db import DB, get_db_session
from helpers.game import get_game_status
from helpers.inline_keyboard import send_game_select_keyboard
from schema import Game
from strings import String


@MJGCommands.command('history')
def history(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    message = update.message

    games = DB.get_games(get_db_session(), chat_id=message.chat_id, options=[
        joinedload(Game.player_1),
        joinedload(Game.player_2),
        joinedload(Game.player_3),
        joinedload(Game.player_4)
    ])

    send_game_select_keyboard(bot,
                              chat_id=message.chat_id,
                              text=String.HISTORY_ASK_GAME,
                              action=String.ACTION_HISTORY_SELECT_GAME,
                              games=games)


@MJGCommands.callback(String.ACTION_HISTORY_LIST)
def history_list(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    data = json.loads(update.callback_query.data)
    game_before_id = data.get('before', None)
    game_after_id = data.get('after', None)

    message = update.callback_query.message

    games = DB.get_games(get_db_session(),
                         chat_id=message.chat_id,
                         size=10,
                         game_before_id=game_before_id,
                         game_after_id=game_after_id,
                         options=[
                             joinedload(Game.player_1),
                             joinedload(Game.player_2),
                             joinedload(Game.player_3),
                             joinedload(Game.player_4)
                         ])

    send_game_select_keyboard(bot,
                              chat_id=message.chat_id,
                              text=String.HISTORY_ASK_GAME,
                              action=String.ACTION_HISTORY_SELECT_GAME,
                              games=games)


@MJGCommands.callback(String.ACTION_HISTORY_SELECT_GAME)
def history_select_game(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    data = json.loads(update.callback_query.data)
    game_id = data['g']
    game_status_str = get_game_status(game_id)
    message = update.callback_query.message

    bot.editMessageText(text=game_status_str,
                        chat_id=message.chat_id,
                        message_id=message.message_id,
                        parse_mode='HTML')
