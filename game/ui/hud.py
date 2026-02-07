"""HUD"""
import pygame
from config import *


class HUD:
    """In-game HUD"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        pygame.font.init()
        self.font_large = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_medium = pygame.font.SysFont("consolas", 20)
        self.font_small = pygame.font.SysFont("consolas", 14)
        
        # Compact bottom panel for tower buttons
        self.panel_height = 100
        self.panel_y = screen_height - self.panel_height
        
        # Tower buttons centered at bottom
        self.tower_buttons = []
        self._init_tower_buttons()
        
        # Messages
        self.messages = []
    
    def _init_tower_buttons(self):
        """Tower buttons centered at bottom"""
        button_width = 90
        button_height = 80
        spacing = 15
        
        tower_types = ["rifleman", "sniper", "barricade"]
        total_width = len(tower_types) * button_width + (len(tower_types) - 1) * spacing
        start_x = (self.screen_width - total_width) // 2
        
        for i, tower_type in enumerate(tower_types):
            stats = TOWERS[tower_type]
            x = start_x + i * (button_width + spacing)
            y = self.panel_y + 10
            self.tower_buttons.append({
                "rect": pygame.Rect(x, y, button_width, button_height),
                "type": tower_type,
                "name": stats["name"],
                "cost": stats["cost"],
                "color": stats["color"]
            })
    
    def add_message(self, text: str, color: tuple, duration: int = 2000):
        expire = pygame.time.get_ticks() + duration
        self.messages.append((text, color, expire))
    
    def update(self):
        current_time = pygame.time.get_ticks()
        self.messages = [(t, c, e) for t, c, e in self.messages if e > current_time]
    
    def draw(self, surface: pygame.Surface, economy, wave_manager, selected_tower: str = None):
        # Bottom panel for towers
        panel_rect = pygame.Rect(0, self.panel_y, self.screen_width, self.panel_height)
        pygame.draw.rect(surface, COLOR_UI_BG, panel_rect)
        pygame.draw.line(surface, (60, 60, 70), (0, self.panel_y), (self.screen_width, self.panel_y), 2)
        
        # Draw tower buttons
        for btn in self.tower_buttons:
            self._draw_tower_button(surface, btn, economy, selected_tower)
        
        # Draw stats (top right)
        self._draw_stats(surface, economy, wave_manager)
        
        # Draw phase indicator (top left)
        self._draw_phase(surface, wave_manager)
        
        # Draw messages (center)
        self._draw_messages(surface)
    
    def _draw_tower_button(self, surface: pygame.Surface, btn: dict, economy, selected: str):
        rect = btn["rect"]
        can_afford = economy.can_afford(btn["cost"])
        is_selected = selected == btn["type"]
        
        if is_selected:
            bg_color = (70, 110, 70)
            border_color = (120, 200, 120)
        elif can_afford:
            bg_color = (45, 45, 55)
            border_color = (80, 80, 100)
        else:
            bg_color = (35, 35, 40)
            border_color = (60, 60, 70)
        
        pygame.draw.rect(surface, bg_color, rect, border_radius=3)
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=3)
        
        # Tower icon
        pygame.draw.circle(surface, btn["color"], (rect.centerx, rect.top + 28), 18)
        pygame.draw.circle(surface, (255, 255, 255), (rect.centerx, rect.top + 28), 18, 2)
        
        # Name
        name_text = self.font_small.render(btn["name"], True, COLOR_TEXT)
        surface.blit(name_text, (rect.centerx - name_text.get_width() // 2, rect.top + 50))
        
        # Cost
        cost_color = COLOR_MONEY if can_afford else (120, 120, 120)
        cost_text = self.font_small.render(f"${btn['cost']}", True, cost_color)
        surface.blit(cost_text, (rect.centerx - cost_text.get_width() // 2, rect.top + 66))
    
    def _draw_stats(self, surface: pygame.Surface, economy, wave_manager):
        x = self.screen_width - 180
        y = 15
        
        # Money
        money_text = self.font_large.render(f"${economy.money}", True, COLOR_MONEY)
        surface.blit(money_text, (x, y))
        
        # Lives
        lives_text = self.font_large.render(f"♥{economy.lives}", True, COLOR_LIVES)
        surface.blit(lives_text, (x, y + 32))
        
        # Wave / Enemy count
        if wave_manager.wave_in_progress:
            info = f"Wave {wave_manager.current_wave} | {len(wave_manager.enemies)} enemies"
        else:
            info = f"Wave {wave_manager.current_wave} ready"
        
        info_text = self.font_medium.render(info, True, COLOR_WAVE)
        surface.blit(info_text, (x, y + 64))
    
    def _draw_phase(self, surface: pygame.Surface, wave_manager):
        x = 20
        y = 15
        
        if wave_manager.wave_in_progress:
            text = f"WAVE {wave_manager.current_wave}"
            color = COLOR_WAVE
        else:
            text = "BUILD"
            color = (100, 255, 100)
        
        phase_text = self.font_large.render(text, True, color)
        surface.blit(phase_text, (x, y))
        
        # Controls hint below
        hint = self.font_small.render("[SPACE] start  [ESC] pause  [F3] debug", True, (150, 150, 150))
        surface.blit(hint, (x, y + 35))
    
    def _draw_messages(self, surface: pygame.Surface):
        y = self.screen_height // 2 - 40
        for text, color, _ in self.messages:
            text_surf = self.font_medium.render(text, True, color)
            x = (self.screen_width - text_surf.get_width()) // 2
            surface.blit(text_surf, (x, y))
            y += 26
    
    def get_hovered_tower(self, mouse_pos: tuple) -> str:
        for btn in self.tower_buttons:
            if btn["rect"].collidepoint(mouse_pos):
                return btn["type"]
        return None
    
    def draw_tower_preview(self, surface: pygame.Surface, grid_x: int, grid_y: int, 
                          tower_type: str, can_place: bool, grid):
        if tower_type is None or grid_x is None or grid_y is None:
            return
        
        x, y = grid.grid_to_screen(grid_x, grid_y)
        color = (100, 255, 100) if can_place else (255, 100, 100)
        
        # Cell highlight
        rect = grid.get_cell_rect(grid_x, grid_y)
        pygame.draw.rect(surface, (*color, 100), rect)
        
        # Range preview
        stats = TOWERS[tower_type]
        range_pixels = stats.get("range", 0) * TILE_SIZE
        if range_pixels > 0:
            range_surf = pygame.Surface((range_pixels * 2, range_pixels * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (255, 255, 255, 40), 
                             (range_pixels, range_pixels), range_pixels)
            surface.blit(range_surf, (x - range_pixels, y - range_pixels))
