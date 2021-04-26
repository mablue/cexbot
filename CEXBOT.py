# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import os
import sys
import ccxt
import time
import subprocess

root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')


############################################################
exps = 0
############################################################
botEnabled = False


def runBot():

    exchange = ccxt.binance({
        'apiKey': 'YOUR EXCHANGE API KEY',
        'secret': 'YOUR EXCHANGE API AECRET',
        'enableRateLimit': True,
    })

    assets = {}
    exp = -10
    trades = ['doge/btc', 'bnb/usdt', 'cfx/usdt']
    TRADES = [x.upper() for x in trades]

    if exchange.has['fetchMyTrades']:
        for trade in TRADES:
            t = exchange.fetch_my_trades(symbol=trade)
            base, pair = trade.split('/')
            assets[base] = {
                pair: None,
                'exp': exp,
                'enable': True,
                'tf': '1h',
            }
            assets[base][pair] = float(t[-1]['info']['price'])
            # print(assets)

    markets = exchange.load_markets()
    marketslst = sorted(list(markets))

    # gereftane gimate feli
    maxValuer = 'bid'
    minValuer = "ask"

    def getValue(base, quote):
        #time.sleep (exchange.rateLimit / 1000)
        pair = f"{base}/{quote}"

        if pair in list(markets):
            ft = exchange.fetch_ticker(pair)
            val = (ft[maxValuer]+ft[minValuer])/2
            return val
        else:
            pair = f"{quote}/{base}"
            ft = exchange.fetch_ticker(pair)
            val = (ft[maxValuer]+ft[minValuer])/2
            if val == 0:
                val = 0.0000000001
            return 1/val

    # get my orders
    """allMyTrades=[]
    myTrades = exchange.fetch_my_trades(symbol='XLM/USDT')
    allMyTrades.extend(myTrades) 
    for trade in allMyTrades:
        print(trade)
    """

    ppsum = 0
    count = 0
    ppold = None

    # try:
    # print(f"\n{'Asset':<10} {'Profit':>6} % | " +
    #       f"{'Buy':>16} {'Unit':<5} | " +
    #       f"{maxValuer+' '+minValuer:>16} {'Unit':<5} | " +
    #       f"{'Real':>16} {'Unit':<5}")
    telmsg = ""
    while(True):
        for pair in marketslst:

            base = markets[pair]['base']
            quote = markets[pair]['quote']
            # print(base,assets)
            if base in assets:
                #print('im inside')
                # and quote in assets[base]:

                # firstBase=base
                firstQuote = list(assets[base])[0]
                # populateQuotes(firstBase,firstQuote,markets)

                buy = None
                marketPrice = None  # market price in usdt
                realPrice = getValue(base, quote)
                if quote == firstQuote:
                    buy = assets[base][quote]
                    marketPrice = realPrice
                else:
                    quoteOnFirstQuote = getValue(quote, firstQuote)
                    # print('pair,base,quote,firstQuote,quoteOnFirstQuote')
                    # print(pair,base,quote,firstQuote,quoteOnFirstQuote)
                    buy = assets[base][firstQuote]  # *quoteOnFirstQuote
                    marketPrice = getValue(base, quote)*quoteOnFirstQuote

                exp = assets[base]['exp']

                # marketPrice=round(marketPrice,10)
                # buy=round(buy,10)

                profitPercent = marketPrice/buy*100-100
                out = \
                    f"{pair:<10} {profitPercent:>6.2f}%\n" +\
                    f"Buy(first unit): {buy:>16.10f}{firstQuote}\n" +\
                    f"Sell(new unit): {realPrice:>16.10f}{quote}\n" +\
                    f"Sell(first unit): {marketPrice:>16.10f}{firstQuote}"

                if profitPercent >= exp and assets[base]['enable'] != False:

                    sendTelMsg(out)

    time.sleep(5)


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')
    botEnabled = True
    runBot()


def stop(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Buy!')
    botEnabled = False


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    # update.message.reply_text(update.message.text)

    # try:
    # exps = int(update.message.text)
    # print(exps)
    # update.message.reply_text("expected profit setted to: ", exps)
    # except:
    # update.message.reply_text("Please enter a number")


def sendMessage(update, context):
    update.message.replay_text("hi")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


"""Start the bot."""
# Create the Updater and pass it your bot's token.
# Make sure to set use_context=True to use the new context based callbacks
# Post version 12 this will no longer be necessary
updater = Updater(
    "YOUR TELEGRAM API BOT TOKEN", use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher


def sendTelMsg(txt):
    updater.dispatcher.bot.sendMessage(chat_id='YOUR CHAT ID', text=txt)


# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("stop", stop))
dp.add_handler(CommandHandler("help", help))

# on noncommand i.e message - echo the message on Telegram
dp.add_handler(MessageHandler(Filters.text, echo))

# log all errors
dp.add_error_handler(error)

# Start the Bot
updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()

