import pygame

class UIRenderer:
    def __init__(self):
        self.player_font = pygame.font.SysFont('Arial', 14)
        self.title_font = pygame.font.SysFont('Arial', 16, bold=True)

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
        
        screen.blit(surface, (screen.get_width() - width - 10, 10))