"""
Developer Debug System for Dead End
Analyzes and exports game state for external analysis
"""
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import pygame


class GameDebugger:
    """
    Debug system that captures game state for analysis.
    
    Features:
    - Real-time state export to JSON
    - Debug overlay (FPS, entity counts, paths)
    - Event logging
    - Screenshot capture with metadata
    - Performance profiling
    """
    
    def __init__(self, game):
        self.game = game
        self.enabled = False
        self.debug_dir = "debug_output"
        self.ensure_debug_dir()
        
        # State tracking
        self.frame_count = 0
        self.fps_history = []
        self.last_fps_update = 0
        
        # Event log
        self.event_log: List[Dict] = []
        self.max_log_entries = 1000
        
        # Performance
        self.update_times = []
        self.draw_times = []
        
        # Analysis snapshot
        self.last_snapshot = None
        self.snapshot_requested = False
    
    def ensure_debug_dir(self):
        """Create debug output directory"""
        if not os.path.exists(self.debug_dir):
            os.makedirs(self.debug_dir)
            os.makedirs(os.path.join(self.debug_dir, "screenshots"))
            os.makedirs(os.path.join(self.debug_dir, "snapshots"))
    
    def toggle(self):
        """Toggle debug mode"""
        self.enabled = not self.enabled
        return self.enabled
    
    def log_event(self, event_type: str, data: Dict = None):
        """Log a game event"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "frame": self.frame_count,
            "type": event_type,
            "data": data or {}
        }
        self.event_log.append(entry)
        
        # Trim old entries
        if len(self.event_log) > self.max_log_entries:
            self.event_log = self.event_log[-self.max_log_entries:]
    
    def request_snapshot(self):
        """Request a full state snapshot"""
        self.snapshot_requested = True
    
    def capture_screenshot(self, filename: str = None) -> str:
        """Capture screenshot and save with metadata"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        filepath = os.path.join(self.debug_dir, "screenshots", filename)
        
        # Save screenshot
        pygame.image.save(self.game.screen, filepath)
        
        # Save metadata
        meta_filepath = filepath.replace(".png", "_meta.json")
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "frame": self.frame_count,
            "game_state": self.game.state.name if hasattr(self.game.state, 'name') else str(self.game.state),
            "wave": self.game.wave_manager.current_wave if self.game.wave_manager else 0,
            "money": self.game.economy.money if self.game.economy else 0,
            "lives": self.game.economy.lives if self.game.economy else 0,
            "enemies_alive": len(self.game.wave_manager.enemies) if self.game.wave_manager else 0,
            "towers_placed": len(self.game.grid.towers) if self.game.grid else 0
        }
        
        with open(meta_filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.log_event("screenshot_captured", {"file": filename, "meta": metadata})
        return filepath
    
    def export_full_snapshot(self) -> str:
        """Export complete game state to JSON"""
        if not self.game.grid:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snapshot_{timestamp}.json"
        filepath = os.path.join(self.debug_dir, "snapshots", filename)
        
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "frame": self.frame_count,
            "game": self._get_game_state(),
            "grid": self._get_grid_state(),
            "economy": self._get_economy_state(),
            "wave": self._get_wave_state(),
            "towers": self._get_tower_states(),
            "enemies": self._get_enemy_states(),
            "path": self._get_path_state(),
            "performance": self._get_performance_state(),
            "recent_events": self.event_log[-50:]  # Last 50 events
        }
        
        with open(filepath, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        self.last_snapshot = snapshot
        self.log_event("snapshot_exported", {"file": filename})
        return filepath
    
    def _get_game_state(self) -> Dict:
        """Get general game state"""
        return {
            "state": self.game.state.name if hasattr(self.game.state, 'name') else str(self.game.state),
            "screen_size": [self.game.screen_width, self.game.screen_height],
            "fps": self._calculate_fps(),
            "selected_tower": self.game.selected_tower_type,
            "hover_pos": self.game.hover_grid_pos
        }
    
    def _get_grid_state(self) -> Dict:
        """Get grid state"""
        grid = self.game.grid
        return {
            "size": [grid.width, grid.height],
            "start": grid.start_pos,
            "end": grid.end_pos,
            "tower_count": len(grid.towers),
            "obstacles": list(grid.pathfinder.obstacles)
        }
    
    def _get_economy_state(self) -> Dict:
        """Get economy state"""
        econ = self.game.economy
        return {
            "money": econ.money,
            "lives": econ.lives,
            "total_earned": econ.total_earned,
            "total_spent": econ.total_spent,
            "enemies_killed": econ.enemies_killed,
            "waves_completed": econ.waves_completed
        }
    
    def _get_wave_state(self) -> Dict:
        """Get wave manager state"""
        wm = self.game.wave_manager
        return {
            "current_wave": wm.current_wave,
            "in_progress": wm.wave_in_progress,
            "spawning": wm.spawning,
            "spawn_queue_size": len(wm.spawn_queue),
            "enemies_alive": len(wm.enemies)
        }
    
    def _get_tower_states(self) -> List[Dict]:
        """Get all tower states"""
        towers = []
        for pos, tower in self.game.grid.towers.items():
            towers.append({
                "position": pos,
                "type": tower.tower_type,
                "hp": tower.hp,
                "max_hp": tower.max_hp,
                "damage": tower.damage,
                "range": tower.range,
                "has_target": tower.target is not None
            })
        return towers
    
    def _get_enemy_states(self) -> List[Dict]:
        """Get all enemy states"""
        enemies = []
        for enemy in self.game.wave_manager.enemies:
            enemies.append({
                "type": enemy.enemy_type,
                "position": [enemy.x, enemy.y],
                "hp": enemy.hp,
                "max_hp": enemy.max_hp,
                "path_index": enemy.path_index,
                "alive": enemy.alive,
                "reached_end": enemy.reached_end
            })
        return enemies
    
    def _get_path_state(self) -> Dict:
        """Get pathfinding state"""
        path = self.game.grid.current_path
        return {
            "length": len(path),
            "path": path[:20] if len(path) <= 20 else path[:10] + ["..."] + path[-10:]
        }
    
    def _get_performance_state(self) -> Dict:
        """Get performance metrics"""
        return {
            "avg_fps": sum(self.fps_history[-60:]) / max(1, len(self.fps_history[-60:])),
            "frame_count": self.frame_count,
            "event_log_size": len(self.event_log)
        }
    
    def _calculate_fps(self) -> float:
        """Calculate average FPS"""
        if len(self.fps_history) < 10:
            return 0.0
        return sum(self.fps_history[-60:]) / min(60, len(self.fps_history[-60:]))
    
    def update(self, dt: float):
        """Update debug tracking"""
        if not self.enabled:
            return
        
        self.frame_count += 1
        
        # Track FPS
        if dt > 0:
            fps = 1.0 / dt
            self.fps_history.append(fps)
            if len(self.fps_history) > 300:
                self.fps_history = self.fps_history[-300:]
        
        # Check for snapshot request
        if self.snapshot_requested:
            self.export_full_snapshot()
            self.snapshot_requested = False
    
    def draw_overlay(self, surface: pygame.Surface):
        """Draw debug overlay on screen"""
        if not self.enabled:
            return
        
        font = pygame.font.SysFont("consolas", 16)
        line_height = 18
        x = 10
        y = 10
        
        # Background for readability
        overlay_width = 280
        overlay_height = 200
        bg = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        surface.blit(bg, (5, 5))
        
        # FPS
        fps = self._calculate_fps()
        fps_color = (100, 255, 100) if fps >= 55 else (255, 255, 100) if fps >= 30 else (255, 100, 100)
        text = font.render(f"FPS: {fps:.1f}", True, fps_color)
        surface.blit(text, (x, y))
        y += line_height
        
        # Frame
        text = font.render(f"Frame: {self.frame_count}", True, (200, 200, 200))
        surface.blit(text, (x, y))
        y += line_height
        
        # Game State
        state_str = self.game.state.name if hasattr(self.game.state, 'name') else str(self.game.state)
        text = font.render(f"State: {state_str}", True, (200, 200, 200))
        surface.blit(text, (x, y))
        y += line_height
        
        # Wave
        if self.game.wave_manager:
            wm = self.game.wave_manager
            text = font.render(f"Wave: {wm.current_wave} | Enemies: {len(wm.enemies)}", True, (200, 200, 200))
            surface.blit(text, (x, y))
            y += line_height
        
        # Economy
        if self.game.economy:
            econ = self.game.economy
            text = font.render(f"${econ.money} | ♥{econ.lives} | Kills: {econ.enemies_killed}", True, (200, 200, 200))
            surface.blit(text, (x, y))
            y += line_height
        
        # Towers
        if self.game.grid:
            text = font.render(f"Towers: {len(self.game.grid.towers)}", True, (200, 200, 200))
            surface.blit(text, (x, y))
            y += line_height
        
        # Path length
        if self.game.grid:
            text = font.render(f"Path: {len(self.game.grid.current_path)} tiles", True, (200, 200, 200))
            surface.blit(text, (x, y))
            y += line_height
        
        # Debug controls hint
        y += 10
        text = font.render("[F3] Toggle  [F5] Screenshot  [F6] Snapshot", True, (150, 150, 150))
        surface.blit(text, (x, y))
    
    def draw_debug_visuals(self, surface: pygame.Surface):
        """Draw additional debug visuals (paths, ranges, etc)"""
        if not self.enabled:
            return
        
        # Draw path
        if self.game.grid and self.game.grid.current_path:
            path = self.game.grid.current_path
            if len(path) > 1:
                points = [self.game.grid.grid_to_screen(x, y) for x, y in path]
                # Draw path line
                for i in range(len(points) - 1):
                    pygame.draw.line(surface, (255, 255, 0, 128), points[i], points[i+1], 2)
                
                # Draw waypoints
                for i, (x, y) in enumerate(points):
                    if i % 5 == 0:  # Every 5th point
                        pygame.draw.circle(surface, (255, 255, 0), (int(x), int(y)), 3)
        
        # Draw tower ranges
        if self.game.grid:
            for pos, tower in self.game.grid.towers.items():
                if tower.range > 0:
                    range_surface = pygame.Surface((tower.range * 2, tower.range * 2), pygame.SRCALPHA)
                    pygame.draw.circle(range_surface, (0, 255, 255, 30), 
                                     (tower.range, tower.range), tower.range, 1)
                    surface.blit(range_surface, 
                                (tower.x - tower.range, tower.y - tower.range))
        
        # Draw enemy target lines
        if self.game.wave_manager:
            for enemy in self.game.wave_manager.enemies:
                if enemy.path_index < len(enemy.path) - 1:
                    next_pos = enemy.path[enemy.path_index + 1]
                    next_x, next_y = self.game.grid.grid_to_screen(*next_pos)
                    pygame.draw.line(surface, (255, 0, 0, 100), 
                                   (enemy.x, enemy.y), (next_x, next_y), 1)
