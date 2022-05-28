__title__ = "AveBot"
__author__ = "YBN Development Team"
__version__ = "0.0.1a1"

from .bot import AveBot
from .config import get_setup_from_env, get_setup_from_json

from typing import NamedTuple, Literal

class VersionInfo(NamedTuple):
  major: int
  minor: int
  micro: int
  releaselevel: Literal["alpha", "beta", "candidate", "final"]
  serial: int

version_info: VersionInfo = VersionInfo(major=0, minor=0, micro=1, releaselevel="alpha", serial=1)