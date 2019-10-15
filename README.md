# Autochthon

### Setup

If not already installed, install Python 3.8+, with pyenv:

```
pyenv install 3.8.0
```

Create a virtual environment with pyenv-virtualenv:

```
pyenv virtualenv 3.8.0 autochthon
```

Change into the autochthon project directory and set it as the local virtualenv:

```
cd autochthon
pyenv local autochthon 3.8.0
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
