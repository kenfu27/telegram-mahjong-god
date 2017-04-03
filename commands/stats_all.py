import codecs

from telegram.ext.dispatcher import run_async

from commands import MJGCommands
from helpers.stats import get_player_stats


@MJGCommands.command('stats_all')
@run_async
def stats(bot, update):
    """
    :type bot: telegram.bot.Bot
    :type update: telegram.update.Update
    """
    user = update.message.from_user
    chat = update.message.chat

    stats = get_player_stats(user.username, chat_id=chat.id)

    fans = ''

    for i in range(3, 11):
        numbers = [
            stats.win_fan_map.get(i, 0),
            stats.lose_fan_map.get(i, 0),
            stats.touch_win_fan_map.get(i, 0),
            stats.touch_lose_fan_map.get(i, 0)
        ]
        fans += '{0}'.format(i).rjust(4) + '/' + '/'.join(['{0}'.format(n).rjust(4) for n in numbers]) + '\n\r'

    with codecs.open('templates/stats', 'r', 'utf-8') as f:
        html = f.read().format(
            total_game=str(stats.total_games).rjust(5),
            total_balance=str(stats.total_balance).rjust(5),
            eat=str(stats.eat).rjust(5),
            eat_amount=str(stats.eat_amount).rjust(5),
            eat_rate="{0:.4f}".format(float(stats.eat) / float(stats.total_games)),
            average_eat_amount="{0:.1f}".format(float(stats.eat_amount) / float(stats.eat)).rjust(
                6) if stats.eat else '0',
            lose=str(stats.lose).rjust(5),
            lose_amount=str(stats.lose_amount).rjust(5),
            lose_rate="{0:.4f}".format(float(stats.lose) / float(stats.total_games)),
            average_lose_amount="{0:.1f}".format(float(stats.lose_amount) / float(stats.lose)).rjust(
                6) if stats.lose else '0',
            touch_win=str(stats.touch_win).rjust(5),
            touch_win_amount=str(stats.touch_win_amount).rjust(5),
            touch_win_rate="{0:.4f}".format(float(stats.touch_win) / float(stats.total_games)),
            average_touch_win_amount="{0:.1f}".format(
                float(stats.touch_win_amount) / float(stats.touch_win)).rjust(6) if stats.touch_win else '0',
            touch_lose=str(stats.touch_lose).rjust(5),
            touch_lose_amount=str(stats.touch_lose_amount).rjust(5),
            touch_lose_rate="{0:.4f}".format(float(stats.touch_lose) / float(stats.total_games)),
            average_touch_lose_amount="{0:.1f}".format(
                float(stats.touch_lose_amount) / float(stats.touch_lose)).rjust(6) if stats.touch_lose else '0',
            wrap_touch=str(stats.wrap_touch).rjust(5),
            draw=str(stats.draw).rjust(5),
            draw_rate="{0:.4f}".format(float(stats.draw) / float(stats.total_games)).rjust(5),
            fans=fans
        )

    bot.sendMessage(chat_id=update.message.chat_id,
                    text=html,
                    parse_mode='HTML',
                    reply_to_message_id=update.message.message_id,
                    timeout=5)
