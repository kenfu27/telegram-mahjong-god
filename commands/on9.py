# import json
#
# from sqlalchemy.orm import joinedload
# from telegram import Chat
#
# from commands import MJGCommands
# from db import get_db_session, DB
# from helpers import get_player_seat_no
# from helpers.inline_keyboard import send_player_select_keyboard
# from schema import GameStatus, EventType, Game
# from strings import String
#
#
# @MJGCommands.command('on9')
# def on9jai(bot, update):
#     """
#     :type bot: telegram.bot.Bot
#     :type update: telegram.update.Update
#     """
#     user = update.message.from_user
#
#     chat = update.message.chat
#
#     if chat.type == Chat.PRIVATE:
#         bot.sendMessage(update.message.chat_id, String.ERROR_PRIVATE_CHAT, timeout=5)
#     else:
#         session = get_db_session()
#
#         game = DB.get_player_current_game(session, user, status=GameStatus.STARTED)
#
#         if game:
#             description = json.dumps({'winner': user.username})
#             event = DB.create_event(session,
#                                     game_id=game.id,
#                                     message_id=update.message.message_id,
#                                     type=EventType.ON_9,
#                                     description=description)
#
#             current_player = DB.get_player(session, user.username)
#
#             send_player_select_keyboard(bot=bot,
#                                         game_id=game.id,
#                                         event_id=event.id,
#                                         action=String.ACTION_ON_9_SELECT_TARGET,
#                                         chat_id=current_player.chat_id,
#                                         text=String.ON_9_ASK_TARGET)
#         else:
#             with open('assets/eatshit.jpg', 'rb') as f:
#                 update.message.reply_photo(photo=f, caption=String.ERROR_NO_GAME_EAT.encode('utf8'))
#
#
# @MJGCommands.callback(String.ACTION_ON_9_SELECT_TARGET)
# def on9_target(bot, update):
#     """
#     :type bot: telegram.bot.Bot
#     :type update: telegram.update.Update
#     """
#     data = json.loads(update.callback_query.data)
#     event_id = data['e']
#
#     session = get_db_session()
#
#     event = DB.get_event(session, event_id=event_id)
#
#     if event and not event.completed:
#         target_id = data['t']
#
#         update_dict = json.loads(event.description)
#         update_dict['loser'] = target_id
#
#         game = DB.get_game(session, event.game_id, options=[joinedload(Game.player_1),
#                                                             joinedload(Game.player_2),
#                                                             joinedload(Game.player_3),
#                                                             joinedload(Game.player_4)])
#         target_seat_no = get_player_seat_no(user=target_id, game=game)
#         winner_ids = []
#         for i in range(1, 5):
#             if i != target_seat_no:
#                 winner_ids.append(game.__getattribute__('player_{0}'.format(i)).username)
#         for i in range(0, len(winner_ids)):
#             update_dict['winner_{0}'.format(i + 1)] = winner_ids[i]
#
#         DB.update_event(session, event_id, {'description': json.dumps(update_dict), 'completed': 1})
#
#         # Create Transaction
#         DB.create_transaction(session, event_id=event_id, from_id=update_dict['loser'], to_id=update_dict['winner'],
#                               fan_no=update_dict['fan'], amount=amount)
#
#         # Update Message in Individual Chat
#         message = update.callback_query.message
#         bot.editMessageText(timeout=5, text=String.EAT_CONFIRM,
#                             chat_id=message.chat_id,
#                             message_id=message.message_id)
#
#         # Send Message to Group
#         from_player = DB.get_player(session, update_dict['loser'])
#         to_player = DB.get_player(session, update_dict['winner'])
#
#         text = random.choice(String.EAT_MESSAGES).format(winner_first=to_player.first_name,
#                                                          winner_last=to_player.last_name,
#                                                          loser_first=from_player.first_name,
#                                                          loser_last=from_player.last_name,
#                                                          fan=fan, amount=amount)
#
#         bot.sendMessage(chat_id=game.chat_id, text=text, timeout=5)
