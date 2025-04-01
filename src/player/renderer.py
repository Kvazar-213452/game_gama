import pygame
import time

class PlayerRenderer:
    def __init__(self):
        self.ui_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.name_font = pygame.font.SysFont('Arial', 16, bold=True)
        self.hp_font = pygame.font.SysFont('Arial', 14)
        self.state_font = pygame.font.SysFont('Arial', 14, bold=True)
        self.card_timer_font = pygame.font.SysFont('Arial', 18)

    def draw_player(self, player, screen, camera_offset=(0, 0)):
        if not player.is_alive and player.state != "death":
            return
            
        if player.state == "death":
            frames = player.animation_manager.get_animation("death")
            if frames and player.frame < len(frames):
                current_frame = frames[player.frame]
            else:
                return
        else:
            if player.is_hurt:
                frames = player.animation_manager.get_animation("hurt")
            else:
                frames = player.animation_manager.get_animation(player.state)
            
            if not frames:
                return
                
            current_frame = frames[player.frame % len(frames)]
        
        if not player.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        if player.is_hurt and player.frame % 2 == 0:
            current_frame = self.apply_hurt_effect(current_frame)
        
        if not player.is_alive:
            current_frame = self.apply_death_effect(current_frame)
        
        screen.blit(current_frame, (
            player.rect.x + camera_offset[0],
            player.rect.y + camera_offset[1]
        ))

        if player.is_alive:
            hp_bar_y = player.rect.y + camera_offset[1] - 40
            name_y = player.rect.y + camera_offset[1] - 80
            
            name_text = self.name_font.render(player.name, True, (255, 255, 255))
            screen.blit(name_text, (
                player.rect.centerx + camera_offset[0] - name_text.get_width()//2,
                name_y
            ))
            
            self.draw_hp_bar(player, screen, 
                            player.rect.centerx + camera_offset[0], 
                            hp_bar_y)
            
            if player.is_attacking:
                state_text = self.state_font.render("ATTACKING!", True, (255, 50, 50))
                screen.blit(state_text, (
                    player.rect.centerx + camera_offset[0] - state_text.get_width()//2,
                    name_y - 20
                ))

    def apply_death_effect(self, surface):
        death_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        death_surface.blit(surface, (0, 0))
        death_surface.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
        return death_surface

    def draw_hp_bar(self, player, screen, x, y):
        hp_width = 60
        hp_height = 8
        
        pygame.draw.rect(screen, (50, 50, 50), (x - hp_width//2, y, hp_width, hp_height))
        
        current_hp = max(0, (player.hp / player.max_hp) * hp_width)
        hp_color = (255, 0, 0) if (player.hp/player.max_hp) < 0.3 else (0, 255, 0)
        pygame.draw.rect(screen, hp_color, (x - hp_width//2, y, current_hp, hp_height))
        
        pygame.draw.rect(screen, (200, 200, 200), (x - hp_width//2, y, hp_width, hp_height), 1)
        
        hp_text = self.hp_font.render(f"{player.hp}/{player.max_hp}", True, (255, 255, 255))
        screen.blit(hp_text, (x - hp_text.get_width()//2, y - 15))

    def draw_player_ui(self, player, screen, card_manager=None):
        bar_width = 180
        bar_height = 22
        bar_x = 15
        hp_bar_y = 15
        stamina_bar_y = hp_bar_y + bar_height + 8
        border_width = 3
        
        pygame.draw.rect(screen, (40, 40, 40), (bar_x, hp_bar_y, bar_width, bar_height))
        current_hp_width = max(0, (player.hp / player.max_hp) * bar_width)
        hp_color = (255, 60, 60) if (player.hp/player.max_hp) < 0.3 else (60, 220, 60)
        pygame.draw.rect(screen, hp_color, (bar_x, hp_bar_y, current_hp_width, bar_height))
        pygame.draw.rect(screen, (220, 220, 220), (bar_x, hp_bar_y, bar_width, bar_height), border_width)

        pygame.draw.rect(screen, (25, 25, 25), (bar_x, stamina_bar_y, bar_width, bar_height))
        current_stamina_width = max(0, (player.stamina / player.max_stamina) * bar_width)
        stamina_color = (50, 180, 255) if player.stamina >= player.jerk_cost else (255, 80, 80)
        pygame.draw.rect(screen, stamina_color, (bar_x, stamina_bar_y, current_stamina_width, bar_height))
        pygame.draw.rect(screen, (220, 220, 220), (bar_x, stamina_bar_y, bar_width, bar_height), border_width)

        current_time = time.time()
        
        attack_cooldown = max(0, player.attack_delay - (current_time - player.last_attack_time))
        if attack_cooldown > 0:
            cooldown_text = self.ui_font.render(
                f"Атака: {attack_cooldown:.1f}s", 
                True, 
                (220, 220, 220)
            )
            screen.blit(cooldown_text, (bar_x, stamina_bar_y + bar_height + 10))

        if card_manager:
            card_time = max(0, card_manager.get_remaining_time())
            card_text = self.card_timer_font.render(
                f"Карта через: {int(card_time)}s", 
                True, 
                (200, 220, 255)
            )
            screen.blit(card_text, (bar_x, stamina_bar_y + bar_height + 40))

    def apply_hurt_effect(self, surface):
        hurt_surface = surface.copy()
        red_mask = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        red_mask.fill((255, 0, 0, 128))  
        hurt_surface.blit(red_mask, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return hurt_surface