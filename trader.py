import json
import signal
import sys
import time
from cryptopia_api import Api

def get_keys(file):
    with open(file) as keys:
        keys_json = json.load(keys)
        keys.close()
    return str(keys_json['public']), str(keys_json['secret'])

public_key, private_key = get_keys('test.json');

cryptopia = Api(public_key, private_key)
#GET ELECTRONEUM BALANCE
def get_etn_balance():
    response, error = cryptopia.get_balance('ETN')
    if error is not None:
        print error
    else:
        bal = response['Available']
        return bal
#GET ELECTRONEUM PRICE
def get_etn_usdt_price():
    response, error = cryptopia.get_market('ETN_USDT')
    if error is not None:
        print error
    else:
        price = response['LastPrice']
        return price
#SELL ETN FOR ETN_USDT
def trade(buysell, price, amount):
    response, error = cryptopia.submit_trade('ETN//USDT', buysell, price, amount)
    if error is not None:
        print error
    else:
        return response['OrderID']
def check_trade():
    if error is not None:
        print error
    else:
        response, error = cryptopia.get_openorders('ETN_USDT')
        return str(response['Remaining']), str(response['Amount']), str(response['Rate'])
def cancel_trade():
    response, error = cryptopia.cancel_trade(trade_type, order_id)

def main():
    exit = False
    state = 0
    while not exit:

        if state == 0:
            balance = get_etn_balance()
            current_price = get_etn_usdt_price()
            print "Your ETN balance is %s" %str(balance)
            print "The current ETN/USDT price is %s" %str(current_price)
            active_balance = input("How much ETN would you like to risk in this run?(#)")
            sell_threshold = input("At what level growth relative to the current price should the sale be initiated? (%)")
            loss_prevention_threshold = input("At what level should loss be abated relative to sale price? (%)")
            purchase_threshold = input("At what level gain should purchase be initiated relative to the sale price. (%)")
            sell_threshold = sell_threshold * .01
            loss_prevention_threshold = loss_prevention_threshold * .01
            purchase_threshold = purchase_threshold * .01
            sell_price = current_price + (sell_threshold * current_price)
            purchase_price = sell_price - (sell_price * purchase_threshold)
            loss_prevention_price = (sell_price + (sell_price * loss_prevention_threshold))
            print "ETN will be sold for USDT if price reaches %s" %str(sell_price)
            state = 1

        elif state == 1:
            time.sleep(3)
            current_price = get_etn_usdt_price()
            print "The current price is %s" % str(current_price)
            if current_price < sell_price:
                sell_price = current_price + (sell_threshold * current_price)
                purchase_price = sell_price - (sell_price * purchase_threshold)
                loss_prevention_price = (sell_price + (sell_price * loss_prevention_threshold))
                print "ETN will be sold for USDT if price reaches %s" %str(sell_price)

            if current_price >= sell_price:
                print "Initializing sale..."
                current_trade = trade('Sell', sell_price, active_balance)
                state = 2

        elif state == 2:
            time.sleep(3)
            current_price = get_etn_usdt_price()
            print "The current price is %s" % str(current_price)
            remaining, amount, rate = check_trade()
            print "You have sold %s of %s ETN at a rate of %s USDT." % (remaining, amount, rate)
            if current_price <= purchase_price:
                cancel_trade('Sell', current_trade)
                purchase_amount = amount - remaining
                current_trade = trade('Buy', purchase_price, purchase_amount)
                state = 3
            elif current_price >= loss_prevention_price :
                cancel_trade('Sell', current_trade)
                exit()
        elif state == 3:
            time.sleep(3)
            current_price = get_etn_usdt_price()
            print "The current price is %s" % str(current_price)
            remaining, amount, rate = check_trade()
            print "You have bought %s of %s ETN at a rate of %sUSDT" % (remaining, amount, rate)


main()
