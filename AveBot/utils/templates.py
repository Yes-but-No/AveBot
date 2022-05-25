from __future__ import annotations

from datetime import datetime
from random import choice
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
  from ..bot import AveBot

def embed_template(bot: AveBot, author: discord.User=None, **options) -> discord.Embed:
  colour = options.pop('colour', None) or bot.default_embed_colour()
  timestamp = options.pop('timestamp', None) or datetime.now()
  embed = discord.Embed(colour=colour, timestamp=timestamp, **options)
  if author is not None:
    embed.set_footer(text=f'Requested by {author!s}', icon_url=author.display_avatar.url)
  embed.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
  return embed

error_msg = None

def error_template(bot: AveBot, author: discord.User=None, err_type=None, **options) -> discord.Embed:
  global error_msg
  colour = options.pop('colour', None) or bot.error_embed_colour()
  title = options.pop('title', None)
  timestamp = options.pop('timestamp', None) or datetime.now()
  if not title:
    if not error_msg:
      error_msg = bot.error_msg
    if err_type:
      title = choice(error_msg.get(err_type, [])+error_msg['default'])
    else:
      title = choice(error_msg['default'])
  embed = discord.Embed(title=title, colour=colour, timestamp=timestamp, **options)
  if author is not None:
    embed.set_footer(text=f'Requested by {author!s}', icon_url=author.display_avatar.url)
  embed.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
  return embed