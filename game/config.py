from pathlib import Path
from typing import Any

import toml

class Config:
    def __init__(self, cfg_file: str) -> None:
        self.cfg_file = cfg_file
        self._full_path = Path(__file__).parent.parent / cfg_file
        self._file_obj = open(self._full_path, mode='r+')
        self._config = toml.load(self._file_obj)

    def __getitem__(self, key: str):
        fullkey = key.split('.')
        curr_layer = self._config[fullkey.pop(0)]
        for k in fullkey:
            curr_layer = curr_layer[k]
        return curr_layer

    def __setitem__(self, key: str, value: Any):
        fullkey = key.split('.')
        curr_layer = self._config[fullkey.pop(0)]
        for k in fullkey[:-1]:
            curr_layer = curr_layer[k]
        curr_layer[fullkey[-1]] = value
        toml.dump(self._config, self._file_obj)

    def full(self):
        return self._config.copy()

class GameOptions(Config):
    pass
