from pybit.unified_trading import HTTP
from datetime import datetime
from api_keys import api_k,api_s
session = HTTP(
    testnet=False,
    api_key=api_k,
    api_secret=api_s,
)
symbol = 'BTCUSDT'


def get_last_high_low_close():
    try:
        k = session.get_kline(
            category='linear',  # для фьчерсов
            symbol=symbol,
            interval='1',
            limit=1
        )

        return float(k['result']['list'][0][2]), float(k['result']['list'][0][3]), float(k['result']['list'][0][4])
    except:
        print('error in get_last_high_low_close')
        return 0, 0, 0


def get_open_orders():
    try:
        oo = session.get_open_orders(
            category="linear",
            symbol=symbol,
        )
        return oo['result']['list']
    except:
        print('error in get_open_orders')
        return 0


def count_open_trades():
    oo = session.get_open_orders(
        category="linear",
        symbol=symbol,
    )
    list2 = oo['result']['list']
    return len(list2)


def cancel_all_orders():
    try:
        oo = session.get_open_orders(
            category="linear",
            symbol=symbol,
        )

        list2 = oo['result']['list']
        for i in list2:
            o_id = i['orderId']
            session.cancel_order(
                category="linear",
                symbol=symbol,
                orderId=o_id
            )
    except:
        print('error in cancel_all_orders')


def make_up_orders(_qty, price):
    # Размещаем ордер на покупку при достижении цены вверх и SL
    try:
        session.place_order(
            category="linear",
            symbol=symbol,
            side="Buy",
            orderType="Market",
            qty=str(_qty),
            triggerPrice=str(price),
            triggerBy="LastPrice",
            triggerDirection=1,
            stopLoss=str(price - 2)
        )
    except:
        print('error in make_up_orders')
        return 0
    return 1


def make_down_orders(_qty, price):
    # Размещаем ордер на продажу при достижении цены вниз и SL
    try:
        session.place_order(
            category="linear",
            symbol=symbol,
            side="Sell",
            orderType="Market",
            qty=str(_qty),
            triggerPrice=str(price),
            triggerBy="LastPrice",
            triggerDirection=2,
            stopLoss=str(price + 2)
        )
    except:
        print('error in make_down_orders')
        return 0
    return 1


def if_in_order():
    try:
        a = session.get_positions(
            category="linear",
            symbol=symbol,
        )
        return a['result']['list'][0]['side']
    except:
        print('error in if_in_order')
        return 0


def buy_market(_qty, _last_SL):
    tmp_qty = 0
    cancel_all_orders()
    _side = if_in_order()
    if _side == "Buy":
        tmp_qty = 0
    elif _side == "None":
        tmp_qty = round(_qty)
    elif _side == "Sell":
        tmp_qty = round(_qty * 2)
    try:
        if tmp_qty != 0:
            session.place_order(
                category="linear",
                symbol=symbol,
                side="Sell",
                orderType="Market",
                qty=str(tmp_qty),
                stopLoss=str(_last_SL - 2)
            )
    except:
        print('error buy_market')
        return 0
    return 1


def sell_market(_qty, _last_SL):
    tmp_qty = 0
    cancel_all_orders()
    _side = if_in_order()
    if _side == "Buy":
        tmp_qty = round(_qty * 2)
    elif _side == "None":
        tmp_qty = round(_qty)
    elif _side == "Sell":
        tmp_qty = 0
    try:
        if tmp_qty != 0:
            session.place_order(
                category="linear",
                symbol=symbol,
                side="Sell",
                orderType="Market",
                qty=str(tmp_qty),
                stopLoss=str(_last_SL + 2)
            )
    except:
        print('error sell_market')
        return 0
    return 1


vah = 26507
poc = 26431
val = 26394
qty = 0.018
last_SL = 26822
upper_block_high = round(vah * 1.005)
upper_block_low = vah
upper_block_lower_low = upper_block_low
upper_block_moved = False
lower_block_high = val
lower_block_low = round(0.995 * val)
lower_block_moved = False

