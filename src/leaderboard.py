import pygame

class LeaderboardRenderer:
    def __init__(self):
        self.leaderboard = []
        self.leaderboard_surface = None
        self.leaderboard_dirty = True
        self.font = pygame.font.SysFont('Arial', 20, bold=True)

    def update_leaderboard(self, new_leaderboard):
        self.leaderboard = new_leaderboard
        self.leaderboard_dirty = True

    def update_surface(self):
        if not self.leaderboard_dirty:
            return
            
        surface = pygame.Surface((200, 180), pygame.SRCALPHA)
        
        title = self.font.render("Топ гравців:", True, (255, 255, 255))
        surface.blit(title, (0, 0))
        
        for i, (player_id, stats) in enumerate(self.leaderboard[:5]):
            entry = self.font.render(
                f"{i+1}. {stats['name']}: {stats['kills']}", 
                True, 
                (255, 215, 0) if i == 0 else (255, 255, 255)
            )
            surface.blit(entry, (0, 30 + i * 30))
        
        self.leaderboard_surface = surface
        self.leaderboard_dirty = False

    def draw(self, screen):
        if self.leaderboard_surface:
            screen.blit(
                self.leaderboard_surface, 
                (screen.get_width() - self.leaderboard_surface.get_width() - 20, 20)
            )