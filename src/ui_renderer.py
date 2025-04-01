import pygame

class UIRenderer:
    def __init__(self):
        self.fps_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.player_font = pygame.font.SysFont('Arial', 14)
        self.title_font = pygame.font.SysFont('Arial', 16, bold=True)
        
    def draw_fps(self, screen, clock):
        fps = int(clock.get_fps())
        fps_text = f"FPS: {fps}"
        
        if fps >= 50:
            color = (50, 255, 50)
        elif fps >= 30:
            color = (255, 255, 50)
        else:
            color = (255, 50, 50)
        
        fps_surface = self.fps_font.render(fps_text, True, color)
        
        pos = (10, screen.get_height() - fps_surface.get_height() - 10)
        bg_rect = pygame.Rect(
            pos[0] - 5,
            pos[1] - 2,
            fps_surface.get_width() + 10,
            fps_surface.get_height() + 4
        )
        pygame.draw.rect(screen, (30, 30, 30, 180), bg_rect)
        
        screen.blit(fps_surface, pos)

    def draw_player_list(self, screen, players, current_player_id):
        if not players:
            return
            
        width = 200
        padding = 10
        row_height = 25
        
        height = padding * 2 + 20 + len(players) * row_height

        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((30, 30, 30, 200))

        title = self.title_font.render("Гравці онлайн:", True, (255, 255, 255))
        surface.blit(title, (padding, padding))
        
        for i, (player_id, player) in enumerate(players.items()):
            y_pos = padding + 20 + i * row_height
            
            name = f"{player.name} (Ви)" if player_id == current_player_id else player.name
            name_text = self.player_font.render(name, True, (255, 255, 255))
            surface.blit(name_text, (padding, y_pos))
            
            ping_text = self.player_font.render("100ms", True, (150, 255, 150))
            surface.blit(ping_text, (width - ping_text.get_width() - padding, y_pos))
        
        screen.blit(surface, (screen.get_width() - width - 10, 10))