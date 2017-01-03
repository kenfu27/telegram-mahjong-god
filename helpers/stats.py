import json

from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from db import get_db_session
from schema import Game, GameStatus, Event, EventType


class MJGStats(object):
    def __init__(self, total_rounds, eat, eat_amount, draw, lose, lose_amount, touch_win, touch_win_amount, touch_lose,
                 touch_lose_amount, wrap_touch, eat_2, eat_3, win_map, win_fan_map, lose_map, lose_fan_map,
                 touch_win_map, touch_win_fan_map, touch_lose_map, touch_lose_fan_map):
        self.total_games = total_rounds
        self.eat = eat
        self.eat_amount = eat_amount
        self.draw = draw
        self.lose = lose
        self.lose_amount = lose_amount
        self.touch_win = touch_win
        self.touch_win_amount = touch_win_amount
        self.touch_lose = touch_lose
        self.touch_lose_amount = touch_lose_amount
        self.wrap_touch = wrap_touch
        self.eat_2 = eat_2
        self.eat_3 = eat_3
        self.win_map = win_map
        self.win_fan_map = win_fan_map
        self.lose_map = lose_map
        self.lose_fan_map = lose_fan_map
        self.touch_win_map = touch_win_map
        self.touch_win_fan_map = touch_win_fan_map
        self.touch_lose_map = touch_lose_map
        self.touch_lose_fan_map = touch_lose_fan_map


def get_player_stats(username):
    """
    :type username: str | unicode
    :rtype: MJGStats
    """
    session = get_db_session()

    games = session.query(Game).filter(
        or_(Game.player_1_id == username,
            Game.player_2_id == username,
            Game.player_3_id == username,
            Game.player_4_id == username),
        Game.status == GameStatus.ENDED).options([joinedload(Game.events, Event.transactions)]).all()

    total_rounds = 0
    eat = 0
    eat_amount = 0
    draw = 0
    lose = 0
    lose_amount = 0
    touch_win = 0
    touch_win_amount = 0
    touch_lose = 0
    touch_lose_amount = 0
    wrap_touch = 0
    eat_2 = 0
    eat_3 = 0

    win_map = {}
    win_fan_map = {}
    lose_map = {}
    lose_fan_map = {}
    touch_win_map = {}
    touch_win_fan_map = {}
    touch_lose_map = {}
    touch_lose_fan_map = {}

    def update_map(map, username, amount):
        if username not in map:
            map[username] = 0
        map[username] += amount

    for game in games:
        for event in game.events:
            description = json.loads(event.description)
            if event.type not in [EventType.END, EventType.DELETE]:
                total_rounds += 1
                if event.type == EventType.DRAW:
                    draw += 1
                elif event.type in [EventType.EAT, EventType.EAT_2, EventType.EAT_3]:
                    for transaction in event.transactions:
                        if transaction.from_player_id == username:
                            # LOSE
                            lose += 1
                            lose_amount += transaction.amount
                            update_map(lose_map, transaction.to_player_id, transaction.amount)
                            update_map(lose_fan_map, description['fan'], 1)

                            if event.type == EventType.EAT_2:
                                eat_2 += 1
                            if event.type == EventType.EAT_3:
                                eat_3 += 1

                        elif transaction.to_player_id == username:
                            # WIN
                            eat += 1
                            eat_amount += transaction.amount
                            update_map(win_map, transaction.from_player_id, transaction.amount)
                            update_map(win_fan_map, description['fan'], 1)
                elif event.type in [EventType.SELF_TOUCH, EventType.WRAP_TOUCH]:
                    for transaction in event.transactions:
                        if transaction.from_player_id == username:
                            # LOSE
                            touch_lose += 1
                            touch_lose_amount += transaction.amount
                            update_map(touch_lose_map, transaction.to_player_id, transaction.amount)
                            update_map(touch_lose_fan_map, description['fan'], 1)

                            if event.type == EventType.WRAP_TOUCH:
                                wrap_touch += 1
                        elif transaction.to_player_id == username:
                            # WIN
                            touch_win += 1
                            touch_win_amount += transaction.amount
                            update_map(touch_win_map, transaction.to_player_id, transaction.amount)
                            update_map(touch_win_fan_map, description['fan'], 1)

    touch_win /= 3
    for fan, value in touch_win_fan_map.iteritems():
        touch_win_fan_map[fan] /= 3

    return MJGStats(
        total_rounds, eat, eat_amount, draw, lose, lose_amount, touch_win, touch_win_amount, touch_lose,
        touch_lose_amount, wrap_touch, eat_2, eat_3, win_map, win_fan_map, lose_map, lose_fan_map, touch_win_map,
        touch_win_fan_map, touch_lose_map, touch_lose_fan_map
    )
