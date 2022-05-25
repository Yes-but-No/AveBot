from __future__ import annotations

import sys
import traceback
from typing import TYPE_CHECKING

from discord.errors import Forbidden
from discord.ext import commands

from .templates import error_template

if TYPE_CHECKING:
  from ..bot import AveBot

async def handle_error(bot: AveBot, ctx: commands.Context, error: commands.errors.CommandError):
  command = ctx.command
  if command and command.has_error_handler():
    return

  cog = ctx.cog
  if cog and cog.has_error_handler():
    return

  # TODO: Rework this, there might be a better way
  if isinstance(error, commands.errors.CommandNotFound):
    embed = error_template(bot, ctx.author, err_type='NotFound')
    msg = '**cOmMaNd DoEsN\'t ExIsT**'
  elif isinstance(error, commands.MissingPermissions):
    embed = error_template(bot, ctx.author, err_type='BadPerms')
    msg = '```Your permissions are far inferior for this command```'
  elif isinstance(error, commands.errors.NotOwner):
    embed = error_template(bot, ctx.author, err_type='BadPerms')
    msg = '```Only the owner of the bot can run this command```'
  elif isinstance(error, commands.errors.NoPrivateMessage):
    embed = error_template(bot, ctx.author)
    msg = '```This command can only be run in Servers!```' 
  else:
    if bot.suppress:
      print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
      traceback.print_exception(type(error), error, error.__traceback__, file=sys.sydout)
      return
    else:
      embed = error_template(bot, ctx.author)
      trace_string = '\n'.join(traceback.format_exception(type(error), error, error.__traceback__))
      msg = f'```\n{trace_string}```'

  embed.description = msg
  try:
    await ctx.reply(embed=embed)
  except Forbidden:
    pass