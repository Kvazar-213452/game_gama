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
        self.leaderboard = []
        self.network.start_receive_thread(self.handle_message)

        self.leaderboard_surface = None  # Поверхня для кешування топу
        self.leaderboard_dirty = True  # Прапорець для перемальовування

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
                
        elif message["type"] == "leaderboard_update":
            self.leaderboard = message["leaderboard"]
            self.leaderboard_dirty = True
        
        elif message["type"] == "hp_update":
            if message["player_id"] == getattr(self.player, 'id', None):
                self.player.hp = message["hp"]
                if message.get("is_hurt", False):
                    self.player.is_hurt = True
                    self.player.hurt_timer = self.player.hurt_duration
            elif message["player_id"] in self.other_players:
                self.other_players[message["player_id"]].hp = message["hp"]
                if message.get("is_hurt", False):
                    self.other_players[message["player_id"]].is_hurt = True
                    self.other_players[message["player_id"]].hurt_timer = self.player.hurt_duration
            
            if "attacker_id" in message:
                attacker = self.player if message["attacker_id"] == getattr(self.player, 'id', None) \
                        else self.other_players.get(message["attacker_id"])
                target = self.player if message["player_id"] == getattr(self.player, 'id', None) \
                        else self.other_players.get(message["player_id"])
                
                if attacker and target:
                    print(f"{attacker.name} attacked {target.name}! HP: {message['hp']}")
        
        elif message["type"] == "player_death":
            if message["player_id"] == getattr(self.player, 'id', None):
                self.player.die()
            elif message["player_id"] in self.other_players:
                self.other_players[message["player_id"]].die()
        
        elif message["type"] == "player_respawn":
            if message["player_id"] in self.other_players:
                self.other_players[message["player_id"]].respawn()
                self.other_players[message["player_id"]].update_from_data(message["player_data"])
        
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

            self.update_leaderboard_surface()
            

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.player and not self.player.is_jumping and self.player.is_alive:
                        self.player.jump()
                self.window.handle_event(event)
            
            current_width, current_height = self.window.get_size()
            self.camera.update_screen_size(current_width, current_height)
            
            keys = pygame.key.get_pressed()
            
            if self.player:
                if self.player.is_alive:
                    self.player.handle_input(keys)
                    self.player.update(platforms, dt)
                    
                    if self.player.is_attacking and self.player.frame == 3:
                        self.check_attack()
                    
                    self.camera.update(self.player.rect)
                    self.send_update()
                else:
                    self.player.update(platforms, dt)  # Оновлюємо таймер смерті
            
            # Get current screen surface
            screen = self.window.get_screen()
            screen.fill((30, 30, 30))
            
            for platform in platforms:
                adjusted_rect = self.camera.apply(platform)
                pygame.draw.rect(screen, (100, 100, 100), adjusted_rect)
            
            # Малюємо лише живих гравців
            for player_id, player in list(self.other_players.items()):
                if player.is_alive or player.state == "death":
                    player.draw(screen, self.camera.get_offset())
            
            if self.player and (self.player.is_alive or self.player.state == "death"):
                self.player.draw(screen, self.camera.get_offset())
                self.player.draw_ui(screen)

            self.draw_leaderboard(self.window.get_screen())
            
            self.window.update_display()

        self.network.close_connection()
        self.window.quit()

    def update_leaderboard_surface(self):
        """Оновлює поверхню з топом гравців"""
        if not self.leaderboard_dirty:
            return
            
        leaderboard_font = pygame.font.SysFont('Arial', 20, bold=True)
        surface = pygame.Surface((200, 180), pygame.SRCALPHA)
        
        title = leaderboard_font.render("Топ гравців:", True, (255, 255, 255))
        surface.blit(title, (0, 0))
        
        for i, (player_id, stats) in enumerate(self.leaderboard[:5]):
            entry = leaderboard_font.render(
                f"{i+1}. {stats['name']}: {stats['kills']}", 
                True, 
                (255, 215, 0) if i == 0 else (255, 255, 255)
            )
            surface.blit(entry, (0, 30 + i * 30))
        
        self.leaderboard_surface = surface
        self.leaderboard_dirty = False

    def draw_leaderboard(self, screen):
        """Малює кешовану поверхню з топом"""
        if self.leaderboard_surface:
            screen.blit(self.leaderboard_surface, 
                       (screen.get_width() - self.leaderboard_surface.get_width() - 20, 20))

if __name__ == "__main__":
    try:
        client = GameClient()
        client.run()
    except Exception as e:
        print(f"Client error: {e}")