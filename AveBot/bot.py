from __future__ import annotations

from datetime import datetime

from discord.ext.commands import Bot, when_mentioned_or
from discord.ext.tasks import loop

from discord import Status

from .config import DEFAULT_CONFIG_DICT, ConfigManager
from .cogs import cogs
from .utils import handle_error

import typing

if typing.TYPE_CHECKING:
  from discord import Colour, Message, User
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
      help_command=None,
      case_insensitive=self.config['case_insensitive'],
      intents=self.config["intents"],
      *args,
      **kwargs
    )

    for cog in cogs:
      print(cog)
      self.add_cog(cog(self))
    
  @property
  def run_cmd(self):
    return self.mirror and self.mirror.status == Status.online

  async def update_mirror(self, user: User):
    mutual_guilds = user.mutual_guilds
    print("mutual guilds", mutual_guilds)
    # The mutual guild may not be loaded and results in no mutual guilds.
    # In this case, we must search manually
    if mutual_guilds:
      # Found one or more mutual guilds, so we just take the first one
      guild = mutual_guilds[0]
      self.mirror = guild.get_member(user.id) # Apparently we need to use get_member and not fetch_member so
    else:
      for guild in self.guilds:
        member = guild.get_member(user.id)
        if member: # ladies and gentlemen, we got 'em
          self.mirror = member
          break
      else:
        return # still can't find it, so we wait

    status = self.mirror.status
    print(self.mirror)
    print(status)

    if isinstance(status, str):
      # Not sure when the status will be a string, but just assume it's online
      status = Status.online
    elif status == Status.offline:
      status = Status.invisible

    activity = self.mirror.activity # Try to copy the activity, might not work
    print(activity)
    await self.change_presence(activity=activity, status=status)
    print("Update success")
    
    

  @loop(seconds=10, reconnect=True)
  async def update_loop(self):
    if self.is_ready():
      user = await self.get_or_fetch_user(self.mirror_id)
      await self.update_mirror(user)

  @loop(seconds=0.1, reconnect=True)
  async def run_queue(self):
    if self.is_ready():
      if self.cmd_queue and self.run_cmd:
        await self.invoke(self.cmd_queue.pop(0))

  def run(self, *args, **kwargs):

    @self.event
    async def on_ready():
      print("Bot ready")

      self.update_loop.start()
      self.run_queue.start()

    self.start_time = datetime.now()
    super().run(self.token, *args, **kwargs)

  async def process_commands(self, message):
    if message.author.bot:
      return
    
    ctx = await self.get_context(message)
    print(ctx)
    if ctx.valid:
      self.cmd_queue.append(ctx)

  async def on_message(self, message: Message):
    print(message.content)
    await self.process_commands(message)

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

  async def get_prefix(self, message=None):
    return [self.prefix, f"<@{self.user.id}> ", f"<@!{self.user.id}> "]

  @property
  def uptime(self) -> str:
    """Get the uptime of the bot"""
    timediff = datetime.now() - self.start_time
    hours, remainder = divmod(timediff, 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    fmt = f'{hours}h, {minutes}m and {seconds}s'
    return (f'{days}d, ' + fmt) if days else fmt

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