"""Parse all tile atlases and make master tile ids file."""
import argparse
import json
import pathlib
from typing import List, Dict


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='build master tile ids file')
    parser.add_argument('directory')
    return parser.parse_args()


def get_atlas_info(atlas_file: pathlib.Path) -> List[Dict]:
    """Parse a tile atlas."""
    tileset: str = atlas_file.with_suffix('.json').as_posix()
    atlas_data: list = []
    num_anim_frames: int = 1

    with atlas_file.open() as f:
        for line in f.readlines():
            line = line.strip()

            if not line or line.startswith('#'):
                # blank line or comment
                continue

            if line.startswith('=='):
                # header
                num_anim_frames = int(line.split()[-1])
                continue

            tiles: list = []
            for i in range(num_anim_frames):
                name: str = f'{line}_{i + 1}'
                tiles.append(name)

            atlas_data.append({
                'tileset': tileset,
                'tiles': tiles,
            })

    return atlas_data


def main(args: argparse.Namespace) -> None:
    """The main function."""
    directory = pathlib.Path(args.directory)
    tile_ids = []
    for atlas_file in directory.glob('*.txt'):
        tile_ids.extend(get_atlas_info(atlas_file))
    master_tile_ids = {i: data for i, data in enumerate(tile_ids, start=1)}
    with open(directory / pathlib.Path('tile_ids.json'), 'w') as f:
        json.dump(master_tile_ids, f, indent=2)


if __name__ == '__main__':
    main(parse_args())
