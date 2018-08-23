# Autochthon

### Setup

Create a virtual environment using Python 3.7+, and run:

```
pip install -r requirements.txt
```

## Running

To run as a web server using the host and port defined in `data/config.json`:

```
python start.py
```


To run in a local window:

`python start.py --local`

## Development

### Versioning and Release

When creating a new branch, update to the next patch
or minor or major version but without updating git tags:

```
bumpversion --no-tag patch
```

After merging your branch into master. Bump the version for release:

```
bumpversion release
```

### Creating Tile Atlases

Run `tools.build_atlas` as in this example:

```
tile=Avatar_Equipment
python -m tools.build_atlas  static/img/oryx_ur/$tile.png static/img/oryx_ur/$tile.txt static/img/oryx_ur/$tile.json
```

### Building the tile index

Run `tools.make_tile_ids`:

```
python -m tools.make_tile_ids static/img/oryx_ur
```

### Copying mypy typeshed files to your virtualenv:

```
cp -rf typeshed/* ~/.venv/autochthon/lib/mypy/typeshed/third_party/3
```

### Running mypy:

```
mypy --strict -p game
```
