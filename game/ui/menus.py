"""Menu screens - Main menu, Pause, Game Over"""
import pygame
from config import *


class Menu:
    """Base menu class"""
    
    def __init__(self, screen_width: int, screen_height: int, title: str):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title = title
        
        pygame.font.init()
        self.font_title = pygame.font.SysFont("consolas", 64, bold=True)
        self.font_button = pygame.font.SysFont("consolas", 32)
        self.font_small = pygame.font.SysFont("consolas", 20)
        
        self.buttons = []
        self.selected_index = 0
    
    def add_button(self, text: str, action: str, color: tuple = COLOR_TEXT):
        """Add a button to the menu"""
        self.buttons.append({
            "text": text,
            "action": action,
            "color": color,
            "rect": None
        })
        self._layout_buttons()
    
    def _layout_buttons(self):
        """Position buttons vertically centered"""
        button_width = 250
        button_height = 50
        spacing = 20
        total_height = len(self.buttons) * (button_height + spacing) - spacing
        start_y = (self.screen_height - total_height) // 2 + 50
        
        for i, btn in enumerate(self.buttons):
            x = (self.screen_width - button_width) // 2
            y = start_y + i * (button_height + spacing)
            btn["rect"] = pygame.Rect(x, y, button_width, button_height)
    
    def handle_click(self, pos: tuple) -> str:
        """Handle mouse click, returns action or None"""
        for btn in self.buttons:
            if btn["rect"].collidepoint(pos):
                return btn["action"]
        return None
    
    def handle_key(self, key: int) -> str:
        """Handle keyboard input"""
        if key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
        elif key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
        elif key == pygame.K_RETURN:
            return self.buttons[self.selected_index]["action"]
        elif key == pygame.K_ESCAPE:
            return "back"
        return None
    
    def draw(self, surface: pygame.Surface):
        """Draw menu"""
        # Dark background
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(200)
        surface.blit(overlay, (0, 0))
        
        # Title
        title_surf = self.font_title.render(self.title, True, (255, 255, 255))
        title_x = (self.screen_width - title_surf.get_width()) // 2
        surface.blit(title_surf, (title_x, 80))
        
        # Buttons
        for i, btn in enumerate(self.buttons):
            rect = btn["rect"]
            is_selected = i == self.selected_index
            
            # Background
            bg_color = (80, 80, 100) if is_selected else (50, 50, 60)
            pygame.draw.rect(surface, bg_color, rect, border_radius=5)
            
            # Border
            border_color = (150, 150, 200) if is_selected else (80, 80, 100)
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=5)
            
            # Text
            text_surf = self.font_button.render(btn["text"], True, btn["color"])
            text_x = rect.centerx - text_surf.get_width() // 2
            text_y = rect.centery - text_surf.get_height() // 2
            surface.blit(text_surf, (text_x, text_y))


class MainMenu(Menu):
    """Main menu screen"""
    
    def __init__(self, screen_width: int, screen_height: int):
        super().__init__(screen_width, screen_height, "DEAD END")
        self.add_button("NEW GAME", "new_game", (100, 255, 100))
        self.add_button("QUIT", "quit", (255, 100, 100))


class PauseMenu(Menu):
    """Pause menu"""
    
    def __init__(self, screen_width: int, screen_height: int):
        super().__init__(screen_width, screen_height, "PAUSED")
        self.add_button("RESUME", "resume", (100, 255, 100))
        self.add_button("RESTART", "restart", (255, 255, 100))
        self.add_button("MAIN MENU", "main_menu", (255, 100, 100))


class GameOverMenu(Menu):
    """Game over screen"""
    
    def __init__(self, screen_width: int, screen_height: int, won: bool = False):
        title = "VICTORY!" if won else "GAME OVER"
        super().__init__(screen_width, screen_height, title)
        
        if won:
            self.add_button("PLAY AGAIN", "restart", (100, 255, 100))
        else:
            self.add_button("TRY AGAIN", "restart", (255, 200, 100))
        
        self.add_button("MAIN MENU", "main_menu", (255, 255, 255))
    
    def draw_stats(self, surface: pygame.Surface, economy, wave_manager):
        """Draw game stats on game over screen"""
        y = 180
        stats = [
            f"Waves Completed: {economy.waves_completed}",
            f"Enemies Killed: {economy.enemies_killed}",
            f"Money Earned: ${economy.total_earned}",
        ]
        
        for stat in stats:
            text_surf = self.font_small.render(stat, True, (200, 200, 200))
            x = (self.screen_width - text_surf.get_width()) // 2
            surface.blit(text_surf, (x, y))
            y += 30
