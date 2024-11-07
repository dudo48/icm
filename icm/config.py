from collections import ChainMap
from typing import Any

import tomllib

from icm import path

config: ChainMap[str, Any] = ChainMap()

if path.CONFIG_EXAMPLE.exists():
    with open(path.CONFIG_EXAMPLE, "rb") as file:
        config = config.new_child(tomllib.load(file))

if path.CONFIG.exists():
    with open(path.CONFIG, "rb") as file:
        config = config.new_child(tomllib.load(file))
