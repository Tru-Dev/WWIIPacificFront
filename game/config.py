from pathlib import Path
from typing import Any, ClassVar, Dict, Optional

import toml

class Config:
    # Meant to be overridden by subclasses
    default_config: ClassVar[Optional[Dict[str, Any]]] = None
    default_filename: ClassVar[Optional[str]] = None

    def __init__(self, cfg_file: Optional[str] = None) -> None:
        self.cfg_file = cfg_file if cfg_file is not None else None
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
        self._file_obj.seek(0)
        self._file_obj.truncate()
        toml.dump(self._config, self._file_obj)

    def full(self):
        return self._config.copy()

class GameOptions(Config):
    default_config = {
        'music_sounds': {
            'music_volume': 100,
            'sound_volume': 100,
            'track': 1
        },
        'game': {
            'shot_style': 3,
            'name': ''
        }
    }
    default_filename = 'options.toml'
    
    def __init__(self, cfg_file: str='options.toml') -> None:
        super().__init__(cfg_file)
