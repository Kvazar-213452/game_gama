import pygame

class LeaderboardRenderer:
    def __init__(self):
        self.leaderboard = []
        self.leaderboard_surface = None
        self.leaderboard_dirty = True
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.entry_font = pygame.font.SysFont('Arial', 20)
        self.border_color = (100, 100, 100)
        self.bg_color = (30, 30, 30, 200)
        self.highlight_color = (255, 215, 0)
        self.text_color = (240, 240, 240)
        self.width = 250
        self.padding = 15 

    def update_leaderboard(self, new_leaderboard):
        self.leaderboard = new_leaderboard
        self.leaderboard_dirty = True

    def update_surface(self):
        if not self.leaderboard_dirty:
            return
            
        num_entries = min(5, len(self.leaderboard))
        height = 60 + num_entries * 30
        
        surface = pygame.Surface((self.width, height), pygame.SRCALPHA)
        
        pygame.draw.rect(surface, self.bg_color, (0, 0, self.width, height))
        pygame.draw.rect(surface, self.border_color, (0, 0, self.width, height), 2)
        
        title = self.title_font.render("ТОП ГРАВЦІВ", True, self.text_color)
        surface.blit(title, (
            (self.width - title.get_width()) // 2,
            self.padding
        ))
        
        pygame.draw.line(
            surface, 
            self.border_color, 
            (self.padding, 45), 
            (self.width - self.padding, 45), 
            2
        )
        
        for i, (player_id, stats) in enumerate(self.leaderboard[:5]):
            place_text = self.entry_font.render(f"{i+1}.", True, self.text_color)
            surface.blit(place_text, (
                self.padding,
                50 + i * 30
            ))
            
            name_text = self.entry_font.render(stats['name'], True, 
                self.highlight_color if i == 0 else self.text_color)
            surface.blit(name_text, (
                self.padding + 30,
                50 + i * 30
            ))
            
            kills_text = self.entry_font.render(str(stats['kills']), True, 
                self.highlight_color if i == 0 else self.text_color)
            surface.blit(kills_text, (
                self.width - self.padding - kills_text.get_width(),
                50 + i * 30
            ))
        
        self.leaderboard_surface = surface
        self.leaderboard_dirty = False

    def draw(self, screen):
        if self.leaderboard_surface:
            x_pos = (screen.get_width() - self.leaderboard_surface.get_width()) // 2
            screen.blit(
                self.leaderboard_surface, 
                (x_pos, 20)
            )