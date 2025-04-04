import pygame
import os

class AnimationManager:
    def __init__(self, skin="eblan"):
        self.skin = skin
        self.animations = {
            "idle": {"frames": [], "count": 4},
            "walk": {"frames": [], "count": 6},
            "jump": {"frames": [], "count": 8},
            "attack": {"frames": [], "count": 6},
            "hurt": {"frames": [], "count": 4},
            "death": {"frames": [], "count": 8},
            "jerk": {"frames": [], "count": 4}
        }
        
        self.load_all_animations()
    
    def set_skin(self, skin):
        self.skin = skin
        self.load_all_animations()
    
    def load_all_animations(self):
        try:
            base_path = os.path.join("assets", self.skin)
            
            if not os.path.exists(base_path):
                raise FileNotFoundError(f"Шлях до скіна не знайдено: {base_path}")
            
            animations_to_load = {
                "idle": "Idle.png",
                "walk": "Run.png",
                "jump": "Jump.png",
                "attack": "Attack2.png",
                "hurt": "Hurt.png",
                "death": "Death.png",
                "jerk": "Squat.png"
            }
            
            for state, filename in animations_to_load.items():
                filepath = os.path.join(base_path, filename)
                if os.path.exists(filepath):
                    self.animations[state]["frames"] = self.load_animation(
                        filepath, 
                        self.animations[state]["count"]
                    )
                else:
                    print(f"Попередження: файл {filename} не знайдено для скіна {self.skin}")
                    self.animations[state]["frames"] = self.create_placeholder_frames(
                        self.animations[state]["count"]
                    )
            
        except Exception as e:
            print(f"Помилка завантаження анімацій для скіна {self.skin}: {e}")
            self.create_placeholder_animations()
    
    def load_animation(self, filepath, frame_count):
        try:
            sheet = pygame.image.load(filepath).convert_alpha()
            return self.split_sheet(sheet, frame_count)
        except Exception as e:
            print(f"Не вдалося завантажити анімацію {filepath}: {e}")
            return self.create_placeholder_frames(frame_count)
    
    def split_sheet(self, sheet, frame_count):
        frames = []
        frame_width = sheet.get_width() // frame_count
        frame_height = sheet.get_height()
        
        for i in range(frame_count):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (64, 64))
            frames.append(frame)
        return frames
    
    def create_placeholder_animations(self):
        for state in self.animations:
            self.animations[state]["frames"] = self.create_placeholder_frames(
                self.animations[state]["count"]
            )
    
    def create_placeholder_frames(self, frame_count, color=(255, 0, 0)):
        frames = []
        for i in range(frame_count):
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, (0, 0, 64, 64), 1)
            font = pygame.font.SysFont('Arial', 12)
            text = font.render(f"{self.skin[:3]}{i+1}", True, color)
            surf.blit(text, (10, 10))
            frames.append(surf)
        return frames
    
    def get_animation(self, state):
        return self.animations.get(state, {}).get("frames", [])