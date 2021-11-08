import os
import glob
import csv
import uuid
import time
import requests
import datetime
from datetime import timedelta
from datetime import date as date_current
from django.db.models import Max

from xml.etree import ElementTree
from xml.dom import minidom
from django.http import HttpResponse
from wsgiref.util import FileWrapper  # this used in django
from mimetypes import guess_type
from functools import wraps
# from users.models import AllLogin
from binance.exceptions import BinanceAPIException
from django.contrib import messages
from django.utils.translation import gettext as _
from currency_converter import CurrencyConverter
from balances.models import Coin, CoinBalance
date_now = date_current.today().isoformat()
today = date_current.today()
date_today = today.strftime("%B %d, %Y")
url = "https://api.binance.com/api/v3/ticker/price?symbol="
c = CurrencyConverter()

generic_context = {
    'currency_symbol': '$',
    'currency': 'USD',
    'equity': 0,
    'positionAmt': 0,
    'loss': 0,
    'profit': 0,
    'available_balance_btc': 0,
    'locked_btc': 0,
    'pending_btc': 0,
    'spot_balance': 0,
    'futures_balance': 0,
    'available_balance': 0,
    'locked_balance': 0,
    'pending_balance': 0,
    'used_margin': 0,
    'free_margin': 0,
    'margin_level': 0,
    'opening_cost': 0,
    'current_valuation': 0,
    'fees': 0,
    'all_time_high': 0,
    'accumulated_profit': 0,
    'today_trade_volume': 0,
    'today_profit_volume': 0,
    'btc_amount': 0,
    'btc_balance': 0,
    'home_page': True,
}


def daterange(date1, date2):
    for n in range(int((date2 - date1).days) + 1):
        yield date1 + timedelta(n)


def generate_csv(user):
    csv_columns = [
        'Full Name', 'Email', 'Date Joined', 'Timezone',
        'Default Currency', 'Social Accounts'
    ]
    data = {
        'Full Name': user.get_full_name(),
        'Email': user.email,
        'Date Joined': user.date_joined,
        'Timezone': user.time_zone,
        'Default Currency': user.default_currency,
        'Social Accounts': 'Google, Facebook'
    }
    files = glob.glob('templates/csvfiles/*')
    for f in files:
        os.remove(f)

    csv_file = "personal_info.csv"
    file_path = f"templates/csvfiles/{csv_file}"

    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        writer.writerow(data)

    with open(file_path, 'r') as f:
        wrapper = FileWrapper(f)
        mimetype = 'application/force-download'
        gussed_mimetype = guess_type('.csv')
        if gussed_mimetype:
            mimetype = gussed_mimetype
        response = HttpResponse(wrapper, content_type=mimetype)
        response['Content-Disposition'] = "attachment;filename=%s" % csv_file
        response["X-SendFile"] = csv_file
        return response


def generate_ref_code():
    code = str(uuid.uuid4()).replace('-', '')[:12]
    return code


class persist_session_vars(object):
    """
    Some views, such as login and logout, will reset all session state.
    (via a call to ``request.session.cycle_key()`` or ``session.flush()``).
    That is a security measure to mitigate session fixation vulnerabilities.

    By applying this decorator, some values are retained.
    Be very aware what find of variables you want to persist.
    """

    def __init__(self, vars):
        self.vars = vars

    def __call__(self, view_func):

        @wraps(view_func)
        def inner(request, *args, **kwargs):
            # Backup first
            session_backup = {}
            for var in self.vars:
                try:
                    session_backup[var] = request.session[var]
                except KeyError:
                    pass

            # Call the original view
            response = view_func(request, *args, **kwargs)

            # Restore variables in the new session
            for var, value in session_backup.items():
                request.session[var] = value

            return response

        return inner


