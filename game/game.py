"""Main game"""
import pygame
import sys
from enum import Enum, auto
from typing import Optional

from config import *
from game.grid import Grid
from game.systems.economy import Economy
from game.systems.wave_manager import WaveManager
from game.entities.tower import create_tower
from game.entities.projectile import Projectile
from game.ui.hud import HUD
from game.ui.menus import MainMenu, PauseMenu, GameOverMenu
from game.systems.debugger import GameDebugger


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    BUILD_PHASE = auto()
    WAVE_PHASE = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class Game:
    
    def __init__(self):
        pygame.init()
        
        # Setup display (borderless window)
        self.info = pygame.display.Info()
        self.screen_width = self.info.current_w
        self.screen_height = self.info.current_h
        
        if FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (self.screen_width, self.screen_height),
                pygame.NOFRAME
            )
        else:
            self.screen = pygame.display.set_mode(
                (1280, 720)
            )
            self.screen_width = 1280
            self.screen_height = 720
        
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Adjust grid offset for screen size
        self._adjust_layout()
        
        # Game systems
        self.grid: Optional[Grid] = None
        self.economy: Optional[Economy] = None
        self.wave_manager: Optional[WaveManager] = None
        self.hud: Optional[HUD] = None
        
        # Menus
        self.main_menu = MainMenu(self.screen_width, self.screen_height)
        self.pause_menu: Optional[PauseMenu] = None
        self.game_over_menu: Optional[GameOverMenu] = None
        
        # State
        self.state = GameState.MENU
        self.selected_tower_type: Optional[str] = None
        self.hover_grid_pos: Optional[tuple] = None
        
        # Projectiles
        self.projectiles: List[Projectile] = []
        
        # Debugger
        self.debugger: Optional[GameDebugger] = None
        
        # Input handling
        self.keys_pressed = set()
        self.mouse_pressed = [False, False, False]  # Left, Middle, Right
    
    def _adjust_layout(self):
        global GRID_OFFSET_X, GRID_OFFSET_Y, TILE_SIZE
        
        # HUD takes bottom 140px
        hud_height = 140
        available_height = self.screen_height - hud_height - 40  # 20px margin top+bottom
        available_width = self.screen_width - 40  # 20px margin each side
        
        # Calculate max tile size that fits
        max_tile_w = available_width // GRID_WIDTH
        max_tile_h = available_height // GRID_HEIGHT
        
        # Use smaller of the two, cap at 48px (not too huge)
        TILE_SIZE = min(max_tile_w, max_tile_h, 48)
        # But keep minimum readable size
        TILE_SIZE = max(TILE_SIZE, 24)
        
        # Recalculate grid size with new tile size
        grid_pixel_width = GRID_WIDTH * TILE_SIZE
        grid_pixel_height = GRID_HEIGHT * TILE_SIZE
        
        # Center horizontally, position above HUD vertically
        GRID_OFFSET_X = (self.screen_width - grid_pixel_width) // 2
        GRID_OFFSET_Y = 20  # Small top margin
        
        # Ensure minimum margins
        GRID_OFFSET_X = max(20, GRID_OFFSET_X)
    
    def new_game(self):
        self.grid = Grid()
        
        # Apply calculated layout to grid
        self.grid.tile_size = TILE_SIZE
        self.grid.offset_x = GRID_OFFSET_X
        self.grid.offset_y = GRID_OFFSET_Y
        
        # Recalculate tower positions with new layout
        for (gx, gy), tower in self.grid.towers.items():
            tower.set_position(*self.grid.grid_to_screen(gx, gy))
        
        self.economy = Economy()
        self.wave_manager = WaveManager(self.grid)
        self.hud = HUD(self.screen_width, self.screen_height)
        
        self.state = GameState.BUILD_PHASE
        self.selected_tower_type = None
        self.hover_grid_pos = None
        self.projectiles = []
        
        self.pause_menu = PauseMenu(self.screen_width, self.screen_height)
        self.game_over_menu = None
        
        # Initialize debugger
        self.debugger = GameDebugger(self)
    
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            current_time = pygame.time.get_ticks()
            
            self._handle_events()
            self._update(dt, current_time)
            self._draw()
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._handle_escape()
                elif event.key == pygame.K_SPACE:
                    self._handle_space()
                elif event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                elif event.key == pygame.K_F3:
                    self._toggle_debug()
                elif event.key == pygame.K_F5:
                    self._capture_debug_screenshot()
                elif event.key == pygame.K_F6:
                    self._export_debug_snapshot()
                
                # Menu keyboard navigation
                if self.state in [GameState.MENU, GameState.PAUSED, GameState.GAME_OVER, GameState.VICTORY]:
                    self._handle_menu_key(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_click(event.pos)
                elif event.button == 3:  # Right click
                    self.selected_tower_type = None  # Cancel selection
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_move(event.pos)
    
    def _handle_escape(self):
        if self.state == GameState.PLAYING or self.state == GameState.BUILD_PHASE or self.state == GameState.WAVE_PHASE:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.BUILD_PHASE if not self.wave_manager.wave_in_progress else GameState.WAVE_PHASE
    
    def _handle_space(self):
        if self.state == GameState.BUILD_PHASE:
            self._start_wave()
    
    def _toggle_fullscreen(self):
        global FULLSCREEN
        FULLSCREEN = not FULLSCREEN
        
        if FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (self.info.current_w, self.info.current_h),
                pygame.NOFRAME
            )
            self.screen_width = self.info.current_w
            self.screen_height = self.info.current_h
        else:
            self.screen = pygame.display.set_mode((1280, 720))
            self.screen_width = 1280
            self.screen_height = 720
        
        self._adjust_layout()
        self._rebuild_menus()
    
    def _toggle_debug(self):
        if self.debugger:
            enabled = self.debugger.toggle()
            print(f"Debug overlay: {'ON' if enabled else 'OFF'}")
    
    def _capture_debug_screenshot(self):
        if self.debugger:
            filepath = self.debugger.capture_screenshot()
            print(f"Screenshot saved: {filepath}")
            if self.hud:
                self.hud.add_message("Screenshot captured!", (100, 255, 100))
    
    def _export_debug_snapshot(self):
        if self.debugger:
            filepath = self.debugger.export_full_snapshot()
            print(f"Snapshot exported: {filepath}")
            if self.hud:
                self.hud.add_message("Snapshot exported!", (100, 255, 100))
    
    def _rebuild_menus(self):
        self.main_menu = MainMenu(self.screen_width, self.screen_height)
        if self.pause_menu:
            self.pause_menu = PauseMenu(self.screen_width, self.screen_height)
        if self.game_over_menu:
            won = self.state == GameState.VICTORY
            self.game_over_menu = GameOverMenu(self.screen_width, self.screen_height, won)
    
    def _handle_menu_key(self, key: int):
        menu = None
        if self.state == GameState.MENU:
            menu = self.main_menu
        elif self.state == GameState.PAUSED:
            menu = self.pause_menu
        elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
            menu = self.game_over_menu
        
        if menu:
            action = menu.handle_key(key)
            if action:
                self._handle_menu_action(action)
    
    def _handle_click(self, pos: tuple):
        if self.state == GameState.MENU:
            action = self.main_menu.handle_click(pos)
            if action:
                self._handle_menu_action(action)
        
        elif self.state == GameState.PAUSED:
            action = self.pause_menu.handle_click(pos)
            if action:
                self._handle_menu_action(action)
        
        elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
            action = self.game_over_menu.handle_click(pos)
            if action:
                self._handle_menu_action(action)
        
        elif self.state in [GameState.BUILD_PHASE, GameState.WAVE_PHASE]:
            # Check HUD buttons
            tower_type = self.hud.get_hovered_tower(pos)
            if tower_type:
                self.selected_tower_type = tower_type
                return
            
            # Check grid placement
            if self.selected_tower_type and self.hover_grid_pos:
                self._place_tower(*self.hover_grid_pos)
    
    def _handle_menu_action(self, action: str):
        if action == "new_game" or action == "restart":
            self.new_game()
        elif action == "resume":
            self.state = GameState.BUILD_PHASE if not self.wave_manager.wave_in_progress else GameState.WAVE_PHASE
        elif action == "main_menu":
            self.state = GameState.MENU
        elif action == "quit":
            self.running = False
    
    def _handle_mouse_move(self, pos: tuple):
        if self.grid:
            self.hover_grid_pos = self.grid.screen_to_grid(*pos)
    
    def _place_tower(self, gx: int, gy: int):
        if not self.selected_tower_type:
            return
        
        tower_stats = TOWERS[self.selected_tower_type]
        cost = tower_stats["cost"]
        
        if not self.economy.can_afford(cost):
            self.hud.add_message("Not enough money!", (255, 100, 100))
            if self.debugger:
                self.debugger.log_event("placement_failed", {"reason": "no_money", "cost": cost, "money": self.economy.money})
            return
        
        if not self.grid.is_valid_placement(gx, gy):
            self.hud.add_message("Invalid placement!", (255, 100, 100))
            if self.debugger:
                self.debugger.log_event("placement_failed", {"reason": "invalid", "pos": [gx, gy]})
            return
        
        # Create and place tower
        tower = create_tower(self.selected_tower_type, gx, gy)
        tower.set_position(*self.grid.grid_to_screen(gx, gy))
        
        if self.grid.place_tower(gx, gy, self.selected_tower_type, tower):
            self.economy.spend(cost)
            self.hud.add_message(f"Placed {tower_stats['name']}", (100, 255, 100))
            if self.debugger:
                self.debugger.log_event("tower_placed", {"type": self.selected_tower_type, "pos": [gx, gy], "cost": cost})
    
    def _start_wave(self):
        if self.wave_manager.start_wave():
            self.state = GameState.WAVE_PHASE
            self.hud.add_message(f"Wave {self.wave_manager.current_wave} Started!", COLOR_WAVE)
            if self.debugger:
                wave_def = WAVES[self.wave_manager.current_wave - 1]
                self.debugger.log_event("wave_started", {"wave": self.wave_manager.current_wave, "definition": wave_def})
        else:
            # No more waves - victory!
            self.state = GameState.VICTORY
            self.game_over_menu = GameOverMenu(self.screen_width, self.screen_height, won=True)
    
    def _update(self, dt: float, current_time: int):
        # Update debugger
        if self.debugger:
            self.debugger.update(dt)
        
        if self.state in [GameState.BUILD_PHASE, GameState.WAVE_PHASE]:
            # Update HUD messages
            self.hud.update()
            
            # Update wave manager during wave phase
            if self.state == GameState.WAVE_PHASE:
                events = self.wave_manager.update(dt, current_time)
                
                # Handle events
                if events.get("enemy_killed"):
                    enemy = events["enemy_killed"]
                    self.economy.enemy_killed(enemy.reward)
                    if self.debugger:
                        self.debugger.log_event("enemy_killed", {"type": enemy.enemy_type, "reward": enemy.reward, "pos": [enemy.x, enemy.y]})
                
                if events.get("enemy_reached_end"):
                    self.economy.enemy_reached_end()
                    if self.debugger:
                        self.debugger.log_event("enemy_reached_end", {"lives_remaining": self.economy.lives})
                    if self.economy.is_game_over():
                        if self.debugger:
                            self.debugger.log_event("game_over", {"waves": self.economy.waves_completed, "kills": self.economy.enemies_killed})
                        self.state = GameState.GAME_OVER
                        self.game_over_menu = GameOverMenu(self.screen_width, self.screen_height, won=False)
                
                if events.get("wave_complete"):
                    self.economy.wave_completed()
                    self.state = GameState.BUILD_PHASE
                    self.hud.add_message("Wave Complete!", (100, 255, 100))
                    if self.debugger:
                        self.debugger.log_event("wave_complete", {"wave": self.wave_manager.current_wave})
                
                if events.get("all_complete"):
                    self.state = GameState.VICTORY
                    self.game_over_menu = GameOverMenu(self.screen_width, self.screen_height, won=True)
                    if self.debugger:
                        self.debugger.log_event("victory", {"waves": self.economy.waves_completed, "kills": self.economy.enemies_killed})
                
                # Update towers and handle projectiles
                enemies = self.wave_manager.get_enemies()
                for tower in self.grid.towers.values():
                    projectile_data = tower.update(dt, enemies, current_time)
                    if projectile_data:
                        # Create projectile from returned data
                        proj = Projectile(
                            projectile_data["x"],
                            projectile_data["y"],
                            projectile_data["target"],
                            projectile_data["damage"],
                            projectile_data["speed"],
                            projectile_data.get("type", "bullet")
                        )
                        self.projectiles.append(proj)
                
                # Update projectiles
                for proj in self.projectiles[:]:
                    proj.update(dt)
                    if not proj.alive:
                        self.projectiles.remove(proj)
    
    def _draw(self):
        self.screen.fill(COLOR_BG)
        
        if self.state == GameState.MENU:
            self.main_menu.draw(self.screen)
        
        elif self.state in [GameState.BUILD_PHASE, GameState.WAVE_PHASE, GameState.PAUSED]:
            self._draw_game()
            
            if self.state == GameState.PAUSED:
                self.pause_menu.draw(self.screen)
        
        elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
            self._draw_game()
            self.game_over_menu.draw(self.screen)
            self.game_over_menu.draw_stats(self.screen, self.economy, self.wave_manager)
        
        pygame.display.flip()
    
    def _draw_game(self):
        # Draw grid
        can_place = False
        if self.selected_tower_type and self.hover_grid_pos:
            can_place = self.grid.is_valid_placement(*self.hover_grid_pos)
        
        self.grid.draw(self.screen, self.hover_grid_pos)
        
        # Draw towers
        for tower in self.grid.towers.values():
            tower.draw(self.screen)
        
        # Draw enemies
        for enemy in self.wave_manager.get_enemies():
            enemy.draw(self.screen)
        
        # Draw projectiles
        for proj in self.projectiles:
            proj.draw(self.screen)
        
        # Draw tower preview
        if self.selected_tower_type and self.hover_grid_pos:
            self.hud.draw_tower_preview(self.screen, self.hover_grid_pos[0], 
                                       self.hover_grid_pos[1], self.selected_tower_type,
                                       can_place, self.grid)
        
        # Draw HUD
        self.hud.draw(self.screen, self.economy, self.wave_manager, self.selected_tower_type)
        
        # Draw debug visuals
        if self.debugger:
            self.debugger.draw_debug_visuals(self.screen)
        
        # Draw debug overlay (on top of everything)
        if self.debugger:
            self.debugger.draw_overlay(self.screen)
