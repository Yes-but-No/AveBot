from __future__ import annotations

from datetime import datetime

from discord.ext.commands import Bot, when_mentioned_or
from discord.ext.tasks import loop

from .config import DEFAULT_CONFIG_DICT, ConfigManager
from .cogs import cogs
from .utils import handle_error

import typing

if typing.TYPE_CHECKING:
  from discord import Colour, Message
  from discord.ext.commands import Context, errors
  from .config import SetupConfigDict

class AveBot(Bot):
  """
  Represents a bot connecting to the Discord API
  """

  def __init__(self, setup_config: SetupConfigDict, *args, **kwargs):
    config_dict = kwargs.pop('config', DEFAULT_CONFIG_DICT)
    self.config = ConfigManager(setup_config=setup_config, config_dict=config_dict)
    self.token = self.config["token"]
    self.prefix = self.config["prefix"]
    self.suppress = self.config["suppress"]

    self.mirror_id = self.config["mirror_id"]

    self.mirror = None

    self.cmd_queue = []

    super().__init__(
      command_prefix=when_mentioned_or(self.prefix),
      help_command=None,
      case_insensitive=self.config['case_insensitive'],
      *args,
      **kwargs
    )

    for cog in cogs:
      print(cog)
      self.add_cog(cog(self))



  def run(self, *args, **kwargs):

    @self.event
    async def on_ready():

      print("Bot ready")

      @loop(minutes=5, reconnect=True)
      async def update_user():
        if self.is_ready():
          self.mirror = await self.get_or_fetch_user(self.mirror_id)
          print("Updated!")

      update_user.start()

    self.start_time = datetime.now()
    super().run(self.token, *args, **kwargs)

  async def on_message(self, message: Message):
    print(message.content)
    await super().on_message(message)

  async def on_command_error(self, ctx: Context, error: errors.CommandError):
    """|coro|

    The default command error handler provided by the bot
    """
    if self.extra_events.get('on_command_error', None):
      return

    command = ctx.command
    if command and command.has_error_handler():
      return

    cog = ctx.cog
    if cog and cog.has_error_handler():
      return

    await handle_error(self, ctx, error)

  @property
  def uptime(self) -> str:
    """Get the uptime of the bot"""
    timediff = datetime.now() - self.start_time
    hours, remainder = divmod(timediff, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    fmt = f'{hours}h, {minutes}m and {seconds}s'
    return (f'{days}d, ' + fmt) if days else fmt

  async def get_prefix(self, message=None):
    return [self.prefix, f"<@{self.user.id}> ", f"<@!{self.user.id}> "]

  @property
  def enable_eval(self) -> bool:
    """Whether the bot will run code"""
    return self.config['enable_eval']

  @property
  def default_embed_colour(self) -> typing.Callable[[], Colour]:
    """The default colour for the bot's embeds"""
    return self.config['default_colour']

  @property
  def error_embed_colour(self) -> typing.Callable[[], Colour]:
    """The default colour for the bot's error embeds"""
    return self.config['error_colour']

  @property
  def error_msg(self) -> typing.Dict[str, list]:
    """The random error messages for the bot"""
    return self.config['error_msg']