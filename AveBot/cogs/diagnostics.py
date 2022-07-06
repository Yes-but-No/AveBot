from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from discord.ext.commands import Cog, command, Context

from ..utils import embed_template

if TYPE_CHECKING:
  from ..bot import AveBot

class Diagnostics(Cog):

  def __init__(self, bot: AveBot):
    self.bot = bot
    self.hidden = False

  @command(help='Get websocket latency')
  async def ping(self, ctx: Context):
    time = datetime.now(tz=timezone.utc) - ctx.message.created_at
    time = (time.microseconds/1000 + self.bot.latency*1000)
    embed = embed_template(self.bot, ctx.author, title='Pong! \U0001F3D3', description=f'{round(time,1)}ms')
    await ctx.reply(embed=embed)

  @command(help="Get the uptime of the bot")
  async def uptime(self, ctx: Context):
    uptime = self.bot.uptime
    embed = embed_template(self.bot, ctx.author, title="Bot uptime", description=uptime)