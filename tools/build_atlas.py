"""Build a texture atlas from a given list of texture coordinates."""
import argparse
import json
import pathlib


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='create a texture atlas')
    parser.add_argument('image')
    parser.add_argument('names')
    parser.add_argument('output_json')
    return parser.parse_args()


def main(args: argparse.Namespace) -> None:
    """The main function."""
    output: dict = {}
    frames: dict = {}
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0
    rows: int = 0
    cols: int = 0
    num_anim_frames: int = 1

    with open(args.names) as f:
        for line in f.readlines():
            line = line.strip()

            if not line or line.startswith('#'):
                # blank line or comment
                continue

            if line.startswith('=='):
                # header
                w, h, rows, cols, num_anim_frames = [int(x) for x in line[2:].split()]
                continue

            for i in range(num_anim_frames):
                name = f'{line}_{i + 1}'
                frames[name] = {
                    'frame': {'x': x*w, 'y': (y+i)*h, 'w': w, 'h': h},
                    'rotated': False,
                    'trimmed': False,
                    'spriteSourceSize': {'x': 0, 'y': 0, 'w': w, 'h': h},
                    'sourceSize': {'w': w, 'h': h},
                }

            x += 1
            if x >= cols:
                x = 0
                y += num_anim_frames

    output['frames'] = frames

    output['meta'] = {
        'app': 'build_atlas.py',
        'version': '1.0',
        'image': pathlib.Path(args.image).name,
        'size': {'w': w*cols, 'h': h*rows},
        'scale': '1',
    }

    with open(args.output_json, 'w') as f:
        json.dump(output, f, indent=2)


if __name__ == '__main__':
    main(parse_args())
