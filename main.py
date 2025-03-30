import pygame
from src.player.player import Player
from src.camera import Camera
from src.network_manager import NetworkManager
from src.window_manager import WindowManager

class GameClient:
    def __init__(self, host='localhost', port=5555):
        self.player_name = input("Enter your name: ")
        self.network = NetworkManager(host, port)
        
        if not self.network.connect(self.player_name):
            raise ConnectionError("Failed to connect to server")
        
        self.player = None
        self.other_players = {}
        self.running = True
        
        self.window = WindowManager(title="Multiplayer Platformer")
        screen_width, screen_height = self.window.get_size()
        
        self.camera = Camera(screen_width, screen_height)
        
        self.network.start_receive_thread(self.handle_message)

    def handle_message(self, message):
        if message["type"] == "init":
            self.player = Player(message["player_id"], 
                            message["player_data"]["x"], 
                            message["player_data"]["y"],
                            self.player_name)
            self.player.update_from_data(message["player_data"])
        
        elif message["type"] == "new_player":
            if message["player_id"] != getattr(self.player, 'id', None):
                self.other_players[message["player_id"]] = Player(
                    message["player_id"], 
                    message["player_data"]["x"], 
                    message["player_data"]["y"],
                    message["player_data"].get("name", "Player")
                )
                self.other_players[message["player_id"]].update_from_data(message["player_data"])
        
        elif message["type"] == "player_update":
            if message["player_id"] in self.other_players:
                self.other_players[message["player_id"]].update_from_data(message["player_data"])
        
        elif message["type"] == "hp_update":
            if message["player_id"] == getattr(self.player, 'id', None):
                self.player.hp = message["hp"]
            elif message["player_id"] in self.other_players:
                self.other_players[message["player_id"]].hp = message["hp"]
            
            if "attacker_id" in message:
                attacker = self.player if message["attacker_id"] == getattr(self.player, 'id', None) \
                        else self.other_players.get(message["attacker_id"])
                target = self.player if message["player_id"] == getattr(self.player, 'id', None) \
                        else self.other_players.get(message["player_id"])
                
                if attacker and target:
                    print(f"{attacker.name} attacked {target.name}! HP: {message['hp']}")
        
        elif message["type"] == "player_left":
            if message["player_id"] in self.other_players:
                del self.other_players[message["player_id"]]

    def check_attack(self):
        if not self.player or not self.player.is_attacking or self.player.frame != 3:
            return
        
        attack_range = 100
        attack_rect = pygame.Rect(
            self.player.rect.x - attack_range if not self.player.facing_right 
            else self.player.rect.x + self.player.rect.width,
            self.player.rect.y,
            attack_range,
            self.player.rect.height
        )
        
        for player_id, other_player in self.other_players.items():
            if attack_rect.colliderect(other_player.rect):
                attack_msg = {
                    "type": "attack",
                    "target_id": player_id,
                    "damage": 10
                }
                self.network.send(attack_msg)

    def send_update(self):
        if self.player:
            message = {
                "type": "update",
                "player_data": {
                    **self.player.get_data(),
                    "name": self.player.name
                }
            }
            self.network.send(message)

    def run(self):
        platforms = [
            pygame.Rect(0, 500, 300, 20),
            pygame.Rect(400, 400, 200, 20),
            pygame.Rect(200, 300, 150, 20)
        ]
        
        while self.running:
            dt = self.window.get_clock().tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.player and not self.player.is_jumping:
                        self.player.jump()
                self.window.handle_event(event)
            
            current_width, current_height = self.window.get_size()
            self.camera.update_screen_size(current_width, current_height)
            
            keys = pygame.key.get_pressed()
            
            if self.player:
                self.player.handle_input(keys)
                self.player.update(platforms)
                
                if self.player.is_attacking and self.player.frame == 3:
                    self.check_attack()
                
                self.camera.update(self.player.rect)
                self.send_update()
            
            # Get current screen surface
            screen = self.window.get_screen()
            screen.fill((30, 30, 30))
            
            for platform in platforms:
                adjusted_rect = self.camera.apply(platform)
                pygame.draw.rect(screen, (100, 100, 100), adjusted_rect)
            
            for player in self.other_players.values():
                player.draw(screen, self.camera.get_offset())
            
            if self.player:
                self.player.draw(screen, self.camera.get_offset())
                self.player.draw_ui(screen)
            
            self.window.update_display()

        self.network.close_connection()
        self.window.quit()

if __name__ == "__main__":
    try:
        client = GameClient()
        client.run()
    except Exception as e:
        print(f"Client error: {e}")