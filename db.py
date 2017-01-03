from sqlalchemy import create_engine
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker

from schema import Player, Game, Base, GameStatus, Event, Transaction

# Prepare Schema
engine = create_engine('mysql+mysqldb://root:root@localhost/mahjong', pool_recycle=3600, convert_unicode=True,
                       pool_size=40, echo=False)

Base.metadata.create_all(engine)


def get_db_session():
    session_class = sessionmaker(bind=engine)
    session = session_class()

    return session


class DB(object):
    # Players
    @staticmethod
    def try_register_player(session, user, chat):
        """
        :type session:
        :type user: telegram.user.User
        :type chat: telegram.chat.Chat
        :rtype: bool
        """
        player = Player(username=user.username, first_name=user.first_name, last_name=user.last_name, chat_id=chat.id)

        session.merge(player)

        session.commit()

    @staticmethod
    def get_player(session, username):
        """
        :type session:
        :type username: str
        :rtype: schema.Player
        """
        return session.query(Player).get(username)

    @staticmethod
    def is_user_registered(session, user):
        """
        :type session:
        :type user: telegram.user.User
        :rtype: bool
        """
        return bool(DB.get_player(session, user.username))

    # Game
    @staticmethod
    def get_open_game(session, chat_id):
        """
        :rtype: schema.Game
        """
        return session.query(Game).filter(Game.chat_id == chat_id, Game.end_date != None).first()

    @staticmethod
    def get_player_current_game(session, user, status=None, options=None):
        """
        :type session:
        :type user: telegram.user.User
        :rtype: schema.Game
        """
        query = session.query(Game).filter(
            or_(Game.player_1_id == user.username,
                Game.player_2_id == user.username,
                Game.player_3_id == user.username,
                Game.player_4_id == user.username))

        if status:
            query = query.filter(Game.status == status)
        else:
            query = query.filter(Game.status != GameStatus.ENDED)

        if options:
            query = query.options(options)

        return query.first()

    @staticmethod
    def create_game(session, chat_id, player_1_id=None, player_2_id=None, player_3_id=None, player_4_id=None):
        """
        :rtype: schema.Game
        """
        game = Game(chat_id=chat_id, player_1_id=player_1_id, player_2_id=player_2_id, player_3_id=player_3_id,
                    player_4_id=player_4_id)
        session.add(game)
        session.commit()
        return game

    @staticmethod
    def get_game(session, game_id, options=None):
        """
        :type session:
        :type game_id:
        :type options:
        :rtype: schema.Game
        """
        query = session.query(Game)

        if options:
            query = query.options(options)

        return query.get(game_id)

    @staticmethod
    def get_games(session, chat_id, size=10, game_before_id=None, game_after_id=None, options=None):
        """
        :type session:
        :type chat_id: int
        :type size: int
        :type game_before_id: int
        :type game_after_id: int
        :type options:
        :rtype: list[schema.Game]
        """
        query = session.query(Game).filter(Game.chat_id == chat_id)

        if options:
            query = query.options(options)

        if game_before_id:
            return query.filter(Game.id < game_before_id).order_by(Game.id.desc()).limit(size).all()
        elif game_after_id:
            return list(reversed(query.filter(Game.id > game_before_id).order_by(Game.id.asc()).limit(size).all()))
        else:
            return query.order_by(Game.id.desc()).limit(size).all()

    @staticmethod
    def update_game(session, game_id, update_dict):
        session.query(Game).filter(Game.id == game_id).update(update_dict)
        session.commit()

    # Event
    @staticmethod
    def create_event(session, game_id, message_id, type, created_by, description='{}', completed=0):
        event = Event(game_id=game_id,
                      message_id=message_id,
                      type=type,
                      description=description,
                      created_by=created_by,
                      completed=completed)

        session.add(event)
        session.commit()
        return event

    @staticmethod
    def get_event(session, event_id=None):
        return session.query(Event).get(event_id)

    @staticmethod
    def get_events(session, game_id=None, event_id=None):
        query = session.query(Event)

        if game_id:
            query = query.filter(Event.game_id == game_id)

        if event_id:
            if isinstance(event_id, (int, str, unicode)):
                query = query.filter(Event.id == event_id)
            elif isinstance(event_id, (set, list)):
                query = query.filter(Event.id.in_(event_id))

        return query.all()

    @staticmethod
    def update_event(session, event_id, update_dict):
        session.query(Event).filter(Event.id == event_id).update(update_dict)
        session.commit()

    @staticmethod
    def delete_event(session, event_id):
        event = session.query(Event).get(event_id)

        if event:
            for transaction in event.transactions:
                session.delete(transaction)

        session.delete(event)
        session.commit()

    # Transaction
    @staticmethod
    def create_transaction(session, event_id, from_id, to_id, fan_no, amount, self_touch=0):
        transaction = Transaction(event_id=event_id, from_player_id=from_id, to_player_id=to_id, fan_no=fan_no,
                                  amount=amount, self_touch=self_touch)
        session.add(transaction)
        session.commit()

    @staticmethod
    def get_transaction(session, transaction_id=None, event_id=None, from_player_id=None, to_player_id=None):
        query = session.query(Transaction)

        if transaction_id:
            if isinstance(transaction_id, (int, str, unicode)):
                query = query.filter(Transaction.id == transaction_id)
            elif isinstance(transaction_id, (list, set)):
                query = query.filter(Transaction.id.in_(transaction_id))

        if event_id:
            if isinstance(event_id, (int, str, unicode)):
                query = query.filter(Transaction.event_id == event_id)
            elif isinstance(event_id, (list, set)):
                query = query.filter(Transaction.event_id.in_(event_id))

        if from_player_id:
            if isinstance(from_player_id, (str, unicode)):
                query = query.filter(Transaction.from_player_id == from_player_id)
            elif isinstance(from_player_id, (list, set)):
                query = query.filter(Transaction.from_player_id.in_(from_player_id))

        if to_player_id:
            if isinstance(to_player_id, (str, unicode)):
                query = query.filter(Transaction.to_player_id == to_player_id)
            elif isinstance(to_player_id, (list, set)):
                query = query.filter(Transaction.to_player_id.in_(to_player_id))

        if transaction_id or event_id or from_player_id or to_player_id:
            return query.order_by(Transaction.event_id.asc()).all()
        else:
            return []
