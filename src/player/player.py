import pygame
from src.player.animations import AnimationManager
from src.player.renderer import PlayerRenderer

class Player:
    def __init__(self, player_id, x, y, name="Player", skin="eblan"):
        self.id = player_id
        self.skin = skin
        self.name = name
        self.rect = pygame.Rect(x, y, 64, 64)
        self.velocity_y = 0
        self.velocity_x = 0
        self.speed = 5
        self.jump_power = -15
        self.gravity = 0.8
        self.is_jumping = False
        self.facing_right = True
        self.state = "idle"
        self.frame = 0
        self.last_update = 0
        self.animation_speed = 0.1
        self.hp = 100
        self.max_hp = 100
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_cooldown = 0
        self.is_hurt = False
        self.hurt_timer = 0
        self.hurt_duration = 0.5

        self.is_alive = True
        self.death_timer = 0
        self.respawn_time = 5
        self.respawn_position = (x, y)
        self.death_animation_played = False

        self.animation_manager = AnimationManager(skin)
        self.renderer = PlayerRenderer()
        self.kills = 0
        self.deaths = 0

    def add_kill(self):
        self.kills += 1

    def add_death(self):
        self.deaths += 1

    def jump(self):
        if not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True
            self.state = "jump"
            self.frame = 0

    def take_damage(self, amount):
        if not self.is_alive:
            return False
            
        self.hp = max(0, self.hp - amount)
        self.is_hurt = True
        self.hurt_timer = self.hurt_duration
        
        if self.hp <= 0:
            self.die()
            return True
        return False

    def die(self):
        self.is_alive = False
        self.death_timer = self.respawn_time
        self.state = "death"
        self.frame = 0
        self.death_animation_played = False

    def respawn(self):
        self.is_alive = True
        self.hp = self.max_hp
        self.rect.x, self.rect.y = self.respawn_position
        self.state = "idle"
        self.frame = 0
        self.death_animation_played = False

    def update_from_data(self, data):
        self.rect.x = data["x"]
        self.rect.y = data["y"]
        self.facing_right = data["facing_right"]
        self.state = data["state"]
        self.frame = data.get("frame", 0)
        self.name = data.get("name", "Player")
        self.hp = data.get("hp", 100)
        self.is_attacking = data.get("is_attacking", False)
        self.is_jumping = data.get("is_jumping", False)
        self.is_hurt = data.get("is_hurt", False)
        self.skin = data.get("skin", "eblan")  # Оновлюємо скін
        self.animation_manager.set_skin(self.skin)  # Оновлюємо анімації
    
    def get_data(self):
        return {
            "x": self.rect.x,
            "y": self.rect.y,
            "facing_right": self.facing_right,
            "state": self.state,
            "frame": self.frame,
            "name": self.name,
            "hp": self.hp,
            "is_attacking": self.is_attacking,
            "is_jumping": self.is_jumping,
            "is_hurt": self.is_hurt,
            "skin": self.skin  # Додаємо скін до даних гравця
        }

    def handle_input(self, keys):
        self.velocity_x = 0
        
        if keys[pygame.K_LEFT]:
            self.velocity_x = -self.speed
            self.facing_right = False
            if not self.is_jumping and not self.is_attacking:
                self.state = "walk"
        elif keys[pygame.K_RIGHT]:
            self.velocity_x = self.speed
            self.facing_right = True
            if not self.is_jumping and not self.is_attacking:
                self.state = "walk"
        elif not self.is_jumping and not self.is_attacking:
            self.state = "idle"
        
        if keys[pygame.K_m] and not self.is_attacking and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.state = "attack"
            self.frame = 0
            self.attack_cooldown = 30

    def update(self, platforms, dt):
        if not self.is_alive:
            if not self.death_animation_played:
                self.death_timer -= dt
                if self.death_timer <= 0:
                    self.respawn()
            return

        if self.is_hurt:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.is_hurt = False
                if self.velocity_x != 0:
                    self.state = "walk"
                else:
                    self.state = "idle"

        current_time = pygame.time.get_ticks() / 1000
        if current_time - self.last_update > self.animation_speed:
            self.last_update = current_time
            
            if self.is_hurt:
                frames = self.animation_manager.get_animation("hurt")
            else:
                frames = self.animation_manager.get_animation(self.state)
            
            if frames:
                if not (self.is_attacking and self.frame == len(frames) - 1):
                    self.frame = (self.frame + 1) % len(frames)
                
                if self.state == "attack" and self.frame == len(frames) - 1:
                    self.is_attacking = False
                    if self.velocity_x != 0:
                        self.state = "walk"
                    else:
                        self.state = "idle"
                    self.frame = 0

        if not self.is_attacking:
            self.velocity_y += self.gravity
            self.rect.x += self.velocity_x
            self.rect.y += self.velocity_y
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        self.is_jumping = True
        for platform in platforms:
            collision_rect = pygame.Rect(
                self.rect.x,
                self.rect.bottom - self.rect.height // 3,
                self.rect.width,
                self.rect.height // 3
            )
            
            if collision_rect.colliderect(platform):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.is_jumping = False
                    if self.state == "jump":
                        self.state = "idle" if self.velocity_x == 0 else "walk"
                        self.frame = 0
                elif self.velocity_y < 0:
                    self.rect.top = platform.bottom
                    self.velocity_y = 0

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        return self.hp <= 0

    def draw(self, screen, camera_offset=(0, 0)):
        self.renderer.draw_player(self, screen, camera_offset)

    def draw_ui(self, screen):
        self.renderer.draw_player_ui(self, screen)