# AveBot

Is this a self bot? Well yes, but no

## What does this bot do?

This bot is able to "mirror" a user that is specified.

This "mirrored" user can copy the target's activities and only runs commands when the user is online

Even when the user is offline and idle, it will queue commands and run them when the user comes back online

If the user is set to "do not disturb", no commands are added to the queue

This bot was made to test the YBN bot framework

## Setup

To setup the bot, you first need to create a `json` file as follows:

```json
{
  "prefix": "<prefix here>",
  "token": "<bot token>",
  "mirror_id": "<user id of user to copy>",
  "suppress": "<set to true to turn on error supression>",
  "case_insensitive": "<set to true to make commands case insensitive>",
  "enable_eval": "<currently does not do anything>"
}
```

To run the bot, use code that looks something like this:

```py
from AveBot.AveBot import AveBot, get_setup_from_json

setup = get_setup_from_json("setup.json")

bot = AveBot(setup)

bot.run()
```

