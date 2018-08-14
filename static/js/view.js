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
        const socket_events_json = 'static/websocketevents.json';
        let keys_data;
        let socket_events;
        let ws;
        let tile_info;
        let cells = {};
        let tile_width;
        let tile_height;
        let world_width;
        let world_height;
        let camera;
        let app;

        // noinspection JSUnresolvedFunction
        PIXI.loader
            .add([
                config_json,
                keys_json,
                socket_events_json,
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
            keys_data = resources[keys_json].data;
            socket_events = resources[socket_events_json].data;

            tile_width = config.tiles.width;
            tile_height = config.tiles.height;
            const map_tile_width = config.server.width;
            const map_tile_height = config.server.height;
            world_width = map_tile_width * tile_width;
            world_height = map_tile_height * tile_height;

            const renderDiv = document.getElementById('render');

            // noinspection JSValidateTypes
            PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

            app = new PIXI.Application({
                width: window.innerWidth * 0.7,
                height: window.innerHeight * 0.8,
                transparent: true
            });
            camera = new PIXI.Container();
            app.stage.addChild(camera);
            renderDiv.appendChild(app.view);
            window.addEventListener('resize', resize);

            setupWebsockets(config);
            app.ticker.add(delta => gameLoop(delta));
            console.log('Done loading.');
            resize();
        }

        function resize() {
            app.renderer.resize(window.innerWidth * 0.7, window.innerHeight * 0.8);
            camera.position.set(app.screen.width / 2, app.screen.height / 2);
            requestRefresh();
        }

        function gameLoop(delta) {

        }

        function handleBinaryData(data) {
            const headerByte = new Uint8Array(data)[0];
            const actualData = data.slice(1, data.length);
            switch (headerByte) {
                case socket_events.FromServer.GameLog:
                    handleGameLog(actualData);
                    break;
                case socket_events.FromServer.UpdateMap:
                    handleUpdateMap(actualData);
                    break;
                default:
                    console.error('Got unknown event from server.', headerByte);
            }
        }

        function handleGameLog(data) {
            const string = new TextDecoder().decode(data);
            const parsed = JSON.parse(string);
            parsed.lines.forEach(function(line) {
                console.log(line[0]);
            });
        }

        function handleUpdateMap(data) {
            const view = new DataView(data);
            const player_x = view.getUint16(0) * tile_width;
            const player_y = view.getUint16(2) * tile_height;
            camera.pivot.x = player_x;
            camera.pivot.y = player_y;
            const num_cells = view.getUint16(4);
            const offset = 6;      // header size in bytes
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

            const cameraRect = new PIXI.Rectangle();
            cameraRect.x = camera.pivot.x - app.screen.width / 2;
            cameraRect.y = camera.pivot.y - app.screen.height / 2;
            cameraRect.width = app.screen.width;
            cameraRect.height = app.screen.height;

            sprite.visible = (
                (cell.tile_id > 0) &&
                (sprite.x > (cameraRect.left - 3*tile_width)) &&
                (sprite.y > (cameraRect.top - 3*tile_height)) &&
                (sprite.x < (cameraRect.right + 3*tile_width)) &&
                (sprite.y < (cameraRect.bottom + 3*tile_height))
            );
        }

        function makeSprite(cell) {
            const tile = tile_info[cell.tile_id];
            const tex = PIXI.loader.resources[tile.tileset].textures[tile.tiles[0]];
            const sprite = new PIXI.Sprite(tex);
            sprite.x = tile_width * cell.x;
            sprite.y = tile_height * cell.y;
            sprite.tint = cell.tint;
            camera.addChild(sprite);
            cells[cell.id] = sprite;
        }

        function setupWebsockets(config) {
            const host = config.server.host;
            const port = config.server.port;
            let pausingKeyPress = false;
            let pausingKeyPressTimer = null;
            ws = new WebSocket("ws://" + host + ":" + port + "/websocket");
            ws.binaryType = 'arraybuffer';

            document.addEventListener("keypress", function (event) {
                if (event.defaultPrevented) {
                    return;
                }

                if (pausingKeyPress) {
                    return;
                }

                if (pausingKeyPressTimer === null) {
                    pausingKeyPressTimer = setTimeout(function () {
                        pausingKeyPress = false;
                        clearTimeout(pausingKeyPressTimer);
                        pausingKeyPressTimer = null;
                    }, 110);
                    pausingKeyPress = true;
                }

                let modifiers = 0;
                if (event.shiftKey) {
                    modifiers |= keys_data.Modifiers.Shift;
                }
                if (event.ctrlKey) {
                    modifiers |= keys_data.Modifiers.Ctrl;
                }
                if (event.altKey) {
                    modifiers |= keys_data.Modifiers.Alt;
                }
                const key = event.code.replace(/^Key/, "").replace(/^Digit/, "");
                let code = 0;
                if (key.length === 1) {
                    code = key.charCodeAt(0);
                } else {
                    code = keys_data.Keys[event.code] || 0;
                }
                let buffer = new ArrayBuffer(8);
                const view = new DataView(buffer);
                // byte 0: socket event type
                // byte 1: input event flags
                // byte 2: modifier keys
                // byte 3: key/button code
                // byte 4-5: x coordinate
                // byte 6-7: y coordinate
                view.setUint8(0, socket_events.ToServer.GameInput);
                view.setUint8(1, keys_data.Events.KeyPress);
                view.setUint8(2, modifiers);
                view.setUint8(3, code);
                view.setUint16(4, 0);
                view.setUint16(6, 0);
                const data = new Uint8Array(buffer);
                ws.send(data);
            });

            ws.onmessage = function (evt) {
                handleBinaryData(evt.data)
            };

            ws.onopen = function(evt) {
                requestRefresh();
            };
        }

        function requestRefresh() {
            if (ws.readyState === 1) {
                let refresh = new Uint8Array(1);
                refresh[0] = socket_events.ToServer.RefreshGraphics;
                ws.send(refresh);
            }
        }
    };
}());
