# Autochthon

## NOTE:

The game code is currently broken!

I was using a modified esper.py which I accidentally deleted when
upgrading the python virtual environment.

Why I didn't make the changes in this git repo, I don't know. Big mistake.

To get this working again, I'll need to recreate the modifications I had
made to esper.World (and possibly other classes as well.), which I have
by now forgotten.

### Setup

If not already installed, install Python 3.7+, with pyenv:

```
pyenv install 3.7.4
```

Create a virtual environment with pyenv-virtualenv:

```
pyenv virtualenv 3.7.4 autochthon
```

Change into the autochthon project directory and set it as the local virtualenv:

```
cd autochthon
pyenv local autochthon 3.7.4
```

Install dependencies using poetry:

```
poetry install
```

Install git pre-commit hooks:

```
poetry run pre-commit install
```

## Running

Note: _Any of the below commands can be run in a poetry subshell using `poetry shell`, removing the need to preface each command with `poetry run`._

To run:

```
poetry run python start.py
```

## Development

### Versioning and Release

When creating a new branch, update to the next patch
or minor or major version but without updating git tags:

```
poetry run bumpversion --no-tag patch
```

After merging your branch into master. Bump the version for release:

```
poetry run bumpversion release
```

### Creating Tile Atlases

Run `tools.build_atlas` as in this example:

```
tile=Avatar_Equipment
poetry run python -m tools.build_atlas  static/img/oryx_ur/$tile.png static/img/oryx_ur/$tile.txt static/img/oryx_ur/$tile.json
```

### Building the tile index

Run `tools.make_tile_ids`:

```
poetry run python -m tools.make_tile_ids static/img/oryx_ur
```

### Running the Assemblage Editor

Run `tools.assemblage_edit`:

```
poetry run python -m tools.assemblage_edit
```

### Running the Map Visualizer

Run `tools.map_visualizer`:

```
poetry run python -m tools.map_visualizer
```

### Running mypy:

```
poetry run mypy
```
