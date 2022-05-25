from __future__ import annotations

from ..utils import embed_template

from typing import TYPE_CHECKING

from discord.ext.commands import Cog, command

if TYPE_CHECKING:
  from ..bot import AveBot

class Diagnostics(Cog):

  def __init__(self, bot: AveBot):
    self.bot = bot
    self.hidden = False

  @command(help='Get websocket latency', guild_ids=[914057960827781130])
  async def ping(self, ctx):
    embed = embed_template(self.bot, ctx.author, title='Pong! \U0001F3D3', description=f'{round(self.bot.latency*1000,1)}ms')
    await ctx.reply(embed=embed)
