# BananaOniBot
This repository hosts the source code for [BananaOniBot](https://reddit.com/user/BananaOniBot), a reddit bot designed to share banana facts.
The code has been documented to help readers understand some of its behavior, but knowledge of Python, PRAW, and the reddit API might be useful as well.
This bot was mostly written in a 4-6 hour drunken spree some years ago as a limited replacement for a similar, long-dead bot, and the code quality isn't great. I've had no desire to fix the horrific quality and glaring bugs in the time since, and certainly have no plans to do so now, given reddit's upcoming API changes. However, anyone is free to learn from, adapt, or copy this code as they see fit.

##Setting up the bot
- If you plan on using a reddit account other than your primary account to run your bot, create that account and verify the email address.
- [Follow these steps](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps) to get a client id and client secret, while logged into the account that the bot will run on.
- Place all relevant info in the bottom section of praw.ini; if you wish to change the default site name of [bob] in the ini, make sure you also update the name in bot.py
- **NEVER** share your bot's password or client secret - this includes sharing the praw.ini file you've just populated.
- Ideally, you would also want to actually edit the bot's code in bot.py before running it - otherwise it's just going to copy BananaOniBot's functionality.

##Starting the bot
- [Follow the instructions for setting up PRAW](https://praw.readthedocs.io/en/stable/getting_started/installation.html).
- Start the bot from the command line with `python3 bot.py`. The bot will continue to run until the command window is closed - to run it indefinitely, look into programs such as `screen`, or set up a service to run the bot.
