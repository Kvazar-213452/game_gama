import pygame

class Camera:
    def __init__(self, screen_width, screen_height):
        self.update_screen_size(screen_width, screen_height)
        self.camera_offset = [0, 0]
    
    def update_screen_size(self, width, height):
        self.screen_width = width
        self.screen_height = height
    
    def update(self, target_rect):
        if target_rect:
            self.camera_offset[0] = self.screen_width // 2 - target_rect.centerx
            self.camera_offset[1] = self.screen_height // 2 - target_rect.centery
    
    def apply(self, rect):
        return pygame.Rect(
            rect.x + self.camera_offset[0],
            rect.y + self.camera_offset[1],
            rect.width,
            rect.height
        )
    
    def get_offset(self):
        return self.camera_offset