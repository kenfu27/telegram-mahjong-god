# -*- coding: utf-8 -*-


class String(object):
    # Register
    REGISTER_SUCCESSFUL = u'註冊成功啊死賭鬼，去開枱啦屌你老味'
    REGISTER_FAIL = u'你咪已經註左冊囉戇鳩仔'

    # Error
    ERROR_NOT_REGISTERED = u'你邊撚個啊 我唔撚識你啊\n\r同我開個單人房打 /start 先返黎啦'
    ERROR_PRIVATE_CHAT = u'單人房開乜撚野枱啊死毒撚'
    ERROR_EXISTING_GAME = u'{0} {1} 一個人點打兩枱啊 你估你係李騰啊'
    ERROR_NO_GAME = u'打空氣啊你 一係打 /join 一係返屋企打飛機啦'
    ERROR_LEAVE_NO_GAME = u'走乜撚野姐走 未坐低就嗌走'
    ERROR_SAME_SEAT = u'係咪玩野啊 {0} {1} 我知你坐嗰個位啦 再禁我J都斬撚斷你'
    ERROR_SEAT_TAKEN = u'{0} {1} 你咁鐘意坐大脾 俾支騰棍你坐'
    ERROR_NOT_ENOUGH_PLAYER = u'唔夠人點開波啊戇鳩仔'
    ERROR_NO_GAME_EAT = u'食屎啦你 唔係打緊就死撚開啦'

    # Start Game
    START_GAME = u'開波'
    START_GAME_ASK_PRICE = u'打打打 打幾大啊?'
    START_GAME_SELECT_SEAT = u'打骰執位啦柒頭'
    START_GAME_CHOSE_SEAT = u'{0} {1} 坐左落{2}位'
    START_GAME_CHANGE_SEAT = u'{0} {1} 數都唔識數 坐{2}位走去禁{3}位'

    # Actions
    ACTION_ASK_PRICE = 'ask_price'
    ACTION_SELECT_SEAT = 'select_seat'
    ACTION_START_GAME = 'start_game'
    ACTION_EVENT_CANCEL = 'event_cancel'
    ACTION_EAT_SELECT_WINNER = 'eat_winner'
    ACTION_EAT_SELECT_LOSER = 'eat_loser'
    ACTION_EAT_SELECT_FAN = 'eat_fan'
    ACTION_SELF_TOUCH_SELECT_WINNER = 'self_touch_winner'
    ACTION_SELF_TOUCH_SELECT_FAN = 'self_touch_fan'
    ACTION_2_EAT_SELECT_WIN_1 = '2_eat_win_1'
    ACTION_2_EAT_SELECT_FAN_1 = '2_eat_fan_1'
    ACTION_2_EAT_SELECT_WIN_2 = '2_eat_win_2'
    ACTION_2_EAT_SELECT_FAN_2 = '2_eat_fan_2'
    ACTION_2_EAT_SELECT_TARGET = '2_eat_target'
    ACTION_3_SELECT_TARGET = '3_eat_target'
    ACTION_3_EAT_SELECT_FAN_1 = '3_eat_fan_1'
    ACTION_3_EAT_SELECT_FAN_2 = '3_eat_fan_2'
    ACTION_3_EAT_SELECT_FAN_3 = '3_eat_fan_3'
    ACTION_ON_9_SELECT_TARGET = 'on9_target'
    ACTION_END_GAME_CONFIRM = 'end_confirm'
    ACTION_HISTORY_SELECT_GAME = 'history_game'
    ACTION_HISTORY_LIST = 'history_list'
    ACTION_CANCEL = 'cancel'

    # Fan
    FAN_10 = u'十番'
    FAN_9 = u'九番'
    FAN_8 = u'八番'
    FAN_7 = u'七番'
    FAN_6 = u'六番'
    FAN_5 = u'五番'
    FAN_4 = u'四番'
    FAN_3 = u'三番'

    # Price
    PRICE_8f64 = FAN_8 + u' 64'
    PRICE_8f128 = FAN_8 + u' 128'
    PRICE_10f128 = FAN_10 + u' 128'
    PRICE_10f256 = FAN_10 + u' 256'

    # Seating
    SEAT_1 = u'東'
    SEAT_2 = u'南'
    SEAT_3 = u'西'
    SEAT_4 = u'北'

    # Game Status
    SAME_JONG_MESSAGE = u'冧莊！{set}風{round}局 *{jong_first} {jong_last}* 做莊'
    NEXT_JONG_MESSAGE = u'過莊！{set}風{round}局 *{jong_first} {jong_last}* 做莊'

    # Eat
    EAT_ASK_WINNER = u'邊個食糊？'
    EAT_ASK_LOSER = u'威喇威喇 食邊個傻閪啊?'
    EAT_ASK_PRICE = u'勁勁勁 食幾大啊?'
    EAT_CONFIRM = u'數已入'
    EAT_MESSAGES = [
        u'{winner_first} {winner_last}食左個傻西{loser_first} {loser_last} {fan}番贏左{amount}蚊',
        u'{loser_first} {loser_last}戇鳩鳩咁出銃{fan}番俾{winner_first} {winner_last}'
    ]

    # Self Touch
    SELF_TOUCH_ASK_WINNER = u'邊個仆街自摸？'
    SELF_TOUCH_ASK_PRICE = u'自摸幾多番？'
    SELF_TOUCH_MESSAGES = [
        u'{winner_first} {winner_last} 自摸{fan}番！ 位位{amount}蚊！',
        u'{winner_first} {winner_last} 又屎忽撞騰棍自摸{fan}番喇'
    ]

    # 2 Eat
    EAT_2_ASK_WINNER_1 = u'第一個邊個食？'
    EAT_2_ASK_PRICE_1 = u'第一個食幾多番？'
    EAT_2_ASK_WINNER_2 = u'第二個邊個食？'
    EAT_2_ASK_PRICE_2 = u'第二個食幾多番？'
    EAT_2_ASK_TARGET = u'邊個傻閪一炮雙響？'
    EAT_2_MESSAGES = [
        u'{loser_first} {loser_last} 一炮雙響！\n\r'
        u'出銃俾 {winner_1_first} {winner_1_last} ({fan_1}番) 同 {winner_2_first} {winner_2_last} ({fan_2}番)'
    ]

    # 3 Eat
    EAT_3_ASK_TARGET = u'邊個超級大傻閪一炮三響？'
    EAT_3_ASK_PRICE = u'{winner_first} {winner_last}食幾多番？'
    EAT_3_MESSAGES = [
        u'超級大傻閪 {loser_first} {loser_last} 一炮三響！\n\r'
        u'出銃俾 {winner_1_first} {winner_1_last} ({fan_1}番)，'
        u'{winner_2_first} {winner_2_last} ({fan_2}番)，'
        u'{winner_3_first} {winner_3_last} ({fan_3}番)'
    ]

    # Draw
    DRAW_MESSAGES = [
        u'成班垃圾食唔到糊，流局！'
    ]

    # On9
    ON_9_ASK_TARGET = u'邊個食詐糊？'
    ON_9_MESSAGES = [
        u'戇鳩仔{loser_first} {loser_last}食詐糊！位位爆棚！'
    ]

    # End Game
    END_GAME_CONFIRM = u'係咪真係打完架？揾多個人禁打完'
    END_GAME_MESSAGE = u'打撚完！'

    # History
    HISTORY_ASK_GAME = u'想睇邊局？'

    NO_ONE = u'冇人'
    CANCEL = u'禁錯 對唔撚住'
    CANCEL_CONFIRM = u'再禁錯打撚死你'
    BEFORE = u'之前'
    AFTER = u'之後'
