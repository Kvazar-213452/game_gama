import pygame

class WindowManager:
    def __init__(self, default_width=800, default_height=600, title="Game Window"):
        pygame.init()
        self.default_width = default_width
        self.default_height = default_height
        self.current_width = default_width
        self.current_height = default_height
        self.title = title
        
        self.screen = pygame.display.set_mode(
            (self.current_width, self.current_height),
            pygame.RESIZABLE
        )
        pygame.display.set_caption(self.title)
        
        self.clock = pygame.time.Clock()
        self.is_fullscreen = False

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
            self.handle_resize(event)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            self.toggle_fullscreen()

    def handle_resize(self, event):
        self.current_width, self.current_height = event.w, event.h
        self.screen = pygame.display.set_mode(
            (self.current_width, self.current_height),
            pygame.RESIZABLE
        )
        return self.current_width, self.current_height

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.DOUBLEBUF
            )
            self.current_width, self.current_height = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode(
                (self.default_width, self.default_height),
                pygame.RESIZABLE
            )
            self.current_width, self.current_height = self.default_width, self.default_height

    def get_screen(self):
        return self.screen

    def get_size(self):
        return self.current_width, self.current_height

    def get_clock(self):
        return self.clock

    def update_display(self):
        pygame.display.flip()

    def quit(self):
        pygame.quit()