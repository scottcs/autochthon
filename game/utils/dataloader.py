"""Data loader."""
import json
import logging
import pathlib
import typing

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

DEFAULT_PATH = pathlib.Path("data")
PATTERNS_TO_LOAD = ("*.json", "assemblage/**/*.json")


class DataLoader:
    """Loads data."""

    def __init__(self, data_path: typing.Optional[typing.Union[str, pathlib.Path]] = None) -> None:
        self.base_path = pathlib.Path(data_path or DEFAULT_PATH)
        self.data: dict = {}

    def load_all_json(self) -> None:
        """Load all JSON data files recursively into our data object."""
        for pattern in PATTERNS_TO_LOAD:
            for json_file in self.base_path.glob(pattern):
                key = ".".join(json_file.parent.parts[1:])
                self.data.setdefault(key, {})
                with json_file.open() as f:
                    try:
                        new_data = json.load(f)
                    except json.decoder.JSONDecodeError as exc:
                        raise json.decoder.JSONDecodeError(
                            f"{json_file}: {exc.msg}", exc.doc, exc.pos
                        )
                for new_key, new_value in new_data.items():
                    if new_key in self.data[key]:
                        log.error(
                            f"Template already defined for {new_key} (again in: {json_file})"
                        )
                    else:
                        self.data[key][new_key] = new_value
