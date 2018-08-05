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
        const tile_id_table = tileset_dir + 'tile_ids.json';
        const config_json = 'static/config.json';

        const MOD_SHIFT = 1 << 0;
        const MOD_CTRL  = 1 << 1;
        const MOD_ALT   = 1 << 2;
        const SPECIAL_KEYS = {
            "Enter": 1,
            "Space": 32,
            "Tab": 24,
            "Backtick": 28
        };

        // TODO: get rid of these
        const tile_width = 16;
        const tile_height = 24;
        const map_tile_width = 70;
        const map_tile_height = 26;
        const world_width = map_tile_width * tile_width;
        const world_height = map_tile_height * tile_height;

        let tile_info;
        let cells = {};

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
                config_json,
                tileset_avatar,
                tileset_avatar_equipment,
                tileset_items,
                tileset_monsters,
                tileset_monsters_scifi,
                tileset_terrain,
                tileset_terrain_objects,
                tile_id_table
            ])
            .on("progress", loadProgressHandler)
            .load(setup);

        function loadProgressHandler(loader, resource) {
            console.log("loading: " + resource.url);
            console.log("progress: " + loader.progress + "%");
        }

        function setup(loader, resources) {
            tile_info = resources[tile_id_table].data;
            console.log('Done loading.');
            setupWebsockets(resources[config_json].data);
            app.ticker.add(delta => gameLoop(delta));
        }

        function gameLoop(delta) {

        }

        function handleBinaryData(data) {
            const view = new DataView(data);
            const num_cells = view.getUint16(0);
            const offset = 2;      // header is 2 bytes
            const cell_size = 12;  // cell size in bytes
            for (let i = 0; i < num_cells; i++) {
                const cell_offset = offset + (i * cell_size);
                const cell = {
                    id: view.getUint16(cell_offset),
                    x: view.getUint16(cell_offset + 2),
                    y: view.getUint16(cell_offset + 4),
                    tile_id: view.getUint16(cell_offset + 6),
                    tint: view.getUint32(cell_offset + 8),
                };
                if (cells[cell.id] === undefined) {
                    makeSprite(cell);
                } else {
                    updateSprite(cell);
                }
            }
        }

        function updateSprite(cell) {
            const sprite = cells[cell.id];
            sprite.x = tile_width * cell.x;
            sprite.y = tile_height * cell.y;
            sprite.tint = cell.tint;
            sprite.visible = (
                (sprite.x + tile_width) > 0 &&
                (sprite.y + tile_height) > 0 &&
                sprite.x < world_width &&
                sprite.y < world_height
            );
        }

        function makeSprite(cell) {
            const tile = tile_info[cell.tile_id];
            const tex = PIXI.loader.resources[tile.tileset].textures[tile.tiles[0]];
            const sprite = new PIXI.Sprite(tex);
            sprite.x = tile_width * cell.x;
            sprite.y = tile_height * cell.y;
            sprite.tint = cell.tint;
            app.stage.addChild(sprite);
            cells[cell.id] = sprite;
        }

        function setupWebsockets(config) {
            let keys_down = [];
            const host = config.server.host;
            const port = config.server.port;
            const ws = new WebSocket("ws://" + host + ":" + port + "/websocket");
            ws.binaryType = 'arraybuffer';

            document.addEventListener("keypress", function (event) {
                if (event.defaultPrevented) {
                    return;
                }
                let modifiers = 0;
                if (event.shiftKey) {
                    modifiers |= MOD_SHIFT;
                }
                if (event.ctrlKey) {
                    modifiers |= MOD_CTRL;
                }
                if (event.altKey) {
                    modifiers |= MOD_ALT;
                }
                const key = event.code.replace(/^Key/, "").replace(/^Digit/, "");
                let code = 0;
                if (key.length === 1) {
                    code = key.charCodeAt(0);
                } else {
                    code = SPECIAL_KEYS[event.code] || 0;
                }
                console.log(event);
                console.log(event.code, key, code, modifiers);
                if (event.key !== 'Meta' && event.key !== 'Alt') {
                    keys_down.push(event.key);
                }
                if (!keys_down.includes('Control')) {
                    sendKeys()
                }
            });

            document.addEventListener("keyup", sendKeys);

            function sendKeys() {
                // TODO: improve performance - send binary?
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

            ws.onmessage = function (evt) {
                handleBinaryData(evt.data)
            };
        }
    };
}());
