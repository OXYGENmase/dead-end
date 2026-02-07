"""Enemies"""
import pygame
import math
from typing import List, Tuple, Optional
from config import *


class Enemy:
    """Base enemy class"""
    
    def __init__(self, enemy_type: str, path: List[Tuple[int, int]], grid):
        self.enemy_type = enemy_type
        self.stats = ENEMIES[enemy_type]
        self.grid = grid
        
        # Stats
        self.max_hp = self.stats["hp"]
        self.hp = self.max_hp
        self.speed = self.stats["speed"] * TILE_SIZE  # pixels per second
        self.reward = self.stats["reward"]
        
        # Visual
        self.color = self.stats["color"]
        self.radius = self.stats["radius"]
        
        # Movement
        self.path = path
        self.path_index = 0
        self.x, self.y = self._get_path_pos(0)
        
        # State
        self.alive = True
        self.reached_end = False
        self.slow_factor = 1.0  # For freezer tower
        self.slow_timer = 0
    
    def _get_path_pos(self, index: int) -> Tuple[float, float]:
        """Get screen position at path index"""
        if index >= len(self.path):
            index = len(self.path) - 1
        gx, gy = self.path[index]
        return self.grid.grid_to_screen(gx, gy)
    
    def take_damage(self, damage: float):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
    
    def apply_slow(self, factor: float, duration: float):
        self.slow_factor = factor
        self.slow_timer = duration
    
    def update(self, dt: float):
        if not self.alive or self.reached_end:
            return
        
        # Handle slow timer
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0
        
        # Move along path
        if self.path_index >= len(self.path) - 1:
            self.reached_end = True
            self.alive = False
            return
        
        # Get target position (next waypoint)
        target_x, target_y = self._get_path_pos(self.path_index + 1)
        
        # Calculate direction
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 2:  # Reached waypoint
            self.path_index += 1
            return
        
        # Move towards target
        move_dist = self.speed * self.slow_factor * dt
        if move_dist >= dist:
            self.x, self.y = target_x, target_y
            self.path_index += 1
        else:
            self.x += (dx / dist) * move_dist
            self.y += (dy / dist) * move_dist
    
    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        
        pos = (int(self.x), int(self.y))
        
        # Body
        pygame.draw.circle(surface, self.color, pos, self.radius)
        pygame.draw.circle(surface, (50, 20, 20), pos, self.radius, 2)
        
        # HP bar
        hp_ratio = max(0, self.hp / self.max_hp)
        bar_width = 20
        bar_height = 4
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 8
        
        pygame.draw.rect(surface, (50, 50, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (255, 50, 50), 
                        (bar_x, bar_y, bar_width * hp_ratio, bar_height))
        
        # Slow effect
        if self.slow_factor < 1.0:
            pygame.draw.circle(surface, (100, 200, 255), pos, self.radius + 3, 2)


class Walker(Enemy):
    def __init__(self, path: List[Tuple[int, int]], grid):
        super().__init__("walker", path, grid)


class Runner(Enemy):
    def __init__(self, path: List[Tuple[int, int]], grid):
        super().__init__("runner", path, grid)


def create_enemy(enemy_type: str, path: List[Tuple[int, int]], grid) -> Enemy:
    if enemy_type == "walker":
        return Walker(path, grid)
    elif enemy_type == "runner":
        return Runner(path, grid)
    else:
        raise ValueError(f"Unknown enemy type: {enemy_type}")
