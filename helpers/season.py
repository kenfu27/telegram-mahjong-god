from db import get_db_session, DB


def get_chat_current_season_no(chat_id):
    """
    :type chat_id: int
    :rtype: int
    """

    return DB.get_chat_current_season_no(get_db_session(), chat_id=chat_id)


def get_chat_current_season(chat_id):
    """
    :type chat_id:
    :rtype: schema.Season
    """
    return DB.get_chat_current_season(get_db_session(), chat_id=chat_id)
