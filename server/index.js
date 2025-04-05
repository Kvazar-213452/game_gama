const net = require('net');
const EventEmitter = require('events');

class GameServer extends EventEmitter {
    constructor(host = '26.102.24.118', port = 5555) {
        super();
        this.server = net.createServer();
        this.clients = new Map();
        this.players = new Map();
        this.leaderboard = new Map();
        this.running = false;
        
        this.server.on('connection', (socket) => this.handleConnection(socket));
        this.server.on('error', (err) => this.handleServerError(err));
        
        this.server.listen(port, host, () => {
            console.log(`Server started on ${host}:${port}`);
            this.running = true;
        });
    }

    broadcast(message, excludeSocket = null) {
        const messageStr = JSON.stringify(message) + '\n';
        this.clients.forEach((client, socket) => {
            if (socket !== excludeSocket && socket.writable) {
                socket.write(messageStr);
            }
        });
    }

    handleConnection(socket) {
        const clientId = `${socket.remoteAddress}:${socket.remotePort}`;
        console.log(`New connection from ${clientId}`);

        let buffer = '';
        socket.setEncoding('utf8');
        
        const onData = (data) => {
            buffer += data;
            let boundary;
            while ((boundary = buffer.indexOf('\n')) !== -1) {
                const message = buffer.substring(0, boundary);
                buffer = buffer.substring(boundary + 1);
                this.handleMessage(socket, clientId, message);
            }
        };

        const onError = (err) => {
            console.log(`Client error (${clientId}):`, err);
            this.removeClient(socket, clientId);
        };

        const onClose = () => {
            this.removeClient(socket, clientId);
        };

        socket.on('data', onData);
        socket.on('error', onError);
        socket.on('close', onClose);

        // Store client with cleanup handlers
        this.clients.set(socket, {
            id: clientId,
            handlers: { onData, onError, onClose }
        });

        // Wait for initial player data
        const initTimeout = setTimeout(() => {
            if (!this.players.has(clientId)) {
                this.initializePlayer(socket, clientId, { name: `Player${Math.floor(Math.random() * 1000)}`, skin: 'default' });
            }
        }, 5000);
        
        const initialHandler = (data) => {
            try {
                const playerData = JSON.parse(data);
                clearTimeout(initTimeout);
                socket.removeListener('data', initialHandler);
                this.initializePlayer(socket, clientId, playerData);
            } catch (err) {
                console.log('Invalid initial data:', err);
            }
        };

        socket.once('data', initialHandler);
    }

    initializePlayer(socket, playerId, playerData) {
        const now = Date.now();
        const player = {
            x: 100,
            y: 300,
            facing_right: true,
            state: 'idle',
            frame: 0,
            last_update: now,
            name: playerData.name || `Player${Math.floor(Math.random() * 1000)}`,
            skin: playerData.skin || 'default',
            hp: 100,
            max_hp: 100,
            is_alive: true
        };

        this.players.set(playerId, player);
        this.leaderboard.set(playerId, {
            name: player.name,
            kills: 0,
            deaths: 0
        });

        // Send initial data to new player
        socket.write(JSON.stringify({
            type: 'init',
            player_id: playerId,
            player_data: player
        }) + '\n');

        // Notify others about new player
        this.broadcast({
            type: 'new_player',
            player_id: playerId,
            player_data: player
        }, socket);

        // Send existing players to new player
        this.players.forEach((existingPlayer, existingId) => {
            if (existingId !== playerId) {
                socket.write(JSON.stringify({
                    type: 'new_player',
                    player_id: existingId,
                    player_data: existingPlayer
                }) + '\n');
            }
        });
    }

    handleMessage(socket, playerId, message) {
        try {
            const data = JSON.parse(message);
            
            switch (data.type) {
                case 'update':
                    this.handlePlayerUpdate(playerId, data);
                    break;
                case 'use_card':
                    this.handleCardUse(playerId, data);
                    break;
                case 'attack':
                    this.handleAttack(playerId, data);
                    break;
                default:
                    console.log('Unknown message type:', data.type);
            }
        } catch (err) {
            console.log('Invalid message:', err);
        }
    }

    handlePlayerUpdate(playerId, data) {
        const player = this.players.get(playerId);
        if (player && player.is_alive) {
            const now = Date.now();
            Object.assign(player, data.player_data, { last_update: now });
            
            this.broadcast({
                type: 'player_update',
                player_id: playerId,
                player_data: player
            });
        }
    }

    handleCardUse(playerId, data) {
        const player = this.players.get(playerId);
        if (!player) return;

        switch (data.card) {
            case 'heal':
                player.hp = Math.min(player.max_hp, player.hp + 50);
                this.broadcast({
                    type: 'hp_update',
                    player_id: playerId,
                    hp: player.hp
                });
                break;

            case 'boom':
                this.handleExplosion(playerId, data);
                break;

            case 'def_random':
                this.handleRandomKill(playerId);
                break;
        }
    }

