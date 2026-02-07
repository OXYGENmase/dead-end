"""Towers"""
import pygame
import math
from typing import Optional, List, Tuple
from config import *


class Tower:
    """Base tower class"""
    
    def __init__(self, grid_x: int, grid_y: int, tower_type: str, stats: dict):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.tower_type = tower_type
        self.stats = stats
        
        # Combat stats
        self.damage = stats.get("damage", 0)
        self.range = stats.get("range", 0) * TILE_SIZE  # Convert tiles to pixels
        self.fire_rate = stats.get("fire_rate", 1.0)
        self.hp = stats.get("hp", 100)
        self.max_hp = self.hp
        
        # Visual
        self.color = stats.get("color", COLOR_TOWER)
        self.radius = TILE_SIZE // 2 - 4
        
        # State
        self.last_shot_time = 0
        self.target: Optional[object] = None
        self.angle = 0  # For rotation
        
        # Position (set by grid)
        self.x = 0
        self.y = 0
    
    def set_position(self, x: int, y: int):
        """Set screen position (center of tile)"""
        self.x = x
        self.y = y
    
    def update(self, dt: float, enemies: List[object], current_time: int) -> Optional[dict]:
        """Update tower logic, returns projectile data if fired"""
        # Find target
        self.target = self._find_target(enemies)
        
        # Aim at target
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            self.angle = math.degrees(math.atan2(-dy, dx))
            
            # Shoot if ready
            if current_time - self.last_shot_time >= self.fire_rate * 1000:
                return self._shoot(current_time)
        
        return None
    
    def _find_target(self, enemies: List[object]) -> Optional[object]:
        """Find enemy within range (closest to exit or closest to tower)"""
        best_target = None
        best_dist = float('inf')
        
        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range and dist < best_dist:
                best_dist = dist
                best_target = enemy
        
        return best_target
    
    def _shoot(self, current_time: int):
        """Fire at target - override in subclasses"""
        self.last_shot_time = current_time
    
    def draw(self, surface: pygame.Surface):
        # Base
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius, 2)
        
        # Direction indicator
        if self.target and self.tower_type != "barricade":
            end_x = self.x + math.cos(math.radians(self.angle)) * (self.radius + 8)
            end_y = self.y - math.sin(math.radians(self.angle)) * (self.radius + 8)
            pygame.draw.line(surface, (255, 255, 255), (self.x, self.y), (end_x, end_y), 3)
    
    def draw_range(self, surface: pygame.Surface, alpha: int = 60):
        if self.range > 0:
            range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (255, 255, 255, alpha), 
                             (self.range, self.range), self.range)
            surface.blit(range_surface, 
                        (self.x - self.range, self.y - self.range))


class RiflemanTower(Tower):
    def __init__(self, grid_x: int, grid_y: int):
        super().__init__(grid_x, grid_y, "rifleman", TOWERS["rifleman"])
    
    def _shoot(self, current_time: int):
        self.last_shot_time = current_time
        # Return projectile data for game to create
        return {
            "type": "bullet",
            "x": self.x,
            "y": self.y,
            "target": self.target,
            "damage": self.damage,
            "speed": 8
        }


class SniperTower(Tower):
    def __init__(self, grid_x: int, grid_y: int):
        super().__init__(grid_x, grid_y, "sniper", TOWERS["sniper"])
    
    def _shoot(self, current_time: int):
        self.last_shot_time = current_time
        # Sniper hits instantly
        if self.target:
            self.target.take_damage(self.damage)
        return None  # No projectile
    
    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        # Laser line
        if self.target and self.last_shot_time > pygame.time.get_ticks() - 100:
            pygame.draw.line(surface, (255, 0, 0, 128), 
                           (self.x, self.y), 
                           (self.target.x, self.target.y), 2)


class BarricadeTower(Tower):
    def __init__(self, grid_x: int, grid_y: int):
        super().__init__(grid_x, grid_y, "barricade", TOWERS["barricade"])
        self.color = COLOR_BARricade
    
    def update(self, dt: float, enemies: List[object], current_time: int):
        pass  # Wall - no attack
    
    def draw(self, surface: pygame.Surface):
        rect = pygame.Rect(
            self.x - self.radius - 2,
            self.y - self.radius - 2,
            self.radius * 2 + 4,
            self.radius * 2 + 4
        )
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, (150, 130, 110), rect, 2)
        # HP indicator
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, (50, 50, 50), 
                        (self.x - 10, self.y - self.radius - 8, 20, 4))
        pygame.draw.rect(surface, (0, 255, 0), 
                        (self.x - 10, self.y - self.radius - 8, 20 * hp_ratio, 4))


def create_tower(tower_type: str, grid_x: int, grid_y: int) -> Tower:
    """Factory function to create towers"""
    if tower_type == "rifleman":
        return RiflemanTower(grid_x, grid_y)
    elif tower_type == "sniper":
        return SniperTower(grid_x, grid_y)
    elif tower_type == "barricade":
        return BarricadeTower(grid_x, grid_y)
    else:
        raise ValueError(f"Unknown tower type: {tower_type}")
