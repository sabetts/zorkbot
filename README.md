# Zork for IRC

A bot for playing Z Machine games over IRC.

# Usage

Specify the channel and nick:

    ZORKBOT_CHANNEL="#zorkbot" ZORKBOT_NICK="zorkbot" python3 zorkbot.py

Interact with the bot like this:

    *** zorkbot JOIN
    <sabetts> zorkbot: look
    <zorkbot> West of House You are standing in an open field
              west of a white house, with a boarded front
              door. There is a small mailbox here.

There are some special commands it accepts for navigating the library:

* `randrom` load a random rom from the library
* `rom <filename>` load a specific rom file
* `reset` reset the currently loaded rom
* `actions` list the possible valid actions

Everything else will be passed to the game.

# Background

Uses [Jericho](https://github.com/microsoft/jericho) to run the games. It's an AI Gym wrapper around the Z Machine and supports a bunch of games.

You need to download the game archive as documented in Jericho's quickstart guide:

https://jericho-py.readthedocs.io/en/latest/tutorial_quick.html