class HomeModules:
    def spot_positions_dict(request, client, symbol_dict, spot_positions_dict):
        try:
            for key in symbol_dict:  # symbol_dict = {symbol: [symbol_price, amount, value]}
                if key != 'USDT':
                    asset = key + 'USDT'
                    positions = client.get_all_orders(symbol=asset)
                    tp = '--'
                    sl = '--'
                    if positions:
                        for position in positions:
                            status = position['status']
                            type = position['type']
                            order_id = position['orderId']

                            # status: not filled, executed > 0
                            # set notification for spot open order executed
                            if float(position['executedQty']) > 0 and status != 'FILLED':
                                order_notified = request.session.get(f"order_id: {order_id}")
                                if not order_notified:
                                    msg = f"Spot Open Order {s}(type: {type}) was executed"
                                    messages.success(request, _(msg))
                                    request.session[f"order_id: {order_id}"] = order_id

                            if type in ['STOP_LOSS', 'TAKE_PROFIT', 'STOP_LOSS_LIMIT', 'TAKE_PROFIT_LIMIT']:
                                if position['stopPrice']:
                                    stopPrice = float(position['stopPrice'])
                                    sl = round(stopPrice, 2)
                                if position['unrealizedProfit']:
                                    take_profit = float(position['unrealizedProfit'])
                                    tp = round(take_profit, 2)
                                if position['totalUnrealizedProfit']:
                                    take_profit = float(position['totalUnrealizedProfit'])
                                    tp = round(take_profit, 2)

                            size = float(position['origQty'])
                            bal = float(client.get_asset_balance(key)['free'])
                            executedQty = float(position['executedQty'])
                            if status == 'FILLED' and executedQty > 0 and size + 0.5 <= bal:  # executed order i.e position
                                # fees += float(position['stopPrice'])
                                price = float(position['price'])
                                type = position['type']

                                # set notification for spot position(tp/sl)
                                # status: filled, type: tp/sl
                                order_notified = request.session.get(f"order_id: {order_id}")
                                if type in ['STOP_LOSS', 'TAKE_PROFIT'] and not order_notified:
                                    msg = _(f"Spot Position {sm}(type: {type}) was executed")
                                    messages.success(request, msg)
                                    request.session[f"order_id: {order_id}"] = order_id
                                multiple = 0
                                if type == 'LIMIT':
                                    multiple = price * executedQty
                                elif type == 'MARKET':
                                    multiple = float(position['cummulativeQuoteQty']) / float(position['origQty']) * executedQty
                                data = [size, multiple, executedQty, type, tp, sl]
                                if asset in spot_positions_dict:
                                    spot_positions_dict[asset].append(data)
                                else:
                                    spot_positions_dict[asset] = list()
                                    spot_positions_dict[asset].append(data)

            return spot_positions_dict
        except BinanceAPIException as e:
            # print(e.status_code)
            print('error_code_spot_positions_list', e.code)
            print('error_msg_spot_positions_list', e.message)
            return spot_positions_dict

    def position_valuation(request, client, opening_cost, current_valuation, spot_profit, today_trade_volume):
        futures_profit = 0
        futures_loss = 0
        accumulated_profit = 0
        today_profit_volume = 0
        try:
            for item in client.futures_position_information():
                entry_price = float(item['entryPrice'])
                mark_price = float(item['markPrice'])
                position_amount = float(item['positionAmt'])
                symbol = item['symbol']
                if entry_price > 0 and mark_price > 0 and position_amount > 0:
                    try:
                        pr = requests.get(url + symbol).json()['price']
                        cost = float(pr) * position_amount
                        cost = round(cost, 2)
                        print('f opening_cost', cost)
                        opening_cost += cost
                        current_valuation += mark_price * position_amount - entry_price * position_amount
                    except:
                        pass
            opening_cost = round(opening_cost, 2)
            current_valuation = round(current_valuation, 2)

            for item in client.futures_position_information():
                unrealized_profit = float(item['unRealizedProfit'])
                if unrealized_profit > 0:
                    futures_profit += unrealized_profit
                elif unrealized_profit < 0:
                    futures_loss += unrealized_profit

            data = client.futures_income_history()
            if data:
                for item in data:
                    if item['incomeType'] == 'COMMISSION' or item['incomeType'] == 'REALIZED_PNL' and float(item['income']) > 0:
                        t = time.strftime("%Y-%m-%d", time.gmtime(item['time'] / 1000))
                        if date_now == t:
                            accumulated_profit += float(item['income'])

            accumulated_profit += spot_profit
            accumulated_profit = round(accumulated_profit, 2)

            today_trade_volume = round(today_trade_volume, 2)
            if today_trade_volume > 0:
                today_profit_volume = accumulated_profit / today_trade_volume * 100

            today_profit_volume = round(today_profit_volume, 2)
            return opening_cost, current_valuation, futures_profit, futures_loss, accumulated_profit, today_profit_volume
        except BinanceAPIException as e:
            # print(e.status_code)
            print('error_msg_position_valuation: ', e.message)
            print('error_code: ', e.code)
            return opening_cost, current_valuation, futures_profit, futures_loss, accumulated_profit, today_profit_volume

    def trade_vol(request, client, symbol_dict, spot_used_margin):
        today_trade_volume = 0
        try:
            for key in symbol_dict:
                if key != 'USDT':
                    symbol = key + 'USDT'
                    my_trades = client.get_my_trades(symbol=symbol)
                    if my_trades:
                        for trade in my_trades:
                            margin = float(trade['price']) * float(trade['qty'])
                            spot_used_margin += margin
                            # commission = float(trade['commission'])
                            trade_time = time.strftime("%Y-%m-%d", time.gmtime(trade['time'] / 1000))
                            yesterday = datetime.datetime.now() - timedelta(1)
                            yesterday = datetime.datetime.strftime(yesterday, '%Y-%m-%d')
                            if trade_time == yesterday:
                                today_trade_volume += margin
            return today_trade_volume, spot_used_margin
        except BinanceAPIException as e:
            print('error_trade_vol: ', e.message)
            print('error_code: ', e.code)
            return today_trade_volume, spot_used_margin

    def graph_bal(request, client, symbol_dict, balance_list):
        # symbol_dict = {symbol: [symbol_price, amount, value]}
        for key in symbol_dict:
            symbol_price = symbol_dict[key][0]
            amount = symbol_dict[key][1]
            value = symbol_dict[key][2]

            if key == "BNB":
                color = "#F7931A"
            elif key == "BTC":
                color = "#F7931A"
            elif key == "ETH":
                color = "#A6DF00"
            elif key == "LTC":
                color = "#FF6600"
            elif key == "USDT":
                color = "#2CA07A"
            elif key == "TRX":
                color = "#FF6600"
            elif key == "TRX":
                color = "#A6DF00"
            else:
                color = "#FF6600"
            coin_icon = Coin.objects.get(name=key)
            balance_list.append([key, symbol_price, amount, value, color, coin_icon])
            # graph_balance_dict[symbol] = amount
            # Create Coin if doesn't exist one
            coin_balance = CoinBalance.objects.filter(user=request.user, coin=coin_icon, date=date_today).first()
            if not coin_balance:
                CoinBalance.objects.create(user=request.user, coin=coin_icon, balance=amount, date=date_today)
            else:
                coin_balance.balance = amount
                coin_balance.save()

        return balance_list

    def analytics_graph(request, client, user, symbol_dict):
        balances_dict = dict()
        date_dict = dict()
        if symbol_dict:
            for coin in symbol_dict:  # {symbol: [symbol_price, amount, value]}
                coin_balances = CoinBalance.objects.filter(user=user, coin__name=coin).order_by('date')[:10]
                for item in coin_balances:
                    date = item.date.split(',')[0]
                    amount = float(item.balance)
                    if coin == 'USDT':
                        balance = amount
                    else:
                        coin_price = symbol_dict[coin][0]
                        balance = coin_price * amount

                    balance = round(balance, 2)
                    if coin in balances_dict:
                        balances_dict[coin].append(balance)
                    else:
                        balances_dict[coin] = list()
                        balances_dict[coin].append(balance)

                    if coin in date_dict:
                        date_dict[coin].append(date)
                    else:
                        date_dict[coin] = list()
                        date_dict[coin].append(date)

        print('balances_dict n', balances_dict)

        for coin in balances_dict:
            length = len(balances_dict[coin])
            if length == 1:
                balances_dict[coin] = [0, 0] + balances_dict[coin]
            elif length == 2:
                balances_dict[coin] = [0] + balances_dict[coin]

        lens = list()
        for key in balances_dict:
            lens.append(len(balances_dict[key]))

        gt = max(lens)
        for key in balances_dict:
            length = len(balances_dict[key])
            if length < gt:
                lis = [0] * (gt - length)
                balances_dict[key] = lis + balances_dict[key]

        print('balances_dict n', balances_dict)

        all_time_high = 0
        for symbol in symbol_dict:  # {symbol: [symbol_price, amount, value]}
            objs = CoinBalance.objects.filter(user=user, coin__name=symbol)
            max_value = objs.aggregate(Max('balance'))['balance__max']
            if max_value:
                max_value = float(max_value)
            if not max_value:
                max_value = 0
            if symbol == 'USDT':
                all_time_high += max_value
            else:
                try:
                    price = symbol_dict[symbol][0]
                except:
                    price = requests.get(url + symbol + 'USDT').json()['price']
                max_value = float(price) * max_value
                all_time_high += max_value

        all_time_high = round(all_time_high, 2)
        return balances_dict, date_dict, all_time_high

    def spot_positions(request, client, symbol_dict, spot_positions_dict, current_valuation, opening_cost, spot_profit, spot_loss):
        # Modify the spot_position to contain the desired values
        spot_positions_l = list()
        try:
            if spot_positions_dict:  # {symbol: [size, multiple, executedQty, type, tp, sl]}
                for key in spot_positions_dict:  # key is symbol e.g BTCUSDT
                    size = 0
                    sum_of_multiples = 0
                    sum_of_excetued = 0
                    tp = None
                    sl = None
                    for a_list in spot_positions_dict[key]:
                        size += a_list[0]
                        sum_of_multiples += a_list[1]
                        sum_of_excetued += a_list[2]
                        tp = a_list[4]
                        sl = a_list[5]

                    entry_price = sum_of_multiples / sum_of_excetued
                    mark_price = symbol_dict[key[:-4]][0]  # {symbol: [symbol_price, amount, value]}
                    pnl = (mark_price - entry_price) * size

                    ROI = pnl/entry_price * 100
                    ROI = round(ROI, 2)
                    pnl = round(pnl, 2)
                    size = round(size, 7)
                    entry_price = round(entry_price, 4)

                    # [symbol, size, entry_price, mark_price, pnl, ORI]
                    spot_positions_l.append([key, size, entry_price, mark_price, pnl, ROI, f"{tp}/{sl}"])

            # current valuation, opening cost and profit, loss
            if spot_positions_l:
                for position in spot_positions_l:
                    # [sm, size, entry_price, mark_price, pnl, ROI, f"{tp}/{sl}"]
                    size = position[1]
                    entry_price = position[2]
                    mark_price = position[3]
                    pnl = position[4]
                    current_valuation += (mark_price - entry_price) * size
                    cost = mark_price * size
                    cost = round(cost, 2)
                    opening_cost += cost

                    if pnl > 0:
                        spot_profit += pnl
                    if pnl < 0:
                        spot_loss += pnl

            spot_loss = round(spot_loss, 2)
            spot_profit = round(spot_profit, 2)
            return spot_positions_l, current_valuation, opening_cost, spot_profit, spot_loss
        except BinanceAPIException as e:
            # print(e.status_code)
            print('error_code_spot_positions', e.code)
            print('error_msg_spot_positions', e.message)
            return spot_positions_l, current_valuation, opening_cost, spot_profit, spot_loss

    def labels_colors_percents(request, client, balance_list):
        spot_balance = 0
        label_list = list()
        item_percentages = list()
        color_list = list()
        if balance_list:  # [key, symbol_price, amount, value, color, coin_icon]
            for item in balance_list:
                spot_balance += item[3]
            for item in balance_list:
                label_list.append(item[0])
                percentage = (item[3] / spot_balance) * 100
                percentage = round(percentage, 2)
                item_percentages.append(percentage)
                color_list.append(item[4])
            spot_balance = round(spot_balance, 2)
        return spot_balance, label_list, item_percentages, color_list

    def futures_bal(request, client):
        futures_balance = 0
        if client.futures_account_balance():
            for item in client.futures_account_balance():
                bal = float(item['balance'])
                if bal > 0:
                    try:
                        symbol = item['asset']
                        if symbol == 'USDT':
                            price = bal
                            futures_balance += price
                        else:
                            price = requests.get(url + symbol + "USDT").json()['price']
                            price = float(price) * bal
                            futures_balance += price
                    except:
                        pass
        futures_balance = round(futures_balance, 2)
        return futures_balance

    def open_orders_spot(request, client, spot_used_margin):
        open_orders_spot = list()
        try:
            if client.get_open_orders():
                for item in client.get_open_orders():
                    amount = float(item['origQty'])
                    type = item['type']
                    if amount > 0:
                        # [symbol, date, type, side, amount, price]
                        symbol = item['symbol']
                        order_date = time.strftime("%d %b %Y", time.localtime(item['time'] / 1000))
                        # trade_fee = client.get_trade_fee(symbol=symbol)[0]
                        # trade_fee = float(trade_fee['makerCommission']) + float(trade_fee['takerCommission'])
                        side = item['side']
                        price = float(item['price'])
                        symbol_quoteAsset = client.get_symbol_info(symbol)['quoteAsset']
                        # remaining_balance = client.get_asset_balance(symbol)['free']
                        filled = float(item['executedQty']) / amount * 100
                        filled = round(filled, 2)
                        amount = round(amount, 4)
                        price = round(price, 4)
                        type = type.replace("_", " ")
                        open_orders_spot.append((symbol, order_date, type, side, price, amount, filled))
                        # used margin
                        spot_used_margin += float(amount) * float(price)
            return open_orders_spot, spot_used_margin
        except BinanceAPIException as e:
            # print(e.status_code)
            print('error_code_open_orders_spot', e.code)
            print('error_msg_open_orders_spot', e.message)
            return open_orders_spot, spot_used_margin

    def deposits(request, client):
        pending_balance = 0
        deposit_list = list()
        try:
            # [id, txid, type, amount, date, hash, status]
            deposits = client.get_deposit_history()
            if deposits:
                n = 1
                for deposit in deposits:
                    deposit['id'] = n
                    n += 1
                    if deposit['status'] == 0:
                        pending_balance += float(deposit['amount'])

                for deposit in deposits[:10]:
                    tx_id = deposit['txId']
                    deposit_notified = request.session.get(f"tx id: {tx_id}")
                    if float(deposit['status']) == 1 and not deposit_notified:
                        messages.success(request, _(f"Successful Deposit(txid: {tx_id})"))
                        request.session[f"tx id: {tx_id}"] = tx_id

                    date = time.strftime("%d %b %Y", time.localtime(deposit['insertTime'] / 1000))
                    tx_id = deposit['txId'].split(' ')[-1]
                    deposit_item = (
                        deposit['id'], tx_id, deposit['coin'], deposit['amount'], date, deposit['address'],
                        deposit['status'])
                    deposit_list.append(deposit_item)
            return pending_balance, deposit_list
        except BinanceAPIException as e:
            # print(e.status_code)
            print('error_code_deposits', e.code)
            print('error_msg_deposits', e.message)
            return pending_balance, deposit_list

    def withdrawls(request, client, pending_balance):
        pending_balance = pending_balance
        try:
            withdrawals = client.get_withdraw_history()
            if withdrawals:
                withdrawal_id = 1
                for withdrawal in withdrawals:
                    tx_id = withdrawal['txId']
                    withdrawal_notified = request.session.get(f"tx id: {tx_id}")
                    if float(withdrawal['status']) == 1 and not withdrawal_notified:
                        messages.success(request, _(f"Successful Withdrawal(txid: {tx_id})"))
                        request.session[f"tx: {tx_id}"] = tx_id
                    withdrawal['id'] = withdrawal_id
                    withdrawal_id += 1
                    if withdrawal['status'] == 0:
                        pending_balance += float(withdrawal['amount'])

                withdrawals = withdrawals[:10]
                for withdrawal in withdrawals:
                    date = withdrawal['applyTime'].split(" ")[0]
                    withdrawal['applyTime'] = date
            return withdrawals, pending_balance
        except BinanceAPIException as e:
            # print(e.status_code)
            print('error_code_withdrawls', e.code)
            print('error_msg_withdrawls', e.message)
            return [], pending_balance

    def transfers(request, client):
        transfer_list = list()
        try:
            transfers = client.new_transfer_history(type='MAIN_UMFUTURE')
            if transfers:
                for item in transfers['rows']:
                    trans_id = item['tranId']
                    trans_notified = request.session.get(f"trans id: {trans_id}")
                    if item['status'] == 'CONFIRMED' and not trans_notified:
                        messages.success(request, _(f"Successful Transfer(tranId: {trans_id})"))
                        request.session[f"trans id: {trans_id}"] = trans_id

                    transfer_date = time.strftime("%d %b %Y", time.localtime(item['timestamp'] / 1000))
                    symbol = item['asset']
                    asset = symbol
                    amount = item['amount']
                    trans_id = str(item['tranId'])
                    status = item['status']
                    transfer_list.append((1, trans_id, symbol, asset, amount, transfer_date, status))
            return transfer_list
        except BinanceAPIException as e:
            # print(e.status_code)
            print('error_code_transfers', e.code)
            print('error_msg_transfers', e.message)
            return transfer_list