    handleExplosion(playerId, data) {
        const explosion_x = data.x;
        const explosion_y = data.y;
        const explosion_radius = 150;
        const damage = 80;

        this.broadcast({
            type: 'explosion',
            x: explosion_x,
            y: explosion_y
        });

        this.players.forEach((target, targetId) => {
            if (targetId !== playerId && target.is_alive) {
                const dx = target.x - explosion_x;
                const dy = target.y - explosion_y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance <= explosion_radius) {
                    target.hp = Math.max(0, target.hp - damage);

                    if (target.hp <= 0) {
                        this.handlePlayerDeath(targetId, playerId);
                    } else {
                        target.is_hurt = true;
                        target.state = 'hurt';
                        
                        this.broadcast({
                            type: 'hp_update',
                            player_id: targetId,
                            hp: target.hp,
                            attacker_id: playerId,
                            is_hurt: true
                        });
                    }
                }
            }
        });
    }

    handleRandomKill(playerId) {
        const playerIds = Array.from(this.players.keys());
        if (playerIds.length === 0) return;

        const targetId = playerIds[Math.floor(Math.random() * playerIds.length)];
        const target = this.players.get(targetId);
        if (!target) return;

        target.hp = 0;
        target.is_alive = false;
        target.death_timer = 5;
        target.state = 'death';

        const killerName = this.players.get(playerId)?.name || 'Unknown';
        const victimName = target.name || 'Unknown';

        if (playerId === targetId) {
            this.leaderboard.get(playerId).deaths += 1;
        } else {
            this.leaderboard.get(playerId).kills += 1;
            this.leaderboard.get(targetId).deaths += 1;
        }

        this.broadcast({
            type: 'leaderboard_update',
            leaderboard: this.getSortedLeaderboard()
        });

        this.broadcast({
            type: 'player_death',
            player_id: targetId,
            respawn_time: 5,
            clear_cards: true
        });

        console.log(`${killerName} used 'def_random' card and killed ${victimName}!`);
        setTimeout(() => this.respawnPlayer(targetId), 5000);
    }

    handleAttack(playerId, data) {
        const attackerId = playerId;
        const targetId = data.target_id;
        const damage = data.damage;
        const target = this.players.get(targetId);

        if (target && target.is_alive) {
            target.hp = Math.max(0, target.hp - damage);

            if (target.hp <= 0) {
                this.handlePlayerDeath(targetId, attackerId);
            } else {
                target.is_hurt = true;
                target.state = 'hurt';
                
                this.broadcast({
                    type: 'hp_update',
                    player_id: targetId,
                    hp: target.hp,
                    attacker_id: attackerId,
                    is_hurt: true
                });
            }

            console.log(`${this.players.get(attackerId)?.name || 'Unknown'} attacked ${target.name || 'Unknown'}! HP: ${target.hp}`);
        }
    }

    handlePlayerDeath(playerId, killerId) {
        const player = this.players.get(playerId);
        if (!player) return;

        player.is_alive = false;
        player.death_timer = 5;
        player.state = 'death';

        if (this.leaderboard.has(killerId)) {
            this.leaderboard.get(killerId).kills += 1;
        }
        if (this.leaderboard.has(playerId)) {
            this.leaderboard.get(playerId).deaths += 1;
        }

        this.broadcast({
            type: 'leaderboard_update',
            leaderboard: this.getSortedLeaderboard()
        });

        this.broadcast({
            type: 'player_death',
            player_id: playerId,
            respawn_time: 5
        });

        setTimeout(() => this.respawnPlayer(playerId), 5000);
    }

    respawnPlayer(playerId) {
        const player = this.players.get(playerId);
        if (!player) return;

        player.is_alive = true;
        player.hp = player.max_hp;
        player.state = 'idle';
        player.frame = 0;
        player.is_hurt = false;

        this.broadcast({
            type: 'player_respawn',
            player_id: playerId,
            player_data: player
        });
    }

    getSortedLeaderboard() {
        return Array.from(this.leaderboard.entries())
            .sort((a, b) => b[1].kills - a[1].kills)
            .slice(0, 10)
            .map(([id, data]) => ({ id, ...data }));
    }

    removeClient(socket, playerId) {
        if (!this.clients.has(socket)) return;

        const client = this.clients.get(socket);
        socket.removeListener('data', client.handlers.onData);
        socket.removeListener('error', client.handlers.onError);
        socket.removeListener('close', client.handlers.onClose);

        try {
            socket.destroy();
        } catch (err) {
            console.log('Error destroying socket:', err);
        }

        this.clients.delete(socket);

        if (playerId) {
            this.players.delete(playerId);
            this.broadcast({
                type: 'player_left',
                player_id: playerId
            });
            console.log(`Player ${playerId} disconnected`);
        }
    }

    handleServerError(err) {
        console.log('Server error:', err);
        this.running = false;
        this.close();
    }

    close() {
        this.running = false;
        this.clients.forEach((client, socket) => {
            this.removeClient(socket, client.id);
        });
        this.server.close();
    }
}

// Start the server
const server = new GameServer();
process.on('SIGINT', () => server.close());