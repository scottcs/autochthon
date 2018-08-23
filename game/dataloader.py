"""Data loader."""
import json
import logging
from pathlib import Path
from typing import Optional, Union

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

DEFAULT_PATH = Path('data')


class DataLoader:
    """Loads data."""
    def __init__(self, data_path: Optional[Union[str, Path]]=None) -> None:
        self.base_path = Path(data_path or DEFAULT_PATH)
        self.data = {}

    def load_all_json(self) -> None:
        """Load all JSON data files recursively into our data object."""
        for json_file in self.base_path.rglob('*.json'):
            key = '.'.join(json_file.parent.parts[1:])
            self.data.setdefault(key, {})
            with json_file.open() as f:
                try:
                    self.data[key].update(json.load(f))
                except json.decoder.JSONDecodeError as exc:
                    raise json.decoder.JSONDecodeError(f'{json_file}: {exc.msg}', exc.doc, exc.pos)
