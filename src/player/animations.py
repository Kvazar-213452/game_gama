import pygame

class AnimationManager:
    def __init__(self):
        self.animations = {
            "idle": {"frames": [], "count": 4},
            "walk": {"frames": [], "count": 6},
            "jump": {"frames": [], "count": 8},
            "attack": {"frames": [], "count": 6},
            "hurt": {"frames": [], "count": 4}
        }
        self.load_all_animations()
    
    def load_all_animations(self):
        try:
            self.animations["idle"]["frames"] = self.load_animation("Idle.png", 4)
            self.animations["walk"]["frames"] = self.load_animation("Walk.png", 6)
            self.animations["jump"]["frames"] = self.load_animation("Jump.png", 8)
            self.animations["attack"]["frames"] = self.load_animation("Attack.png", 6)
            self.animations["hurt"]["frames"] = self.load_animation("Hurt.png", 4)
        except Exception as e:
            print(f"Помилка завантаження анімацій: {e}")
            self.create_placeholder_animations()
    
    def load_animation(self, filename, frame_count):
        try:
            sheet = pygame.image.load(f"asets/{filename}").convert_alpha()
            return self.split_sheet(sheet, frame_count)
        except:
            print(f"Не вдалося завантажити анімацію: {filename}")
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
            self.animations[state]["frames"] = self.create_placeholder_frames(self.animations[state]["count"])
    
    def create_placeholder_frames(self, frame_count, color=(255, 0, 0)):
        frames = []
        for _ in range(frame_count):
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, (0, 0, 64, 64))
            frames.append(surf)
        return frames
    
    def get_animation(self, state):
        return self.animations.get(state, {}).get("frames", [])