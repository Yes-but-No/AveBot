from __future__ import annotations

from datetime import datetime

from math import floor

from discord.ext.commands import Bot
from discord.ext.tasks import loop

from discord import Status, Spotify, Game, Streaming, Activity, ActivityType

from .config import DEFAULT_CONFIG_DICT, ConfigManager
from .cogs import cogs
from .utils import handle_error

import typing

if typing.TYPE_CHECKING:
  from discord import Colour, Message, Member
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
    if self.prefix.isalpha():
      self.prefix += " "

    self.suppress = self.config["suppress"]

    self.mirror_id = int(self.config["mirror_id"])

    print("Setting up...")
    print("Prefix:", self.prefix)
    print("Suppress:", self.suppress)
    print("Mirroring:", self.mirror_id)

    self.mirror = None

    self.cmd_queue = []
    self.queue_cmds = False

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

  async def on_presence_update(self, _: Member, after: Member):
    if after.id == self.mirror_id:
      self.mirror = after
      await self.update_reflection()

  async def on_ready(self):
    print("Update success\n")
    await self.update_mirror() # Get initial mirror info
    self.run_queue.start()
    self.update_loop.start()

  async def update_mirror(self):
    """Forcefully update the mirror"""
    print("Forcefully updating mirror...")
    user = await self.get_or_fetch_user(self.mirror_id)
    mutual_guilds = user.mutual_guilds
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

  async def update_reflection(self):
    status = self.mirror.status
    print("\nUpdating", self.mirror)
    print("Status:", status)

    self.queue_cmds = status != Status.dnd

    if isinstance(status, str):
      # Not sure when the status will be a string, but just assume it's online
      status = Status.online
    elif status == Status.offline:
      status = Status.invisible

    activities = self.mirror.activities
    print("Activities:", activities)

    activity = None

    if activities:
      for act in activities:
        if act is None or act.type == ActivityType.custom:
          continue
        elif isinstance(act, Spotify):
          activity = Activity(
            type=ActivityType.listening,
            name=act.name,
            url=act.track_url
          )
        elif activity.type == ActivityType.playing:
          activity = Game(
            act.name,
            url=act.url
          )
        elif activity.type == ActivityType.streaming:
          activity = Streaming(
            name=act.name,
            url=act.url
          )
        else:
          activity = Activity(
            type=act.type,
            name=act.name,
            url=act.url
          )

    if activity is None and status != Status.invisible:
      activity = Activity(
        type=ActivityType.watching,
        name=self.mirror.name
      )

    print("Setting activity:", activity)
    print("Setting status:", status)

    await self.change_presence(activity=activity, status=status)
    print("Update success\n")

  @loop(seconds=0.1, reconnect=True)
  async def run_queue(self):
    await self.wait_until_ready()
    if self.cmd_queue and self.run_cmd:
      await self.invoke(self.cmd_queue.pop(0))

  @loop(seconds=30, reconnect=True)
  async def update_loop(self):
    await self.wait_until_ready()
    if self.mirror is not None:
      await self.update_reflection()

  def run(self, *args, **kwargs):

    self.start_time = datetime.now()
    super().run(self.token, *args, **kwargs)

  async def process_commands(self, message):
    if message.author.bot:
      return
    
    ctx = await self.get_context(message)
    if ctx.valid and self.queue_cmds:
      self.cmd_queue.append(ctx)

  async def on_message(self, message: Message):
    print(f"{message.author}: {message.content}")
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
    timediff = floor((datetime.now() - self.start_time).total_seconds())
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
