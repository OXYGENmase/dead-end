"""Projectiles"""
import pygame
import math
from typing import Optional


class Projectile:
    """A projectile fired by a tower"""
    
    def __init__(self, x: float, y: float, target, damage: float, speed: float, projectile_type: str = "bullet"):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.projectile_type = projectile_type
        
        self.alive = True
        self.radius = 4
        
        # Colors by type
        self.colors = {
            "bullet": (255, 255, 100),
            "shell": (255, 150, 50),
            "laser": (100, 255, 255),
            "rocket": (255, 100, 100)
        }
        self.color = self.colors.get(projectile_type, (255, 255, 255))
    
    def update(self, dt: float):
        if not self.alive:
            return
        
        # Target dead
        if not self.target or not self.target.alive:
            self.alive = False
            return
        
        # Direction
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 5:  # Hit
            self.target.take_damage(self.damage)
            self.alive = False
            return
        
        # Move
        if dist > 0:
            move_dist = self.speed * 60 * dt  # Speed is in pixels per second
            if move_dist >= dist:
                self.x = self.target.x
                self.y = self.target.y
            else:
                self.x += (dx / dist) * move_dist
                self.y += (dy / dist) * move_dist
    
    def draw(self, surface: pygame.Surface):
        if not self.alive:
            return
        
        pos = (int(self.x), int(self.y))
        
        # Bullet
        pygame.draw.circle(surface, self.color, pos, self.radius)
        pygame.draw.circle(surface, (255, 255, 255), pos, self.radius, 1)
        
        # Trail
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                trail_length = min(15, dist)
                trail_x = self.x - (dx / dist) * trail_length
                trail_y = self.y - (dy / dist) * trail_length
                pygame.draw.line(surface, (*self.color[:3], 128), 
                               (trail_x, trail_y), pos, 2)
