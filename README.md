# autochthon

A traditional roguelike engine written in Python, built around a hand-rolled
entity-component-system. This is an unfinished hobby project I worked on between
2019 and 2022, shared as a code sample rather than a finished product.

## What it is

The engine renders with BearLibTerminal and uses libtcod (`tcod`) for
field-of-view and grid math. It covers map generation, field-of-view, a turn
loop, combat with modifiers, simple AI, inventory and containers, a scrolling
message log, and loading of RexPaint `.xp` maps. Two small PySide2 desktop tools
sit alongside it: an entity ("assemblage") editor and a map visualizer.

The parts worth reading first:

- `game/ecs.py`: the entity-component-system core. A typed `World` with cached
  component queries and priority-scheduled processors. It began from `esper` and
  was rewritten to fit strict typing.
- `game/utils/random.py`: a seeded PCG32 generator and a small expression parser
  for dice and weighted tables, such as `2d6+1`, `weighted((...), (...))`, and
  `step(min, max, step)`.
- `game/map.py`: numpy-backed grid handling on top of `tcod`.

## Typing and tooling

The codebase is fully type-annotated and checks under a strict mypy
configuration (see `setup.cfg`): `disallow_untyped_defs`,
`disallow_any_generics`, `no_implicit_optional`, and more. Formatting and linting
run through pre-commit with isort, black, flake8 (with docstring and bugbear
plugins), and mypy.

## Tests and CI

`test/test_random.py` covers the seeded RNG and the expression parser: stream
determinism against a pinned sequence, the inclusive-range and error behavior of
`GameRNG.rand`, and the dice, weighted, and step parsers including their constant
and out-of-grammar cases.

GitHub Actions runs those tests plus the strict type, format, and lint checks.
The CI checks are scoped to the standard-library `random.py` module and the test
suite, because the rest of the engine imports `tcod`, `bearlibterminal`, and
`PySide2` at versions that predate current Python and are not installed in CI.
To run just those checks locally:

```
pytest test/
mypy game/utils/random.py test/
flake8 test/
black --check -l 99 test/
isort --check test/
```

The full development setup below installs every dependency, which also lets you
run `poetry run mypy` across the whole codebase.

## Setup

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

The sprite art is a commercial Oryx Design Lab tileset that I am not licensed to
redistribute, so it is not in this repository. The game loads it from
`data/tiles/oryx_td/`, and you would need to supply your own copy there for the
world to render. The bundled FiraMono font (SIL OFL) and the tileset metadata are
included.

Note: _Any of the below commands can be run in a poetry subshell using `poetry shell`, removing the need to preface each command with `poetry run`._

To run:

```
poetry run python start.py
```

<!-- TODO: add a screenshot or short GIF of the game running -->

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

### Running mypy

```
poetry run mypy
```

## Credits

- The PCG32 implementation in `game/utils/random.py` is adapted from the
  clubsandwich library (MIT).
- The ECS in `game/ecs.py` began from
  [esper](https://github.com/benmoran56/esper) (MIT) and was rewritten.
- `data/font/FiraMono-Regular.ttf` is licensed under the SIL Open Font License
  1.1.

## License

MIT, see [LICENSE](LICENSE). The license covers my code. Bundled third-party
assets and dependencies keep their own licenses.
