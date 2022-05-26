from __future__ import annotations

import os
import typing
from json import loads

from discord import Colour, Intents

def get_setup_from_json(filename: str) -> SetupConfigDict:
  """
  Gets all setup parameters for the bot from a json file.
  """
  path = os.path.join(
    os.getcwd(), filename
  )
  with open(path, 'r') as f:
    setup_config: SetupConfigDict = loads(f.read())
  return setup_config


class ConfigDict(typing.TypedDict):
  intents: Intents
  default_colour: typing.Callable[[], Colour]
  error_colour: typing.Callable[[], Colour]
  error_msg: typing.Dict[str, typing.List[str]]

class SetupConfigDict(typing.TypedDict):
  """Configurations needed to specified to run the bot"""
  prefix: str
  token: str
  mirror_id: str
  suppress: bool
  case_insensitive: bool
  enable_eval: bool

DEFAULT_CONFIG_DICT: ConfigDict = {
  "intents": Intents.all(),
  "activity_message": "Yes but No",
  "default_colour": Colour.random,
  "error_colour": Colour.brand_red,
  "error_msg": {
    "default": [
      "Error!",
      "D'Oh",
      "Oops?",
      "Uh oh...",
      "What did you do...",
      "Reebe!",
      "01000101 01110010 01110010 01101111 01110010 00100001",
      "RXJyb3Ih",
      "VWggb2guLi4=",
      "Better luck next time",
      "why",
      "Noooooooo",
      "Have you tried turning it off and on again?",
      "Pls no"
    ],
    "not_found": [
      "What even is that?!",
      "UNKNOWN COMMAND",
      "Maybe it works on Alexa...",
      "Maybe try suggesting it?",
      "Nice typing",
      "Idk tho",
      "This ain't Google btw"
    ],
    "bad_perms": [
      "Nice try",
      "Haha NOO!",
      "Sike you thought",
      "Worth a try I guess",
      "E for Effort",
      "Cry about it",
      "NO U"
    ]
  }
}

class ConfigManager:

  def __init__(self, setup_config: SetupConfigDict, config_dict: ConfigDict):
    self.setup_config = setup_config
    self.config_dict = config_dict
    self._configs: typing.Union[SetupConfigDict, ConfigDict] = {**setup_config, **config_dict}

  @property
  def values(self):
    return self._configs

  @property
  def items(self):
    return self._configs.items()

  @property
  def keys(self):
    return self._configs.keys()

  def get(self, item, default=None):
    try:
      return self._configs[item]
    except KeyError:
      return default

  def __getitem__(self, item: str):
    return self.get(item)

  def __setitem__(self, item: str, value: typing.Any):
    self._configs[item] = value

  def __str__(self):
    return str(self._configs)