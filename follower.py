import json
import logging
import logging.handlers

import twitter

from bittrex import Bittrex


def instantiate_apis(secrets_file_location):
    """
    Will instantiate all of the APIs for money

    :param secrets_file_location: location of API secrets JSON file
    :type secrets_file_location: str

    :return: Bittrex and Twitter APIs
    :rtype : twitter, Bittrex
    """
    try:
        with open(secrets_file_location) as secrets_file:
            secrets = json.load(secrets_file)
            secrets_file.close()
            twit = twitter.Api(
                consumer_key=secrets['twitter']['consumer_key'],
                consumer_secret=secrets['twitter']['consumer_secret'],
                access_token_key=secrets['twitter']['access_token_key'],
                access_token_secret=secrets['twitter']['access_token_secret']
            )
            bitt = Bittrex(
                secrets['bittrex']['key'],
                secrets['bittrex']['secret']
            )
            return twit, bitt
    except AttributeError as e:
        error_handler('Failed to locate API Secrets JSON file', e)
    except KeyError as e:
        error_handler('JSON API keys file contains errors', e)


def error_handler(error_str, e):
    """
    Deals with errors

    :param error_str: String of error
    :type error_str: str
    """
    print(error_str)
    logging.exception(e)


def fetch_timeline(twit):
    """
    Fetches Vicki's timeline (10 latest tweets)

    :param twit: Twitter API object
    :type twit: twitter

    :return: Latest tweets
    :rtype : dict
    """
    try:
        statuses = twit.GetUserTimeline(screen_name='Vickicryptobot')
        return statuses
    except twitter.error.TwitterError as e:
        error_handler("Error fetching user timeline", e)


def get_twiter_position(twit, market):
    """
    Get's Vicki's position on the appropriate stock

    :param twit: Twitter API Object
    :param market: The market pair which to observe
    :type twit: twitter
    :type market: str

    :return: String contining Vicki's position on the relavant market
    :rtype : str
    """
    statuses = fetch_timeline(twit)
    try:
        latest_tweet = ""
        for tweet in statuses:
            if market in tweet.text:
                latest_tweet = tweet.text
                break
        if 'long' in latest_tweet:
            return 'long'
        elif 'short' in latest_tweet:
            return 'short'
    #Generic exceptor used to catch all posible error types when itterating through tweets
    except Exception as e:
        error_handler('Error itterating through tweets in statuses', e)


def get_bittrex_position(bitt, market):
    """
    Get's current position on market from Bittrex
    Be aware: this is not neccicarily a good idea as it wil trade any pre-exising funds 
        in your Bittrex accounts.

    :param bitt: The bittrex API object
    :param market: The market pair which to observe
    :type bitt: Bittrex
    :type market: str

    :return: String contining Bittrex's position on the relavant market
    :rtype : str
    """
    try:
        pair = market.split('-')
        market_currency = pair[1]
        base_currency = pair[0]
        market_currency_balance = bitt.get_balance(
            market_currency)['result']['Available']
        base_currency_balance = bitt.get_balance(
            base_currency)['result']['Available']
        if market_currency_balance > base_currency_balance:
            return 'long'
        else:
            return 'short'
    except Exception as e:
        error_handler(
            'Failed to connect to bittrex and/ or pull balance data', e)


def should_a_trade_occur(twit, bitt, twit_market, bitt_market):
    """
    Boolean variable to determine whether or not to trade. 
    :param twit: The twitter API object
    :type twit: twitter
    :param bitt: The Bittrex API object
    :type bitt: Bittrex
    :param twit_market: The market pair to look for in the tweets
    :type twit_market: str
    :param bitt_market: The market pair to look the balances up of
    :type bitt_market: str
    """
    twit_posiiton = get_twiter_position(twit, twit_market)
    bitt_position = get_bittrex_position(bitt, bitt_market)
    has_new_trade_occured = not twit_posiiton == bitt_position
    return has_new_trade_occured, twit_posiiton


def get_buy_price(bitt, market, base_currency_balance):
    """
    Get the current price for the sell order capible of filling this buy order
    This is an exceptionally shitty way of doing this, but it works for low volume
    :param bitt: The Bittrex API object
    :type bitt: Bittrex
    :param market: The market pair being traded
    :type market: str
    :param base_currency_balance: Amount of base currency held (used to find big enough buy order)
    """
    try:
        order_book = bittrex.get_orderbook(market, 'sell', depth=20)["result"]
        price = 0.01
        for order in order_book:
            order_book_vol = order['Quantity'] * order['Rate']
            if order_book_vol > base_currency_balance:
                price = order['Rate']
                break
    except Exception as e:
        error_handler('Failed to get current orderbook', e)
    return price


def execute_trade(bitt, market, direction):
    """
    Finally the code that actually excecutes the trade via the API.
    :param bitt: The Bittrex API object
    :type bitt: Bittrex
    :param market: The market pair being traded
    :type market: str
    :param direction: whether to go long or short on coin
    :type direction: str
    """
    try:
        pair = market.split('-')
        base_currency = pair[0]
        base_currency_balance = bitt.get_balance(
            base_currency)['result']['Available']
        if direction.lower() == 'short':
            bitt.buy_market(market, base_currency_balance)
        elif direction.lower() == 'long':
            price = get_buy_price(bitt, market, base_currency_balance)
            amount_of_coin_to_buy = base_currency_balance / price
            bitt.sell_market(market, amount_of_coin_to_buy)
        else:
            raise ValueError
    except Exception as e:
        error_handler('An error occured placing the current trade', e)


def configure_email_error_logging(secrets_file_location):
    """
    Sets up logging via email.
    :param secrets_file_location: the location of the email secrets json file
    :type secrets_file_location
    """
    with open(secrets_file_location) as secrets_file:
        secrets = json.load(secrets_file)
        secrets_file.close()
    logger = logging.getLogger()
    logger.addHandler(logging.handlers.SMTPHandler(
        mailhost=(secrets["mail_host"], secrets["port"]),
        fromaddr=secrets["from_addrs"],
        toaddrs=secrets["to_addrs"],
        subject=secrets["subject"],
        credentials=(secrets["smtp_user"], secrets["secret"]),
        secure=()))


if __name__ == '__main__':
    TWITTERMARKETPAIR = "ETHUSD"
    BITTREXMARKETPAIR = "USDT-ETH"
    EMAILSECTRETSFILE = "email_secret.json"
    APISECTRETSFILE = "api_keys.json"
    configure_email_error_logging(EMAILSECTRETSFILE)
    twit, bitt = instantiate_apis(APISECTRETSFILE)
    a_new_trade_should_occur, direction = should_a_trade_occur(
        twit,
        bitt,
        TWITTERMARKETPAIR,
        BITTREXMARKETPAIR)
    if a_new_trade_should_occur:
        execute_trade(bitt, BITTREXMARKETPAIR, direction)
