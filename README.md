# Autochthon

### Setup

Create a virtual environment using Python 3.7+, and `pip install -r requirements.txt`.

## Running

To run as a web server using the host and port defined in `static/config.json`:

`python start`


To run in a local window:

`python start --local`

## Development

### Creating Tile Atlases

Run tools.build_atlas as in this example:

`python -m tools.build_atlas  static/img/oryx_ur/Monsters.png static/img/oryx_ur/Monsters.txt static/img/oryx_ur/Monsters.json`
