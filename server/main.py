import socket
import threading
import json
import time

class GameServer:
    def __init__(self, host='localhost', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        
        self.clients = []
        self.players = {}
        self.running = True
        
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
            player_name = json.loads(name_data)["name"]
        except:
            player_name = f"Player{addr[1]%1000}"
        
        player_id = str(addr[1])
        self.players[player_id] = {
            "x": 100, 
            "y": 300, 
            "facing_right": True, 
            "state": "idle",
            "frame": 0,
            "last_update": time.time(),
            "name": player_name
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

                        elif message["type"] == "attack":
                            attacker_id = player_id
                            target_id = message["target_id"]
                            damage = message["damage"]
                            
                            if target_id in self.players:
                                self.players[target_id]["hp"] = max(0, self.players[target_id]["hp"] - damage)
                                
                                self.broadcast({
                                    "type": "hp_update",
                                    "player_id": target_id,
                                    "hp": self.players[target_id]["hp"],
                                    "attacker_id": attacker_id
                                })
                                
                                print(f"{self.players[attacker_id].get('name', 'Unknown')} атакував {
                                    self.players[target_id].get('name', 'Unknown')}! HP: {
                                    self.players[target_id]['hp']}")
                    
                    except json.JSONDecodeError:
                        print("Invalid JSON received")
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            self.remove_client(client, player_id)
    
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