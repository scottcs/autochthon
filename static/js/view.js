(function () {
    window.onload = function() {
        const img_dir = 'static/img/';
        const tileset_dir = img_dir + 'oryx_ur/';
        const tileset_avatar = tileset_dir + 'Avatar.json';
        const tileset_avatar_equipment = tileset_dir + 'Avatar_Equipment.json';
        const tileset_fx_blood = tileset_dir + 'FX_Blood.json';
        const tileset_fx_general = tileset_dir + 'FX_General.json';
        const tileset_fx_projectiles = tileset_dir + 'FX_Projectiles.json';
        const tileset_items = tileset_dir + 'Items.json';
        const tileset_monsters = tileset_dir + 'Monsters.json';
        const tileset_monsters_scifi = tileset_dir + 'Monsters_Scifi.json';
        const tileset_terrain = tileset_dir + 'Terrain.json';
        const tileset_terrain_objects = tileset_dir + 'Terrain_Objects.json';
        const tile_id_table = tileset_dir + 'tile_ids.json';
        const config_json = 'data/config.json';
        const keys_json = 'data/keys.json';
        const socket_events_json = 'data/websocketevents.json';
        const main_width_scale = 0.7;
        const main_height_scale = 0.88;
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
        let layer_background;
        let layer_floor;
        let layer_item;
        let layer_wall;
        let layer_icon;
        let layer_enemy;
        let layer_player;
        let layer_effect;
        let app;

        PIXI.settings.SCALE_MODE = PIXI.SCALE_MODES.NEAREST;

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

            app = new PIXI.Application({
                width: window.innerWidth * main_width_scale,
                height: window.innerHeight * main_height_scale,
                antialias: false,
                transparent: true
            });
            camera = new PIXI.Container();
            layer_background = new PIXI.Container();
            layer_floor = new PIXI.Container();
            layer_item = new PIXI.Container();
            layer_wall = new PIXI.Container();
            layer_icon = new PIXI.Container();
            layer_enemy = new PIXI.Container();
            layer_player = new PIXI.Container();
            layer_effect = new PIXI.Container();
            app.stage.addChild(camera);
            camera.addChild(layer_background);
            camera.addChild(layer_floor);
            camera.addChild(layer_item);
            camera.addChild(layer_wall);
            camera.addChild(layer_icon);
            camera.addChild(layer_enemy);
            camera.addChild(layer_player);
            camera.addChild(layer_effect);
            // camera.scale.set(2);

            renderDiv.appendChild(app.view);
            window.addEventListener('resize', resize);

            setupWebsockets(config);
            app.ticker.add(delta => gameLoop(delta));
            console.log('Done loading.');
            resize();
        }

        function resize() {
            app.renderer.resize(
                window.innerWidth * main_width_scale,
                window.innerHeight * main_height_scale);
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
                case socket_events.FromServer.ChooseFromList:
                    handleChooseFromList(actualData);
                    break;
                default:
                    console.error('Got unknown event from server.', headerByte);
            }
        }

        function handleGameLog(data) {
            const string = new TextDecoder().decode(data);
            const parsed = JSON.parse(string);
            const logDiv = document.getElementById('gameLog');
            parsed.lines.forEach(function(line) {
                const newSpan = document.createElement('span');
                color = '#' + line[1].toString(16).padStart(6, '0');
                newSpan.classList.add('logline');
                newSpan.setAttribute('style', 'color: ' + color + ';');
                newSpan.textContent = line[0];
                logDiv.appendChild(newSpan);
            });
            logDiv.appendChild(document.createElement('br'));
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function handleUpdateMap(data) {
            setAllSpritesInvisible();
            const view = new DataView(data);
            const player_x = view.getUint16(0) * tile_width;
            const player_y = view.getUint16(2) * tile_height;
            camera.pivot.x = player_x;
            camera.pivot.y = player_y;
            const num_cells = view.getUint16(4);
            const offset = 6;      // header size in bytes
            const cell_size = 13;  // cell size in bytes
            for (let i = 0; i < num_cells; i++) {
                const cell_offset = offset + (i * cell_size);
                const cell_color_offset = cell_offset + 8;
                const cell_r = view.getUint8(cell_color_offset);
                const cell_g = view.getUint8(cell_color_offset + 1);
                const cell_b = view.getUint8(cell_color_offset + 2);
                const cell_a = view.getUint8(cell_color_offset + 3) / 255.0;
                const cell_tint = 65536*cell_r + 256*cell_g + cell_b;
                const cell = {
                    id: view.getUint16(cell_offset),
                    x: view.getUint16(cell_offset + 2),
                    y: view.getUint16(cell_offset + 4),
                    tile_id: view.getUint16(cell_offset + 6),
                    tint: cell_tint,
                    alpha: cell_a,
                    layer: view.getUint8(cell_offset + 12)
                };
                if (cells[cell.id] === undefined) {
                    makeSprite(cell);
                } else {
                    updateSprite(cell);
                }
            }
        }

        function handleChooseFromList(data) {
            const string = new TextDecoder().decode(data);
            const parsed = JSON.parse(string);
            let index = 0;
            const div = document.createElement('div');
            parsed.items.forEach(function(line) {
                const choiceSpan = document.createElement('span');
                choiceSpan.classList.add('choice');
                choiceSpan.textContent = line[0] + ": ";
                div.appendChild(choiceSpan);
                const newSpan = document.createElement('span');
                color = '#' + line[2].toString(16).padStart(6, '0');
                newSpan.classList.add('choice');
                newSpan.setAttribute('style', 'color: ' + color + ';');
                newSpan.textContent = line[1];
                div.appendChild(newSpan);
                div.appendChild(document.createElement('br'));
                index++;
            });
            getChoiceFromListModal(div.innerHTML, parsed);
        }

        function getChoiceFromListModal(html, parsed) {
            const modal = document.getElementById('gameModal');

            // When the user clicks anywhere outside of the modal, close it
            const closeModal = function() {
                modal.style.display = "none";
                window.removeEventListener('click', onModalClick)
                document.removeEventListener("keypress", onKeyPress);
                document.addEventListener("keypress", defaultKeyHandler);
            };

            const openModal = function() {
                const modal_header = document.getElementById('gameModalHeader');
                const modal_inner_content = document.getElementById('gameModalInnerContent');
                modal.style.display = "block";
                modal_header.innerText = parsed.prompt;
                modal_inner_content.innerHTML = html;
                modal_inner_content.scrollTop = modal_inner_content.scrollHeight;
                window.addEventListener('click', onModalClick);
                document.removeEventListener("keypress", defaultKeyHandler);
                document.addEventListener("keypress", onKeyPress);
            };

            const onModalClick = function(event) {
                if (event.target === modal) {
                    closeModal();
                }
            };

            const onKeyPress = function(event) {
                keyHandler(event, function (event) {
                    if (event.code === 'Escape') {
                        closeModal();
                    } else {
                        const modifiers = getKeyModifiers(event);
                        let code = getKeyLetter(event);
                        if (!event.shiftKey) {
                            code = code.toLowerCase();
                        }
                        for (let i = 0; i < parsed.items.length; i++) {
                            const line = parsed.items[i];
                            if (line[0] === code) {
                                sendChoiceToServer(event);
                                closeModal()
                                break;
                            }
                        }
                    }
                })
            };

            if (modal.style.display === "block") {
                closeModal();
            } else {
                openModal();
            }
        }

        function writeToLog(msg) {
            const logDiv = document.getElementById('gameLog');
            const newSpan = document.createElement('span');
            newSpan.classList.add('logline');
            newSpan.textContent = msg;
            logDiv.appendChild(newSpan);
            logDiv.appendChild(document.createElement('br'));
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function setAllSpritesInvisible() {
            Object.keys(cells).forEach(function(key) {
                cells[key].visible = false;
            })
        }

        function updateSprite(cell) {
            const sprite = cells[cell.id];
            sprite.x = tile_width * cell.x;
            sprite.y = tile_height * cell.y;
            sprite.tint = cell.tint;
            sprite.alpha = cell.alpha;

            const cameraRect = new PIXI.Rectangle();
            cameraRect.x = camera.pivot.x - app.screen.width / 2;
            cameraRect.y = camera.pivot.y - app.screen.height / 2;
            cameraRect.width = app.screen.width;
            cameraRect.height = app.screen.height;

            sprite.visible = (
                (cell.tile_id > 0) &&
                (cell.alpha > 0) &&
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
            sprite.alpha = cell.alpha;
            // We'll assume sprites won't change layers
            switch (cell.layer) {
                case 2:
                    layer_floor.addChild(sprite);
                    break;
                case 3:
                    layer_item.addChild(sprite);
                    break;
                case 4:
                    layer_wall.addChild(sprite);
                    break;
                case 5:
                    layer_icon.addChild(sprite);
                    break;
                case 6:
                    layer_enemy.addChild(sprite);
                    break;
                case 7:
                    layer_player.addChild(sprite);
                    break;
                case 8:
                    layer_effect.addChild(sprite);
                    break;
                default:
                    layer_background.addChild(sprite);
            }
            cells[cell.id] = sprite;
        }

        function keyHandler(event, callback) {
            let pausingKeyPress = false;
            let pausingKeyPressTimer = null;
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

            callback(event);
        }

        function getKeyModifiers(event) {
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
            return modifiers;
        }

        function getKeyLetter(event) {
            return event.code.replace(/^Key/, "").replace(/^Digit/, "");
        }

        function getKeyCodeForServer(event) {
            const key = getKeyLetter(event);
            let code = 0;
            if (key.length === 1) {
                code = key.charCodeAt(0);
            } else {
                code = keys_data.Keys[event.code] || 0;
            }
            return code;
        }

        function defaultKeyHandler(event) {
            keyHandler(event, function(event) {
                if (!keyHandled(event)) {
                    sendInputToServer(event);
                }
            })
        }

        function setupWebsockets(config) {
            const host = config.server.host;
            const port = config.server.port;
            ws = new WebSocket("ws://" + host + ":" + port + "/websocket");
            ws.binaryType = 'arraybuffer';

            document.addEventListener("keypress", defaultKeyHandler);

            ws.onmessage = function (evt) {
                handleBinaryData(evt.data)
            };

            ws.onopen = function(evt) {
                requestRefresh();
            };
        }

        function keyHandled(event) {
            // Handle keypress locally first, possibly
            if (event.ctrlKey && event.code === 'KeyP') {
                toggleGameLogModal();
                return true;
            }

            return false;
        }

        function sendInputToServer(event) {
            const modifiers = getKeyModifiers(event);
            const code = getKeyCodeForServer(event);
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
        }

        function sendChoiceToServer(event) {
            const modifiers = getKeyModifiers(event);
            const code = getKeyCodeForServer(event);
            let buffer = new ArrayBuffer(8);
            const view = new DataView(buffer);
            // byte 0: socket event type
            // byte 1: modifier keys
            // byte 2: key/button code
            view.setUint8(0, socket_events.ToServer.ChoiceFromList);
            view.setUint8(1, modifiers);
            view.setUint8(2, code);
            const data = new Uint8Array(buffer);
            ws.send(data);
        }

        function toggleGameLogModal() {
            const modal = document.getElementById('gameModal');

            // When the user clicks anywhere outside of the modal, close it
            const closeModal = function() {
                modal.style.display = "none";
                window.removeEventListener('click', onModalClick);
                document.removeEventListener("keypress", onKeyPress);
                document.addEventListener("keypress", defaultKeyHandler);
            };

            const openModal = function() {
                const modal_header = document.getElementById('gameModalHeader');
                const modal_inner_content = document.getElementById('gameModalInnerContent');
                const game_log = document.getElementById('gameLog');
                modal.style.display = "block";
                modal_header.innerText = 'Game Log:';
                modal_inner_content.innerHTML = game_log.innerHTML;
                modal_inner_content.scrollTop = modal_inner_content.scrollHeight;
                window.addEventListener('click', onModalClick);
                document.removeEventListener("keypress", defaultKeyHandler);
                document.addEventListener("keypress", onKeyPress);
            };

            const onModalClick = function(event) {
                if (event.target === modal) {
                    closeModal();
                }
            };

            const onKeyPress = function(event) {
                keyHandler(event, function (event) {
                    if ((event.code === 'Escape') || (event.ctrlKey && event.code === 'KeyP')) {
                        closeModal();
                    }
                })
            };

            if (modal.style.display === "block") {
                closeModal();
            } else {
                openModal();
            }
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
