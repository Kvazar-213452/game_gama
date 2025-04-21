import pygame
import random
import time

class CardManager:
    def __init__(self):
        self.card_options = ["def_random", "heal"]
        self.generated_cards = []
        self.last_card_time = time.time()
        self.card_interval = 15
        self.card_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.timer_font = pygame.font.SysFont('Arial', 20, bold=True)
        self.max_cards = 3
        
        self.explosion_radius = 0
        self.max_explosion_radius = 150
        self.explosion_speed = 5
        self.is_exploding = False
        self.explosion_pos = (0, 0)
        self.explosion_color = (255, 165, 0)

    def generate_random_card(self):
        if len(self.generated_cards) >= self.max_cards:
            self.generated_cards.pop(0)
        
        card = random.choice(self.card_options)
        self.generated_cards.append(card)
        return card

    def update_cards(self):
        current_time = time.time()
        if current_time - self.last_card_time >= self.card_interval:
            self.generate_random_card()
            self.last_card_time = current_time
            
        if self.is_exploding:
            self.explosion_radius += self.explosion_speed
            if self.explosion_radius >= self.max_explosion_radius:
                self.is_exploding = False
                self.explosion_radius = 0

    def get_remaining_time(self):
        elapsed = time.time() - self.last_card_time
        return max(0, self.card_interval - elapsed)

    def draw_cards_and_timer(self, screen):
        button_width = 150
        button_height = 40
        margin = 10
        
        for i, card in enumerate(reversed(self.generated_cards)):
            if card == "heal":
                color = (0, 200, 0)
            else:
                color = (200, 200, 0)
            
            button_x = screen.get_width() - button_width - margin
            button_y = screen.get_height() - (button_height + margin) * (i + 1)
            
            pygame.draw.rect(screen, color, (button_x, button_y, button_width, button_height))
            pygame.draw.rect(screen, (255, 255, 255), (button_x, button_y, button_width, button_height), 2)
            
            text = self.card_font.render(card, True, (255, 255, 255))
            text_rect = text.get_rect(center=(button_x + button_width/2, button_y + button_height/2))
            screen.blit(text, text_rect)
            
        if self.is_exploding:
            pygame.draw.circle(screen, self.explosion_color, self.explosion_pos, self.explosion_radius, 2)
            pygame.draw.circle(screen, (255, 69, 0), self.explosion_pos, self.explosion_radius//2, 2)

    def handle_card_click(self, mouse_pos, screen_width, screen_height, player_id, network, player_rect=None):
        button_width = 150
        button_height = 40
        margin = 10
        
        for i, card in enumerate(self.generated_cards[:]):
            button_x = screen_width - button_width - margin
            button_y = screen_height - (button_height + margin) * (len(self.generated_cards) - i)
            
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            if button_rect.collidepoint(mouse_pos):
                if card == "heal":
                    heal_msg = {
                        "type": "use_card",
                        "card": "heal",
                        "player_id": player_id
                    }
                    network.send(heal_msg)
                    self.generated_cards.remove(card)
                elif card == "def_random":
                    def_random_msg = {
                        "type": "use_card",
                        "card": "def_random",
                        "player_id": player_id
                    }
                    network.send(def_random_msg)
                    self.generated_cards.remove(card)
                break