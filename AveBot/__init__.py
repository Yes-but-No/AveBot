__title__ = "AveBot"
__author__ = "YBN Development Team"
__version__ = "1.0.0a1"

from .bot import AveBot
from .config import get_setup_from_env, get_setup_from_json

from typing import NamedTuple, Literal

class VersionInfo(NamedTuple):
  major: int
  minor: int
  micro: int
  releaselevel: Literal["alpha", "beta", "candidate", "final"]
  serial: int

version_info: VersionInfo = VersionInfo(major=1, minor=0, micro=0, releaselevel="alpha", serial=1)
