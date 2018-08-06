(function () {
    window.onload = function() {
        const img_dir = 'static/img/';
        const tileset_dir = img_dir + 'oryx_ur/';
        const tileset_avatar = tileset_dir + 'Avatar.json';
        const tileset_avatar_equipment = tileset_dir + 'Avatar_Equipment.json';
        const tileset_fx_blood = tileset_dir + 'FX_Blood.json';
        const tileset_fx_general = tileset_dir + 'FX_General.json';
        const tileset_fx_projectiles = tileset_dir + 'FX_Projectiles.json';
        const tileset_items = tileset_dir + 'Items.png';
        const tileset_monsters = tileset_dir + 'Monsters.json';
        const tileset_monsters_scifi = tileset_dir + 'Monsters_Scifi.png';
        const tileset_terrain = tileset_dir + 'Terrain.json';
        const tileset_terrain_objects = tileset_dir + 'Terrain_Objects.png';
        const tile_id_table = tileset_dir + 'tile_ids.json';
        const config_json = 'static/config.json';
        const keys_json = 'static/keys.json';
        let tile_info;
        let cells = {};
        let tile_width;
        let tile_height;
        let world_width;
        let world_height;
        let app;

        // noinspection JSUnresolvedFunction
        PIXI.loader
            .add([
                config_json,
                keys_json,
                tileset_avatar,
                tileset_avatar_equipment,
                tileset_fx_blood,
                tileset_fx_general,
                tileset_fx_projectiles,
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
            const config = resources[config_json].data;
            tile_info = resources[tile_id_table].data;

            tile_width = config.tiles.width;
            tile_height = config.tiles.height;
            const map_tile_width = config.server.width;
            const map_tile_height = config.server.height;
            world_width = map_tile_width * tile_width;
            world_height = map_tile_height * tile_height;

            // noinspection JSValidateTypes
            PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

            app = new PIXI.Application({
                width: tile_width * map_tile_width,
                height: tile_height * map_tile_height
            });
            document.body.appendChild(app.view);

            setupWebsockets(config, resources[keys_json].data);
            app.ticker.add(delta => gameLoop(delta));
            console.log('Done loading.');
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

        function setupWebsockets(config, keys) {
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
                    modifiers |= keys.Modifiers.Shift;
                }
                if (event.ctrlKey) {
                    modifiers |= keys.Modifiers.Ctrl;
                }
                if (event.altKey) {
                    modifiers |= keys.Modifiers.Alt;
                }
                const key = event.code.replace(/^Key/, "").replace(/^Digit/, "");
                let code = 0;
                if (key.length === 1) {
                    code = key.charCodeAt(0);
                } else {
                    code = keys.Keys[event.code] || 0;
                }
                let buffer = new ArrayBuffer(7);
                const view = new DataView(buffer);
                // byte 0: event type
                // byte 1: modifier keys
                // byte 2: key/button code
                // byte 3-4: x coordinate
                // byte 5-6: y coordinate
                view.setUint8(0, keys.Events.KeyPress);
                view.setUint8(1, modifiers);
                view.setUint8(2, code);
                view.setUint16(3, 0);
                view.setUint16(5, 0);
                const data = new Uint8Array(buffer);
                ws.send(data);
            });

            ws.onmessage = function (evt) {
                handleBinaryData(evt.data)
            };
        }
    };
}());
