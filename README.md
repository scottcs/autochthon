# Autochthon

### Setup

Create a virtual environment using Python 3.7+, and `pip install -r requirements.txt`.

## Running

To run as a web server:

`python start`

which uses the default port (19999), or to specify a port:

`python start --port 1234`

To run in a local tdl window:

`python start --local`

## Development

### Creating Tile Atlases

Run tools.build_atlas as in this example:

`python -m tools.build_atlas  static/img/oryx_ur/Monsters.png static/img/oryx_ur/Monsters.txt static/img/oryx_ur/Monsters.json`
