(function () {
    window.onload = function() {
        const img_dir = "static/img/";
        const tileset_dir = img_dir + "oryx_ur/";
        const tileset_avatar = tileset_dir + "Avatar.json";
        const tileset_avatar_equipment = tileset_dir + "Avatar_Equipment.json";
        const tileset_fx_blood = tileset_dir + "FX_Blood.json";
        const tileset_fx_general = tileset_dir + "FX_General.json";
        const tileset_fx_projectiles = tileset_dir + "FX_Projectiles.json";
        const tileset_items = tileset_dir + "Items.json";
        const tileset_monsters = tileset_dir + "Monsters.json";
        const tileset_monsters_scifi = tileset_dir + "Monsters_Scifi.json";
        const tileset_terrain = tileset_dir + "Terrain.json";
        const tileset_terrain_objects = tileset_dir + "Terrain_Objects.json";
        const tile_id_table = tileset_dir + "tile_ids.json";
        const config_json = "data/config.json";
        const keys_json = "data/keys.json";
        const socket_events_json = "data/websocketevents.json";
        const main_width_scale = 0.7;
        const main_height_scale = 0.88;
        const defaultColorInt = 11184810;  // #aaaaaa
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
        let mapBits;
        let parsedChoices;
        let modalKeyHandler;
        let modalClickHandler;
        let subModalKeyHandler;
        let subModalClickHandler;
        let isModalOpen = false;
        let isSubModalOpen = false;

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
            mapBits = config.map_bits;
            tile_info = resources[tile_id_table].data;
            keys_data = resources[keys_json].data;
            socket_events = resources[socket_events_json].data;

            tile_width = config.tiles.width;
            tile_height = config.tiles.height;
            const map_tile_width = config.server.width;
            const map_tile_height = config.server.height;
            world_width = map_tile_width * tile_width;
            world_height = map_tile_height * tile_height;

            const renderDiv = document.getElementById("render");

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
            window.addEventListener("resize", resize);

            setupWebsockets(config);
            app.ticker.add(delta => gameLoop(delta));
            console.log("Done loading.");
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

        const closeModal = function() {
            isModalOpen = false;
            const modal = document.getElementById("gameModal");
            const modalContent = document.getElementById("gameModalContent");
            modal.classList.remove("open");
            modalContent.classList.remove("open");
            notifyModalClosed();
        };

        const closeSubModal = function() {
            isSubModalOpen = false;
            const subModal = document.getElementById("gameSubModal");
            const subModalContent = document.getElementById("gameSubModalContent");
            subModal.classList.remove("open");
            subModalContent.classList.remove("open");
            notifySubModalClosed();
        };

        const openModal = function(header, content, footer) {
            isModalOpen = true;
            const modal = document.getElementById("gameModal");
            const modalContent = document.getElementById("gameModalContent");
            const modalHeader = document.getElementById("gameModalHeader");
            const modalBody = document.getElementById("gameModalBody");
            const modalFooter = document.getElementById("gameModalFooter");
            const modalStatus = document.getElementById("gameModalStatus");
            modal.classList.add("open");
            modalContent.classList.add("open");
            modalHeader.innerText = header;
            modalBody.innerHTML = content;
            modalFooter.innerText = footer;
            modalStatus.innerText = "";
            modalBody.scrollTop = modalBody.scrollHeight;
        };

        const openSubModal = function(header, content, footer) {
            isSubModalOpen = true;
            const subModal = document.getElementById("gameSubModal");
            const subModalContent = document.getElementById("gameSubModalContent");
            const subModalHeader = document.getElementById("gameSubModalHeader");
            const subModalBody = document.getElementById("gameSubModalBody");
            const subModalFooter = document.getElementById("gameSubModalFooter");
            const subModalStatus = document.getElementById("gameSubModalStatus");
            subModal.classList.add("open");
            subModalContent.classList.add("open");
            subModalHeader.innerText = header;
            subModalBody.innerHTML = content;
            subModalFooter.innerText = footer;
            subModalStatus.innerText = "";
            subModalBody.scrollTop = subModalBody.scrollHeight;
        };

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
                case socket_events.FromServer.ChoiceAccepted:
                    handleChoiceAccepted(actualData);
                    break;
                case socket_events.FromServer.ChoiceDeclined:
                    handleChoiceDeclined(actualData);
                    break;
                case socket_events.FromServer.Describe:
                    handleDescribe(actualData);
                    break;
                default:
                    console.error("Got unknown event from server.", headerByte);
            }
        }

        function handleGameLog(data) {
            const string = new TextDecoder().decode(data);
            const parsed = JSON.parse(string);
            const logDiv = document.getElementById("gameLog");
            parsed.lines.forEach(function(line) {
                const newSpan = document.createElement("span");
                color = "#" + line[1].toString(16).padStart(6, "0");
                newSpan.classList.add("logline");
                newSpan.setAttribute("style", "color: " + color + ";");
                newSpan.textContent = line[0];
                logDiv.appendChild(newSpan);
            });
            logDiv.appendChild(document.createElement("br"));
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function handleUpdateMap(data) {
            const view = new DataView(data);
            const player_x = view.getUint16(0) * tile_width;
            const player_y = view.getUint16(2) * tile_height;
            camera.pivot.x = player_x;
            camera.pivot.y = player_y;
            const num_cells = view.getUint16(4);
            let offset = 6;      // header size in bytes
            for (let i = 0; i < num_cells; i++) {
                const cell_id = view.getUint16(offset);
                offset += 2;
                const bitmask = view.getUint8(offset);
                offset += 1;
                const cell = {id: cell_id}
                if (bitmask & mapBits.x) {
                    cell.x = view.getUint16(offset);
                    offset += 2;
                }
                if (bitmask & mapBits.y) {
                    cell.y = view.getUint16(offset);
                    offset += 2;
                }
                if (bitmask & mapBits.tile_id) {
                    cell.tile_id = view.getUint16(offset);
                    offset += 2;
                }
                if (bitmask & mapBits.tint) {
                    const cell_r = view.getUint8(offset);
                    offset += 1;
                    const cell_g = view.getUint8(offset);
                    offset += 1;
                    const cell_b = view.getUint8(offset);
                    offset += 1;
                    cell.tint = 65536*cell_r + 256*cell_g + cell_b;
                }
                if (bitmask & mapBits.alpha) {
                    cell.alpha = view.getUint8(offset) / 255.0;
                    offset += 1;
                }
                if (bitmask & mapBits.layer) {
                    cell.layer = view.getUint8(offset);
                    offset += 1;
                }
                if (bitmask & mapBits.delete) {
                    cell.delete = true;
                }

                if (cells[cell.id] === undefined) {
                    makeSprite(cell);
                } else {
                    updateSprite(cell);
                }
            }
        }

        function handleChooseFromList(data) {
            const string = new TextDecoder().decode(data);
            parsedChoices = JSON.parse(string);
            const div = document.createElement("div");
            const disable = parsedChoices.disable === undefined ? [] : parsedChoices.disable;
            const select = parsedChoices.select === undefined ? [] : parsedChoices.select;
            if (parsedChoices.items.equipped !== undefined) {
                makeInventoryList(div, parsedChoices.items.equipped, "Equipped:", disable, select);
            }
            if (parsedChoices.items.unequipped !== undefined) {
                makeInventoryList(div, parsedChoices.items.unequipped, "Unequipped:", disable, select);
            }
            openChoiceFromListModal(div.innerHTML);
        }

        function makeInventoryList(div, items, header, disabled, selected) {
            headerSpan = document.createElement("span");
            headerSpan.classList.add("choice-header");
            headerSpan.textContent = header;
            div.appendChild(headerSpan);
            div.appendChild(document.createElement("br"));
            items.forEach(function(line) {
                const isDisabled = disabled.includes[line[0]];
                const isSelected = selected.includes[line[1]];
                const outerSpan = document.createElement("span");
                if (isSelected) {
                    outerSpan.classList.add("selected");
                }
                outerSpan.appendChild(makeColoredSpan(
                    line[1] + ": ", "choice", defaultColorInt, isDisabled
                ));
                outerSpan.appendChild(makeColoredSpan(line[2], "choice", line[3], isDisabled));
                if (line.length > 4) {
                    if (line.length <= 5) {
                        line.push(defaultColorInt);
                    }
                    outerSpan.appendChild(makeColoredSpan(line[4], "choice", line[5], isDisabled));
                }
                div.appendChild(outerSpan);
                div.appendChild(document.createElement("br"));
            });
        }

        function makeColoredSpan(text, withClass, colorInt, isDisabled) {
            const newSpan = document.createElement("span");
            newSpan.classList.add(withClass);
            if (isDisabled) {
                newSpan.classList.add("disabled");
            } else {
                color = "#" + colorInt.toString(16).padStart(6, "0");
                newSpan.setAttribute("style", "color: " + color + ";");
            }
            newSpan.textContent = text;
            return newSpan;
        }

        function choiceListModalKeyHandler(event) {
            if (event.code === "Escape") {
                closeModal();
            } else {
                const modifiers = getKeyModifiers(event);
                let code = getKeyLetter(event);
                if (!event.shiftKey) {
                    code = code.toLowerCase();
                }
                let found = false;
                if (parsedChoices.items.equipped !== undefined) {
                    for (let i = 0; i < parsedChoices.items.equipped.length; i++) {
                        const line = parsedChoices.items.equipped[i];
                        if (line[1] === code) {
                            found = true;
                            break;
                        }
                    }
                }
                if (!found && (parsedChoices.items.unequipped !== undefined)) {
                    for (let i = 0; i < parsedChoices.items.unequipped.length; i++) {
                        const line = parsedChoices.items.unequipped[i];
                        if (line[1] === code) {
                            found = true;
                            break;
                        }
                    }
                }
                if (found) {
                    sendChoiceToServer(event);
                }
            }
        }

        function choiceListModalClickHandler(event) {
            // TODO: handle clicking on items?
        }

        function openChoiceFromListModal(html) {
            modalClickHandler = choiceListModalClickHandler;
            modalKeyHandler = choiceListModalKeyHandler;
            header = "";
            footer = "";
            if (parsedChoices.header !== undefined) {header = parsedChoices.header;}
            if (parsedChoices.footer !== undefined) {footer = parsedChoices.footer;}
            openModal(header, html, footer);
        }

        function handleChoiceAccepted(data) {
            closeModal();
        }

        function handleChoiceDeclined(data) {
            const string = new TextDecoder().decode(data);
            const parsed = JSON.parse(string);
            if (parsed.status !== undefined) {
                const status = document.getElementById("gameModalStatus");
                status.innerText = parsed.status;
            }
            if (parsed.substatus !== undefined) {
                const status = document.getElementById("gameSubModalStatus");
                status.innerText = parsed.substatus;
            }
        }

        function handleDescribe(data) {
            console.log("Describe");
            const string = new TextDecoder().decode(data);
            const parsed = JSON.parse(string);
            console.log(parsed);
            const div = document.createElement("div");
            div.appendChild(makeColoredSpan(parsed.msg, "description", defaultColorInt, false));
            openDescriptionSubModal(parsed.name, div.innerHTML, parsed.choices);
        }

        function writeToLog(msg) {
            const logDiv = document.getElementById("gameLog");
            const newSpan = document.createElement("span");
            newSpan.classList.add("logline");
            newSpan.textContent = msg;
            logDiv.appendChild(newSpan);
            logDiv.appendChild(document.createElement("br"));
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function updateSprite(cell) {
            const sprite = cells[cell.id];
            if (cell.delete) {
                cells[cell.id] = undefined;
                sprite.visible = false;
                sprite.parent.removeChild(sprite);
                return;
            }

            if (cell.x !== undefined) {
                sprite.x = tile_width * cell.x;
            }
            if (cell.y !== undefined) {
                sprite.y = tile_height * cell.y;
            }
            if (cell.tint !== undefined) {
                sprite.tint = cell.tint;
            }
            if (cell.alpha !== undefined) {
                sprite.alpha = cell.alpha;
            }
            // Sprites don't change layers so we don't check cell.layer

            const cameraRect = new PIXI.Rectangle();
            cameraRect.x = camera.pivot.x - app.screen.width / 2;
            cameraRect.y = camera.pivot.y - app.screen.height / 2;
            cameraRect.width = app.screen.width;
            cameraRect.height = app.screen.height;

            sprite.visible = (
                (sprite.alpha > 0) &&
                (sprite.x > (cameraRect.left - 3*tile_width)) &&
                (sprite.y > (cameraRect.top - 3*tile_height)) &&
                (sprite.x < (cameraRect.right + 3*tile_width)) &&
                (sprite.y < (cameraRect.bottom + 3*tile_height))
            );
        }

        function makeSprite(cell) {
            if (cell.delete) {return;}
            const tile = tile_info[cell.tile_id];
            if (tile === undefined) {
                console.error("tile is undefined for ", cell)
                return;
            }
            const tex = PIXI.loader.resources[tile.tileset].textures[tile.tiles[0]];
            const sprite = new PIXI.Sprite(tex);
            sprite.x = tile_width * cell.x;
            sprite.y = tile_height * cell.y;
            sprite.tint = cell.tint;
            sprite.alpha = cell.alpha;
            // We"ll assume sprites won't change layers
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
            ws.binaryType = "arraybuffer";

            document.addEventListener("keypress", defaultKeyHandler);

            ws.onmessage = function (evt) {
                handleBinaryData(evt.data)
            };

            ws.onopen = function(evt) {
                requestRefresh(true);
            };
        }

        function keyHandled(event) {
            if (isSubModalOpen && subModalKeyHandler !== undefined) {
                subModalKeyHandler(event);
                return true;
            } else if (isModalOpen && modalKeyHandler !== undefined) {
                modalKeyHandler(event);
                return true;
            } else {
                // Handle keypress locally first, possibly
                if (event.ctrlKey && event.code === "KeyP") {
                    openGameLogModal();
                    return true;
                }
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

        function gameLogModalKeyHandler(event) {
            if ((event.code === "Escape") || (event.ctrlKey && event.code === "KeyP")) {
                closeModal();
            }
        }

        function gameLogModalClickHandler(event) {
            // TODO: handle clicking on items?
        }

        function openGameLogModal() {
            modalClickHandler = gameLogModalClickHandler;
            modalKeyHandler = gameLogModalKeyHandler;
            const game_log = document.getElementById("gameLog");
            openModal("Game Log:", game_log.innerHTML, "");
        }

        function descriptionSubModalKeyHandler(event) {
            if (event.code === "Escape") {
                closeModal();
            }
        }

        function descriptionSubModalClickHandler(event) {
            // TODO: handle clicking on items?
        }

        function openDescriptionSubModal(header, html, footer) {
            modalClickHandler = descriptionSubModalClickHandler;
            modalKeyHandler = descriptionSubModalKeyHandler;
            openSubModal(header, html, footer);
        }

        function requestRefresh(full=false) {
            if (ws.readyState === 1) {
                let refresh = new Uint8Array(2);
                refresh[0] = socket_events.ToServer.RefreshGraphics;
                refresh[1] = full ? 1 : 0;
                ws.send(refresh);
            }
        }

        function notifyModalClosed() {
            if (ws.readyState === 1) {
                let msg = new Uint8Array(1);
                msg[0] = socket_events.ToServer.ModalWasClosed;
                ws.send(msg);
            }
        }

        function notifySubModalClosed() {
            if (ws.readyState === 1) {
                let msg = new Uint8Array(1);
                msg[0] = socket_events.ToServer.SubModalWasClosed;
                ws.send(msg);
            }
        }
    };
}());