high, low, now = 0, 0, 0
in_process = False
side = ''
position = -1
first_place = False
changed_sl = False
cancel_all_orders()
prev_position = -2
prev_side = ''
to_out = ''
tmp = to_out
count = 0

while True:
    side = if_in_order()
    if side != 'None':
        in_process = True

    else:
        if in_process:
            if last_SL != 0:
                if now > last_SL:
                    buy_market(qty, last_SL)
                elif now < last_SL:
                    sell_market(qty, last_SL)
            # in_process = False
            # first_place = False
            # cancel_all_orders()
            # print('cancel 1')
            # changed_sl = False

    high, low, now = get_last_high_low_close()

    if not in_process and not first_place and now != 0:
        first_place = True
        if vah > now > poc:
            position = 1
            make_up_orders(qty, vah)
            make_down_orders(qty, poc)
        elif poc > now > val:
            position = 2
            make_up_orders(qty, poc)
            make_down_orders(qty, val)
        elif now > vah:
            position = 0
            make_down_orders(qty, vah)
        elif now < val:
            position = 3
            make_up_orders(qty, val)
    elif now != 0:
        if side == 'Buy':

            if last_SL != 0:
                count = count_open_trades()
                if count == 0:
                    res = make_down_orders(qty * 2, last_SL)
                    if res == 0:
                        sell_market(qty, last_SL)

            if vah > now > poc:
                if position != 1:
                    position = 1
                    changed_sl = True
                    last_SL = poc
                    cancel_all_orders()
                    res = make_down_orders(qty * 2, last_SL)
                    if res == 0:
                        sell_market(qty, last_SL)  # 1
            elif poc > now > val:
                if position != 2:
                    position = 2
                    changed_sl = True
                    last_SL = val
                    cancel_all_orders()
                    res = make_down_orders(qty * 2, last_SL)
                    if res == 0:
                        sell_market(qty, last_SL)  # 2
            elif now > vah:
                if position != 0 and position != 10 and position != 11:
                    position = 0
                    changed_sl = True
                    last_SL = vah
                    cancel_all_orders()
                    res = make_down_orders(qty * 2, last_SL)
                    if res == 0:
                        sell_market(qty, last_SL)  # 3

                # зона upper_block
                # Если мы выше крышки прикрепленного блока открепляем блок
                # и выставляем плавающие гранцы
                elif high > upper_block_high and position == 0:
                    upper_block_moved = True
                    position = 10
                    upper_block_high = high
                    upper_block_low = round(upper_block_high * 0.996)
                    cancel_all_orders()
                    # print('cancel5')
                    changed_sl = True
                    last_SL = upper_block_low
                    res = make_down_orders(qty * 2, last_SL)
                    if res == 0:
                        sell_market(qty, last_SL)  # 4

                # если верхний плавающий блок перешел из sell в buy
                elif position == 11:
                    position = 10
                    upper_block_low = upper_block_high
                    upper_block_high = high
                    cancel_all_orders()
                    # print('cancel6')
                    changed_sl = True
                    last_SL = upper_block_low
                    res = make_down_orders(qty * 2, last_SL)
                    if res == 0:
                        sell_market(qty, last_SL)  # 5

                # обновляем крышку верхнего блока
                elif position == 10:
                    if high > upper_block_high:
                        upper_block_high = high
                        upper_block_low = max(round(upper_block_high * 0.996), upper_block_low)
                        cancel_all_orders()
                        # print('cancel7')
                        changed_sl = True
                        last_SL = upper_block_low
                        res = make_down_orders(qty * 2, last_SL)
                        if res == 0:
                            sell_market(qty, last_SL)  # 6

                        # конец зоны upper_block

            # если нет записанной позиции но мы в позиции лонг
            if position == -1:
                # Если мы ниже VAL
                if now < val:
                    lower_block_high = round(now * 1.0015)
                    lower_block_low = round(now * 0.9985)
                    cancel_all_orders()
                    position = 31
                    # print('cancel8*')
                    changed_sl = True
                    last_SL = lower_block_low
                    res = make_down_orders(qty * 2, last_SL)
                    if res == 0:
                        sell_market(qty, last_SL)  # 7*

            # lower_block buy-side
            # Если мы были в плавающем нижнем блоке и исполнен ордер на покупку
            if position == 30:
                position = 31
                lower_block_low = lower_block_high
                lower_block_high = high
                cancel_all_orders()
                # print('cancel8')
                changed_sl = True
                last_SL = lower_block_low
                res = make_down_orders(qty * 2, last_SL)
                if res == 0:
                    sell_market(qty, last_SL)  # 7

            # Меняем верхнюю границу нижнего блока
            if position == 31:
                if high > lower_block_high:
                    lower_block_high = high
                    lower_block_low = max(lower_block_low, round(lower_block_high * 0.996))
                    cancel_all_orders()
                    # print('cancel9')
                    changed_sl = True
                    last_SL = lower_block_low
                    res = make_down_orders(qty * 2, last_SL)
                    if res == 0:
                        sell_market(qty, last_SL)  # 8

            # конец зоны lower_block
            # ----------------------------------------

            # # Подумать есть ли в этом блоке смысл или удалить Возможно это не сработает ни при каких условиях
            # if prev_position == position and not changed_sl:
            #     if position != -1:
            #         print('было касание но невышли в следующую зону 1 ' + str(prev_position) + ' ' + str(position))
            #     else:
            #         # Подумать есть ли в этом блоке смысл или удалить
            #         # Зоны со * были удалены/закомментированы
            #         if now < val:
            #             position = 3
            #             # --------------------*
            #             if now < lower_block_low:
            #                 if side == 'Sell':
            #                     position = 30
            #                 if side == 'Buy':
            #                     position = 31
            #             # --------------------*
            #         else:
            #             position = 0
            #             # --------------------*
            #             if now > upper_block_high:
            #                 if side == 'Buy':
            #                     position = 10
            #                 if side == 'Sell':
            #                     position = 11
            #             # --------------------*


        # ---------------------------------
        elif side == 'Sell':
            if last_SL != 0:
                count = count_open_trades()
                if count == 0:
                    res = make_up_orders(qty * 2, last_SL)
                    if res == 0:
                        sell_market(qty, last_SL)

            if vah > now > poc:
                if position != 1:
                    # print(side + ' changed ls')
                    position = 1
                    changed_sl = True
                    last_SL = vah
                    cancel_all_orders()
                    # print('cancel10')
                    res = make_up_orders(qty * 2, last_SL)
                    if res == 0:
                        buy_market(qty, last_SL)  # 1

            elif poc > now > val:
                if position != 2:
                    # print(side + ' changed ls')
                    position = 2
                    changed_sl = True
                    last_SL = poc
                    cancel_all_orders()
                    # print('cancel11')
                    res = make_up_orders(qty * 2, last_SL)
                    if res == 0:
                        buy_market(qty, last_SL)  # 2

            elif now < val:
                if position != 3 and position != 30 and position != 31:
                    # print(side + ' changed ls')
                    position = 3
                    changed_sl = True
                    last_SL = val
                    res = make_up_orders(qty * 2, last_SL)
                    if res == 0:
                        buy_market(qty, last_SL)  # 3

                # зона lower_block
                # При выхода из лоя нижнего блока открепляем нижний блок
                elif low < lower_block_low and position == 3:
                    lower_block_moved = True
                    position = 30
                    lower_block_low = low
                    lower_block_high = round(lower_block_low * 1.004)
                    cancel_all_orders()
                    # print('cancel12')
                    changed_sl = True
                    last_SL = lower_block_high
                    res = make_up_orders(qty * 2, last_SL)
                    if res == 0:
                        buy_market(qty, last_SL)  # 4

                # при обратном понижении нижнего блока
                elif position == 31:
                    position = 30
                    lower_block_high = lower_block_low
                    lower_block_low = low
                    cancel_all_orders()
                    # print('cancel13')
                    changed_sl = True
                    last_SL = lower_block_high
                    res = make_up_orders(qty * 2, last_SL)
                    if res == 0:
                        buy_market(qty, last_SL)  # 5

                # меняем нижнюю границу и SL нижнего блока
                elif position == 30:
                    if low < lower_block_low:
                        lower_block_low = low
                        lower_block_high = min(round(lower_block_low * 1.004), lower_block_high)
                        cancel_all_orders()
                        changed_sl = True
                        last_SL = lower_block_high
                        # print('cancel14')
                        res = make_up_orders(qty * 2, last_SL)
                        if res == 0:
                            buy_market(qty, last_SL)  # 6

                        # конец зоны lower_block

            # если нет записанной позиции но мы в позиции short
            if position == -1:
                # Если мы выше VAH
                if now > vah:
                    upper_block_high = round(now * 1.0015)
                    upper_block_low = round(now * 0.9985)
                    cancel_all_orders()
                    changed_sl = True
                    last_SL = upper_block_high
                    position = 11
                    # print('cancel8*')
                    res = make_up_orders(qty * 2, last_SL)
                    if res == 0:
                        buy_market(qty, last_SL)  # 7*

            # upper_block sell-side

            # Если у нас сработал ордер Sell а мы были в верхнем блоке
            if position == 10:
                position = 11
                upper_block_high = upper_block_low
                upper_block_low = low
                cancel_all_orders()
                # print('cancel15')
                changed_sl = True
                last_SL = upper_block_high
                res = make_up_orders(qty * 2, last_SL)
                if res == 0:
                    buy_market(qty, last_SL)  # 7

            # Понижаем нижнюю границу верхнего блока при движении цены вниз
            if position == 11:
                if low < upper_block_low:
                    upper_block_low = low
                    upper_block_high = min(upper_block_high, round(upper_block_low * 1.004))
                    changed_sl = True
                    last_SL = upper_block_high
                    cancel_all_orders()
                    # print('cancel16')
                    res = make_up_orders(qty * 2, last_SL)
                    if res == 0:
                        buy_market(qty, last_SL)  # 8

            # конец зоны upper_block
            # ---------------------------------------------------

            # if prev_position == position and not changed_sl:
            #     if position != -1:
            #         print('было касание но невышли в следующую зону 2 ' + str(prev_position) + ' ' + str(position))
            #     else:
            #         if now < val:
            #             position = 3
            #             if now < lower_block_low:
            #                 if side == 'Sell':
            #                     position = 30
            #                 if side == 'Buy':
            #                     position = 31
            #         else:
            #             position = 0
            #             if now > upper_block_high:
            #                 if side == 'Buy':
            #                     position = 10
            #                 if side == 'Sell':
            #                     position = 11

            # prev_position = position
    side = if_in_order()
    # Если вернусли в первую и вторую зону сбросить верхний и нижний блок
    if prev_position == 10 or prev_position == 11 or prev_position == 30 or prev_position == 31:
        if position == 1 or position == 2:
            upper_block_high = round(vah * 1.005)
            upper_block_low = vah
            upper_block_lower_low = upper_block_low
            upper_block_moved = False
            lower_block_high = val
            lower_block_low = round(0.995 * val)
            lower_block_moved = False

    to_out = f'position: {position} prev_position: {prev_position}\nSide: {side} last_SL: {last_SL}' \
             f'\nUBH:{upper_block_high} UBL:{upper_block_low} \nLBH:{lower_block_high} LBL:{lower_block_low}'
    if tmp != to_out:
        date = datetime.now()
        print(date)
        print(to_out)
        print('-----------------------------------------------------')
        tmp = to_out

    if side == 'None' and last_SL != 0:
        print('side is none')
        if now > last_SL:
            try:
                buy_market(qty, last_SL)  # 9
            except:
                print('error in market order buy at the end')
        elif now > last_SL:
            try:
                sell_market(qty, last_SL)  # 9
            except:
                print('error in market order sell at the end')

    if count != 100:
        count = count + 1
    else:
        date = datetime.now()
        print(date)
        print('Я работаю не ссы')
        count = 0
    prev_position = position
