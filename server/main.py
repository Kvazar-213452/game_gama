import socket
import threading
import json
import time
import math
import random

class GameServer:
    def __init__(self, host='26.168.243.99', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        
        self.clients = []
        self.players = {}
        self.running = True

        self.leaderboard = {}
        
        print(f"Server started on {host}:{port}")
    
    def broadcast(self, message):
        disconnected_clients = []
        for client in self.clients:
            try:
                client.send((json.dumps(message) + '\n').encode('utf-8'))
            except:
                disconnected_clients.append(client)
        
        for client in disconnected_clients:
            self.remove_client(client)
    
    def handle_client(self, client, addr):
        print(f"New connection from {addr}")

        name_data = client.recv(1024).decode('utf-8').strip()
        try:
            player_data = json.loads(name_data)
            player_name = player_data["name"]
            player_skin = player_data.get("skin")
        except:
            player_name = f"Player{addr[1]%1000}"
            player_skin = "eblan"
        
        player_id = str(addr[1])
        self.players[player_id] = {
            "x": 100, 
            "y": 300, 
            "facing_right": True, 
            "state": "idle",
            "frame": 0,
            "last_update": time.time(),
            "name": player_name,
            "skin": player_skin
        }

        self.leaderboard[player_id] = {
            "name": player_name,
            "kills": 0,
            "deaths": 0
        }
        
        
        initial_data = {
            "type": "init",
            "player_id": player_id,
            "player_data": self.players[player_id]
        }
        client.send((json.dumps(initial_data) + '\n').encode('utf-8'))
        
        self.broadcast({
            "type": "new_player",
            "player_id": player_id,
            "player_data": self.players[player_id]
        })
        
        for other_id, other_data in self.players.items():
            if other_id != player_id:
                client.send((json.dumps({
                    "type": "new_player",
                    "player_id": other_id,
                    "player_data": other_data
                }) + '\n').encode('utf-8'))
            
        buffer = ""
        try:
            while self.running:
                data = client.recv(1024).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    try:
                        message = json.loads(message)
                        
                        if message["type"] == "update":
                            if self.players[player_id].get("is_alive", True):
                                self.players[player_id] = {
                                    **self.players[player_id],
                                    **message["player_data"],
                                    "last_update": time.time()
                                }
                                
                                self.broadcast({
                                    "type": "player_update",
                                    "player_id": player_id,
                                    "player_data": self.players[player_id]
                                })
                                
                        elif message["type"] == "use_card":
                            player_id = message["player_id"]
                            card = message["card"]
                            
                            if player_id in self.players:
                                if card == "heal":
                                    self.players[player_id]["hp"] = min(
                                        self.players[player_id].get("max_hp", 100),
                                        self.players[player_id]["hp"] + 50
                                    )
                                    
                                    self.broadcast({
                                        "type": "hp_update",
                                        "player_id": player_id,
                                        "hp": self.players[player_id]["hp"]
                                    })

                                elif card == "def_random":
                                    all_player_ids = list(self.players.keys())
                                    if all_player_ids:
                                        target_id = random.choice(all_player_ids)

                                        self.players[target_id]["hp"] = 0
                                        self.players[target_id]["is_alive"] = False
                                        self.players[target_id]["death_timer"] = 5
                                        self.players[target_id]["state"] = "death"
                                        
                                        killer_name = self.players[player_id].get("name", "Unknown")
                                        victim_name = self.players[target_id].get("name", "Unknown")
                                        
                                        if player_id == target_id:
                                            self.leaderboard[player_id]["deaths"] += 1
                                        else:
                                            self.leaderboard[player_id]["kills"] += 1
                                            self.leaderboard[target_id]["deaths"] += 1
                                        
                                        self.broadcast({
                                            "type": "leaderboard_update",
                                            "leaderboard": self.get_sorted_leaderboard()
                                        })
                                        
                                        self.broadcast({
                                            "type": "player_death",
                                            "player_id": target_id,
                                            "respawn_time": 5,
                                            "clear_cards": True
                                        })
                                        
                                        print(f"{killer_name} викорав карту 'def_random' і вбив {victim_name}!")
                                        threading.Timer(5, self.respawn_player, [target_id]).start()

                        elif message["type"] == "attack":
                            attacker_id = player_id
                            target_id = message["target_id"]
                            damage = message["damage"]
                            
                            if target_id in self.players and self.players[target_id].get("is_alive", True):
                                self.players[target_id]["hp"] = max(0, self.players[target_id]["hp"] - damage)
                                
                                if self.players[target_id]["hp"] <= 0:
                                    self.leaderboard[attacker_id]["kills"] += 1
                                    self.leaderboard[target_id]["deaths"] += 1
                                    
                                    self.broadcast({
                                        "type": "leaderboard_update",
                                        "leaderboard": self.get_sorted_leaderboard()
                                    })
                                    self.players[target_id]["is_alive"] = False
                                    self.players[target_id]["death_timer"] = 5
                                    self.players[target_id]["state"] = "death"

                                    self.broadcast({
                                        "type": "player_death",
                                        "player_id": target_id,
                                        "respawn_time": 5
                                    })
                                    
                                    threading.Timer(5, self.respawn_player, [target_id]).start()
                                else:
                                    self.players[target_id]["is_hurt"] = True
                                    self.players[target_id]["state"] = "hurt"
                                    
                                    self.broadcast({
                                        "type": "hp_update",
                                        "player_id": target_id,
                                        "hp": self.players[target_id]["hp"],
                                        "attacker_id": attacker_id,
                                        "is_hurt": True
                                    })
                                
                                print(f"{self.players[attacker_id].get('name', 'Unknown')} attacked {self.players[target_id].get('name', 'Unknown')}! HP: {self.players[target_id]['hp']}")
                    
                    except json.JSONDecodeError:
                        print("Invalid JSON received")
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            self.remove_client(client, player_id)
            
    def get_sorted_leaderboard(self):
        return sorted(self.leaderboard.items(), 
                        key=lambda x: x[1]["kills"], 
                        reverse=True)[:10]
    
    def remove_client(self, client, player_id=None):
        if client in self.clients:
            try:
                client.close()
                self.clients.remove(client)
            except:
                pass
            
            if player_id and player_id in self.players:
                try:
                    del self.players[player_id]
                    self.broadcast({
                        "type": "player_left",
                        "player_id": player_id
                    })
                    print(f"Гравець {player_id} відключився")
                except KeyError:
                    pass

    def respawn_player(self, player_id):
        if player_id in self.players:
            self.players[player_id]["is_alive"] = True
            self.players[player_id]["hp"] = 100
            self.players[player_id]["state"] = "idle"
            self.players[player_id]["frame"] = 0
            
            self.broadcast({
                "type": "player_respawn",
                "player_id": player_id,
                "player_data": self.players[player_id]
            })

    def handle_player_death(self, player_id, killer_id):
        if player_id in self.players:
            self.players[player_id]["is_alive"] = False
            self.players[player_id]["death_timer"] = 5
            self.players[player_id]["state"] = "death"
            
            if killer_id in self.leaderboard:
                self.leaderboard[killer_id]["kills"] += 1
            if player_id in self.leaderboard:
                self.leaderboard[player_id]["deaths"] += 1
            
            self.broadcast({
                "type": "player_death",
                "player_id": player_id,
                "respawn_time": 5,
                "attacker_id": killer_id,
                "clear_cards": True
            })
            
            threading.Timer(5, self.respawn_player, [player_id]).start()
    
    def start(self):
        while self.running:
            try:
                client, addr = self.server.accept()
                self.clients.append(client)
                thread = threading.Thread(target=self.handle_client, args=(client, addr))
                thread.start()
            except Exception as e:
                print(f"Server error: {e}")
                self.running = False
        
        self.server.close()

if __name__ == "__main__":
    server = GameServer()
    server.start()
