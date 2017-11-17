# Vicki Follower
This is a trading bot that follows Vick's movements on ETH/USD.

## Trading platform
This bot trades on BITTREX with the USDT/ETH pair. This is for two reasons, the BITTREX API is very easy to interface with and USDT probably has better tax implications that USD.

## Dependancies
* Twitter

## Secrets files
There are two secrets files required by this bot, one is for the BITTREX and Twitter APIs and the other is for E-Mail settings for error logging/waring purposes.

### Formatting:
api_keys.json:
``` json
{
    "bittrex":{
        "key": "",
        "secret": ""
    },
    "twitter":{
        "consumer_key": "",
        "consumer_secret": "",
        "access_token_key": "",
        "access_token_secret": ""
    }
    
}
```

email_secret.json:
``` json
{
    "mail_host": "smtp.google.com",
    "port": 465,
    "from_addrs":"",
    "to_addrs": "",
    "subject": "Vicki Follower Bot Error!",
    "smtp_user": "",
    "secret": ""
}
```

## Working State
I coded this a while ago (before Vicki switched over to having separate accounts for each pair). This means, that this code will no longer work. That said, the core ideas are still good, they must just be ported over to her new accounts and phrasology so is broken.
