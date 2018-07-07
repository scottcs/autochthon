(function () {
    window.onload = function() {
        const img_dir = 'static/img/';
        const tileset_dir = img_dir + 'oryx_ur/';
        const tileset_avatar = tileset_dir + 'Avatar.png';
        const tileset_avatar_equipment = tileset_dir + 'Avatar_Equipment.png';
        const tileset_items = tileset_dir + 'Items.png';
        const tileset_monsters = tileset_dir + 'Monsters.json';
        const tileset_monsters_scifi = tileset_dir + 'Monsters_Scifi.png';
        const tileset_terrain = tileset_dir + 'Terrain.png';
        const tileset_terrain_objects = tileset_dir + 'Terrain_Objects.png';

        // TODO: get rid of these
        const tile_width = 16;
        const tile_height = 24;
        const map_tile_width = 70;
        const map_tile_height = 26;

        let view_map = new Array(map_tile_width);
        for (let i = 0; i < map_tile_width; i++) {
            view_map[i] = new Array(map_tile_height)
        }

        // noinspection JSValidateTypes
        PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

        let app = new PIXI.Application({
            width: tile_width * map_tile_width,
            height: tile_height * map_tile_height
        });

        document.body.appendChild(app.view);

        // noinspection JSUnresolvedFunction
        PIXI.loader
            .add([
                tileset_avatar,
                tileset_avatar_equipment,
                tileset_items,
                tileset_monsters,
                tileset_monsters_scifi,
                tileset_terrain,
                tileset_terrain_objects
            ])
            .on("progress", loadProgressHandler)
            .load(setup);

        function loadProgressHandler(loader, resource) {
            console.log("loading: " + resource.url);
            console.log("progress: " + loader.progress + "%");
        }

        function setup() {
            console.log('Done loading.')
        }

        function updateView(message) {
            // noinspection JSUnresolvedVariable
            for (const cell of message.deltas) {
                updateMap(cell);
            }
        }

        function updateMap(cell) {
            const old_sprite = view_map[cell.prev_x][cell.prev_y];
            if (old_sprite !== null) {
                app.stage.removeChild(old_sprite);
                view_map[cell.prev_x][cell.prev_y] = null;
            }

            if (cell.tileset !== null) {
                // noinspection JSUnresolvedVariable
                const new_tex = PIXI.loader.resources[cell.tileset].textures[cell.tile];
                const sprite = new PIXI.Sprite(new_tex);
                sprite.x = tile_width * cell.x;
                sprite.y = tile_height * cell.y;
                view_map[cell.x][cell.y] = sprite;
                app.stage.addChild(sprite);
            }
        }

        let keys_down = [];
        const ws = new WebSocket("ws://localhost:19999/websocket");

        document.addEventListener("keydown", function(event) {
            if (event.defaultPrevented) {
                return;
            }
            if (event.key !== 'Meta' && event.key !== 'Alt') {
                keys_down.push(event.key);
            }
            if (!keys_down.includes('Control')) {
                sendKeys()
            }
        });

        document.addEventListener("keyup", sendKeys);

        function sendKeys() {
            if (keys_down.length > 0) {
                const payload = {
                    "keys": Array.from(new Set(keys_down))
                };
                ws.send(JSON.stringify(payload));
                while (keys_down.length > 0) {
                    keys_down.pop();
                }
            }
        }

        ws.onmessage = function(evt) {
            const message = JSON.parse(evt.data);
            if (message) {
                updateView(message);
            }
        };
    };
}());
