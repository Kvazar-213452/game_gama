import pygame

class PlayerRenderer:
    def __init__(self):
        self.name_font = pygame.font.SysFont('Arial', 16, bold=True)
        self.hp_font = pygame.font.SysFont('Arial', 14)
        self.state_font = pygame.font.SysFont('Arial', 14, bold=True)
        self.ui_font = pygame.font.SysFont('Arial', 24, bold=True)

    def draw_player(self, player, screen, camera_offset=(0, 0)):
        frames = player.animation_manager.get_animation(player.state)
        if not frames:
            return
            
        current_frame = frames[player.frame % len(frames)]
        if not player.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        screen.blit(current_frame, (
            player.rect.x + camera_offset[0],
            player.rect.y + camera_offset[1]
        ))

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

    def draw_player_ui(self, player, screen):
        hp_text = self.ui_font.render(f"HP: {player.hp}/{player.max_hp}", True, 
                                    (255, 50, 50) if player.hp < player.max_hp * 0.3 else (50, 255, 50))
        screen.blit(hp_text, (15, 15))
        
        if player.is_attacking:
            attack_text = self.ui_font.render("ATTACKING!", True, (255, 0, 0))
            screen.blit(attack_text, (15, 45))