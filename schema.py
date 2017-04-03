import time

from sqlalchemy import Column
from sqlalchemy import DECIMAL
from sqlalchemy import ForeignKey
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UnicodeText
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

PRICE_LIST = {
    '8f64': {
        3: 8,
        4: 16,
        5: 24,
        6: 32,
        7: 48,
        8: 64
    },
    '8f128': {
        3: 16,
        4: 32,
        5: 48,
        6: 64,
        7: 96,
        8: 128
    },
    '10f128': {
        3: 8,
        4: 16,
        5: 24,
        6: 32,
        7: 48,
        8: 64,
        9: 96,
        10: 128
    },
    '10f256': {
        3: 16,
        4: 32,
        5: 48,
        6: 64,
        7: 96,
        8: 128,
        9: 192,
        10: 256
    },
}


# Mixin
class Timestamps(object):
    create_date = Column(DECIMAL(precision=14, scale=4, asdecimal=True), index=True, default=time.time)
    update_date = Column(DECIMAL(precision=14, scale=4, asdecimal=True), index=True, default=time.time,
                         onupdate=time.time)


class Player(Base):
    __tablename__ = 'player'

    username = Column(String(64), primary_key=True)
    first_name = Column(UnicodeText)
    last_name = Column(UnicodeText)


class GameStatus(object):
    INIT = 0
    WAITING_FOR_PLAYER = 1
    STARTED = 2
    ENDED = 3


class Season(Timestamps, Base):
    __tablename__ = 'season'

    season_no = Column(Integer, primary_key=True)
    chat_id = Column(Integer, primary_key=True, index=True)
    end_date = Column(DECIMAL(precision=14, scale=4, asdecimal=True), index=True, nullable=True)


class Game(Timestamps, Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True, autoincrement=True)
    season_no = Column(Integer, index=True)
    chat_id = Column(Integer)
    price = Column(String(10), nullable=True)
    player_1_id = Column(String(64), ForeignKey('player.username'), nullable=True, index=True)
    player_2_id = Column(String(64), ForeignKey('player.username'), nullable=True, index=True)
    player_3_id = Column(String(64), ForeignKey('player.username'), nullable=True, index=True)
    player_4_id = Column(String(64), ForeignKey('player.username'), nullable=True, index=True)
    set_no = Column(Integer, default=0)
    round_no = Column(Integer, default=0)
    status = Column(Integer, default=GameStatus.INIT)
    end_date = Column(DECIMAL(precision=14, scale=4, asdecimal=True), index=True, nullable=True)

    # Relationship
    player_1 = relationship('Player', foreign_keys=player_1_id)
    player_2 = relationship('Player', foreign_keys=player_2_id)
    player_3 = relationship('Player', foreign_keys=player_3_id)
    player_4 = relationship('Player', foreign_keys=player_4_id)
    events = relationship('Event')

    __table_args__ = (ForeignKeyConstraint([season_no, chat_id],
                                           [Season.season_no, Season.chat_id]),
                      {})


class EventType(object):
    NEW_GAME = 'new_game'
    EAT = 'eat'
    EAT_2 = 'eat_2'
    EAT_3 = 'eat_3'
    SELF_TOUCH = 'self_touch'
    WRAP_TOUCH = 'wrap_touch'
    DRAW = 'draw'
    ON_9 = 'on9'
    END = 'end'
    DELETE = 'delete'


class Event(Timestamps, Base):
    __tablename__ = 'event'

    game_id = Column(Integer, ForeignKey('game.id'))
    message_id = Column(Integer)
    seq_no = Column(Integer, default=-1)
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50))
    description = Column(UnicodeText, nullable=True)
    created_by = Column(String(64), ForeignKey('player.username'))
    completed = Column(Integer, default=0)

    # Relationship
    game = relationship('Game')
    transactions = relationship('Transaction')


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey('event.id'))
    from_player_id = Column(String(64), ForeignKey('player.username'), index=True)
    to_player_id = Column(String(64), ForeignKey('player.username'), index=True)
    fan_no = Column(Integer)
    amount = Column(Integer)
    self_touch = Column(Integer, default=0)

    # Relationship
    events = relationship('Event')
