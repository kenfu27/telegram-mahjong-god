from sqlalchemy.orm import joinedload

from db import DB, get_db_session
from schema import Game, GameStatus
from strings import String


def get_player_seat_no(user, game):
    """
    :type user: telegram.user.User | str | unicode
    :type game: schema.Game
    :rtype: int
    """
    if isinstance(user, (str, unicode)):
        username = user
    else:
        username = user.username

    for i in range(1, 5):
        if game.__getattribute__('player_{0}_id'.format(i)) == username:
            return i
    return 0


def get_game_player_no(game):
    """
    :type game: schema.Game
    :return: int
    """
    player_no = 0

    for i in range(1, 5):
        key = 'player_{0}_id'.format(i)
        if game.__getattribute__(key):
            player_no += 1

    return player_no


def advance_game_status(bot, game_id, winner=None):
    """
    :type bot: telegram.bot.Bot
    :type game_id: int
    :type winner:
    """
    if isinstance(winner, (str, unicode)):
        winner = [winner]

    session = get_db_session()

    game = DB.get_game(session, game_id=game_id,
                       options=[joinedload(Game.player_1),
                                joinedload(Game.player_2),
                                joinedload(Game.player_3),
                                joinedload(Game.player_4)])

    if winner:
        jong_id = game.__getattribute__('player_{0}_id'.format(game.round_no))
        if jong_id in winner:
            # Same Jong
            jong = game.__getattribute__('player_{0}'.format(game.round_no))
            text = String.SAME_JONG_MESSAGE.format(
                set=String.__dict__.get('SEAT_{0}'.format(game.set_no)),
                round=String.__dict__.get('SEAT_{0}'.format(game.round_no)),
                jong_first=jong.first_name,
                jong_last=jong.last_name
            )

            # Send Message To Chat
            bot.sendMessage(chat_id=game.chat_id, text=text, parse_mode='Markdown')
        elif game.set_no == 4 and game.round_no == 4:
            # End Game
            end_game(bot, game.id)
    else:
        # Next Jong
        if game.round_no == 4:
            if game.set_no == 4:
                # Same Jong
                jong = game.__getattribute__('player_{0}'.format(game.round_no))
                text = String.SAME_JONG_MESSAGE.format(
                    set=String.__dict__.get('SEAT_{0}'.format(game.set_no)),
                    round=String.__dict__.get('SEAT_{0}'.format(game.round_no)),
                    jong_first=jong.first_name,
                    jong_last=jong.last_name
                )
            else:
                # Next Set
                DB.update_game(session, game.id, update_dict={'set_no': game.set_no + 1, 'round_no': 1})
                jong = game.player_1
                text = String.NEXT_JONG_MESSAGE.format(
                    set=String.__dict__.get('SEAT_{0}'.format(game.set_no)),
                    round=String.__dict__.get('SEAT_{0}'.format(game.round_no)),
                    jong_first=jong.first_name,
                    jong_last=jong.last_name
                )
        else:
            DB.update_game(session, game.id, update_dict={'round_no': game.round_no + 1})
            jong = game.__getattribute__('player_{0}'.format(game.round_no))
            text = String.NEXT_JONG_MESSAGE.format(
                set=String.__dict__.get('SEAT_{0}'.format(game.set_no)),
                round=String.__dict__.get('SEAT_{0}'.format(game.round_no)),
                jong_first=jong.first_name,
                jong_last=jong.last_name
            )

        # Send Message To Chat
        bot.sendMessage(chat_id=game.chat_id, text=text, parse_mode='Markdown')


def end_game(bot, game_id):
    """
    :type bot: telegram.bot.Bot
    :type game_id: int
    """
    session = get_db_session()

    DB.update_game(session, game_id, {'status': GameStatus.ENDED})

    game = DB.get_game(session, game_id=game_id,
                       options=[joinedload(Game.player_1),
                                joinedload(Game.player_2),
                                joinedload(Game.player_3),
                                joinedload(Game.player_4)])

    # TODO: Display Results
    bot.sendMessage(chat_id=game.chat_id, text=String.END_GAME_MESSAGE)
