# coding=utf-8
from commands import MJGCommands
from helpers.season import get_chat_current_season
from helpers.stats import get_player_vs


@MJGCommands.command('vs')
def vs(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    user = update.message.from_user
    chat = update.message.chat

    current_season = get_chat_current_season(chat_id=chat.id)

    winnings, losings, totals, players = get_player_vs(user.username, season_no=current_season.season_no,
                                                       chat_id=current_season.chat_id)

    html = u'<pre>'

    html += u'贏:\n\r'
    for t in winnings:
        html += u'{first_name} {last_name}: {amount}\n\r'.format(first_name=players[t['username']].first_name,
                                                                 last_name=players[t['username']].last_name,
                                                                 amount=t['amount'])

    html += u'\n\r輸:\n\r'
    for t in losings:
        html += u'{first_name} {last_name}: {amount}\n\r'.format(first_name=players[t['username']].first_name,
                                                                 last_name=players[t['username']].last_name,
                                                                 amount=t['amount'])

    html += u'\n\r總共:\n\r'
    for t in totals:
        html += u'{first_name} {last_name}: {amount}\n\r'.format(first_name=players[t['username']].first_name,
                                                                 last_name=players[t['username']].last_name,
                                                                 amount=t['amount'])

    html += u'</pre>'

    bot.sendMessage(chat_id=update.message.chat_id,
                    text=html,
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id,
                    timeout=5)
