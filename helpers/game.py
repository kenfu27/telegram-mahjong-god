# -*- coding: utf-8 -*-

import codecs
import json
import time

from sqlalchemy.orm import joinedload

from db import DB, get_db_session
from schema import Game, GameStatus, Event, EventType
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


def get_game_status(game_id):
    """
    :type game: int
    :rtype: unicode
    """

    game = DB.get_game(get_db_session(), game_id=game_id,
                       options=[joinedload(Game.player_1),
                                joinedload(Game.player_2),
                                joinedload(Game.player_3),
                                joinedload(Game.player_4),
                                joinedload(Game.events, Event.transactions)])

    event_str = u''

    seat_no_map = {
        game.player_1_id: 0,
        game.player_2_id: 1,
        game.player_3_id: 2,
        game.player_4_id: 3
    }

    totals = [0, 0, 0, 0]
    for index, event in enumerate(sorted(game.events, key=lambda e: e.id)):
        if event.type not in [EventType.END, EventType.DELETE, EventType.NEW_GAME]:
            results = [0, 0, 0, 0]
            for transaction in event.transactions:
                totals[seat_no_map[transaction.from_player_id]] -= int(transaction.amount)
                totals[seat_no_map[transaction.to_player_id]] += int(transaction.amount)
                results[seat_no_map[transaction.from_player_id]] -= int(transaction.amount)
                results[seat_no_map[transaction.to_player_id]] += int(transaction.amount)
            event_str += u'{0}. '.format(index).rjust(4) + u''.join([str(amount).rjust(5) for amount in results]) + \
                         u'   ' + get_event_description(event) + u'\n\r'

    with codecs.open('templates/game_status.html', 'r', 'utf-8') as f:
        html = f.read().format(
            set=String.__dict__.get('SEAT_{0}'.format(game.set_no)),
            round=String.__dict__.get('SEAT_{0}'.format(game.round_no)),
            player_1_first=game.player_1.first_name,
            player_1_last=game.player_1.last_name,
            player_2_first=game.player_2.first_name,
            player_2_last=game.player_2.last_name,
            player_3_first=game.player_3.first_name,
            player_3_last=game.player_3.last_name,
            player_4_first=game.player_4.first_name,
            player_4_last=game.player_4.last_name,
            events=event_str,
            totals=u'   ' + u''.join([str(amount).rjust(5) for amount in totals]) + u'\n\r'
        )

    return html


def get_event_description(event):
    """
    :type event: schema.Event
    :rtype: unicode
    """
    descriptions = json.loads(event.description)
    if event.type == EventType.EAT:
        return u'食{0}番'.format(descriptions['fan'])
    elif event.type == EventType.EAT_2:
        return u'雙響 ({0}番，{1}番)'.format(descriptions['fan_1'], descriptions['fan_2'])
    elif event.type == EventType.EAT_3:
        return u'三響 ({0}番，{1}番，{2}番)'.format(descriptions['fan_1'], descriptions['fan_2'], descriptions['fan_3'])
    elif event.type == EventType.SELF_TOUCH:
        return u'自摸{0}番'.format(descriptions['fan'])
    elif event.type == EventType.WRAP_TOUCH:
        return u'包自摸{0}番'.format(descriptions['fan'])
    elif event.type == EventType.DRAW:
        return u'流局'
    elif event.type == EventType.ON_9:
        return u'詐糊'


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

    def next_jong():
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

        return text

    def same_jong():
        jong = game.__getattribute__('player_{0}'.format(game.round_no))
        text = String.SAME_JONG_MESSAGE.format(
            set=String.__dict__.get('SEAT_{0}'.format(game.set_no)),
            round=String.__dict__.get('SEAT_{0}'.format(game.round_no)),
            jong_first=jong.first_name,
            jong_last=jong.last_name
        )

        return text

    if winner:
        jong_id = game.__getattribute__('player_{0}_id'.format(game.round_no))
        if jong_id in winner:
            # Same Jong
            text = same_jong()

            # Send Message To Chat
            bot.sendMessage(chat_id=game.chat_id, text=text, parse_mode='Markdown', timeout=5)
        elif game.set_no == 4 and game.round_no == 4:
            # End Game
            # end_game(bot, game.id)
            status_text = get_game_status(game.id)

            bot.sendMessage(chat_id=game.chat_id,
                            text=status_text,
                            parse_mode='HTML',
                            timeout=5)
        else:
            # Next Jong
            text = next_jong()

            # Send Message To Chat
            bot.sendMessage(chat_id=game.chat_id, text=text, parse_mode='Markdown', timeout=5)
    else:
        # Next Jong
        text = next_jong()

        # Send Message To Chat
        bot.sendMessage(chat_id=game.chat_id, text=text, parse_mode='Markdown', timeout=5)


def end_game(bot, game_id, message=None):
    """
    :type bot: telegram.bot.Bot
    :type game_id: int
    :type message: telegram.message.Message
    """
    session = get_db_session()

    DB.update_game(session, game_id, {'status': GameStatus.ENDED, 'end_date': time.time()})

    game = DB.get_game(session, game_id=game_id,
                       options=[joinedload(Game.player_1),
                                joinedload(Game.player_2),
                                joinedload(Game.player_3),
                                joinedload(Game.player_4)])

    # TODO: Display Results

    if message:
        bot.editMessageText(text=String.END_GAME_MESSAGE, chat_id=message.chat_id,
                            message_id=message.message_id, timeout=5)
    else:
        bot.sendMessage(chat_id=game.chat_id, text=String.END_GAME_MESSAGE, timeout=5)

    # Send Result
    bot.sendMessage(chat_id=game.chat_id,
                    text=get_game_status(game.id),
                    parse_mode='HTML',
                    timeout=5)
