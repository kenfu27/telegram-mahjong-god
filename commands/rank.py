from commands import MJGCommands
from helpers.season import get_chat_current_season_no
from helpers.stats import get_player_ranks


@MJGCommands.command('rank')
def rank(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    chat = update.message.chat

    current_season_no = get_chat_current_season_no(chat_id=chat.id)

    ranks = get_player_ranks(season_no=current_season_no, chat_id=chat.id)

    text = u''

    for i, record in enumerate(ranks):
        text += u'{0}. '.format(i + 1).rjust(len(ranks) / 10 + 3) + u'{0}: '.format(record['amount']).rjust(8) + record[
            'player'].first_name + u' ' + record['player'].last_name + u'\n\r'

    text = u'<pre>' + (text or u'NO DATA') + u'</pre>'

    bot.sendMessage(chat_id=update.message.chat_id, text=text, parse_mode='HTML', timeout=5,
                    reply_to_message_id=update.message.message_id)
