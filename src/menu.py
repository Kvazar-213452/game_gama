# menu.py
import pygame

class Menu:
    def __init__(self, screen_width, screen_height):
        self.is_active = False
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 36)
        self.button_color = (70, 70, 70)
        self.button_hover_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.block_color = (50, 50, 50)
        self.block_padding = 20
        
        self.update_layout(screen_width, screen_height)
        
    def update_layout(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.block_width = int(screen_width * 0.4)
        self.block_height = int(screen_height * 0.5)
        self.block_rect = pygame.Rect(
            (screen_width - self.block_width) // 2,
            (screen_height - self.block_height) // 2,
            self.block_width,
            self.block_height
        )
        
        button_width = int(self.block_width * 0.8)
        button_height = 50
        self.exit_button = pygame.Rect(
            self.block_rect.x + (self.block_width - button_width) // 2,
            self.block_rect.y + self.block_height - 100,
            button_width,
            button_height
        )
        
    def toggle(self):
        self.is_active = not self.is_active
        
    def draw(self, screen):
        if not self.is_active:
            return
            
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        pygame.draw.rect(screen, self.block_color, self.block_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.block_rect, 2)
        
        title = self.font.render("Меню гри", True, self.text_color)
        title_rect = title.get_rect(center=(self.block_rect.centerx, self.block_rect.y + 50))
        screen.blit(title, title_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        btn_color = self.button_hover_color if self.exit_button.collidepoint(mouse_pos) else self.button_color
        
        pygame.draw.rect(screen, btn_color, self.exit_button, border_radius=5)
        pygame.draw.rect(screen, (150, 150, 150), self.exit_button, 2, border_radius=5)
        
        exit_text = self.font.render("Exit", True, self.text_color)
        exit_rect = exit_text.get_rect(center=self.exit_button.center)
        screen.blit(exit_text, exit_rect)
        
    def handle_event(self, event):
        if not self.is_active:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.exit_button.collidepoint(event.pos):
                print("hhhhhh")
                return True
                
        return False