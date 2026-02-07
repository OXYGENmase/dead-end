"""Wave management system"""
import random
from typing import List, Dict, Optional
from config import WAVES
from game.entities.enemy import create_enemy, Enemy


class WaveManager:
    """Manages spawning enemies in waves"""
    
    def __init__(self, grid):
        self.grid = grid
        self.waves = WAVES
        self.current_wave = 0
        
        # Spawning state
        self.spawning = False
        self.spawn_queue: List[str] = []  # Enemy types to spawn
        self.spawn_timer = 0
        self.spawn_delay = 1000  # ms between spawns
        self.last_spawn_time = 0
        
        # Active enemies
        self.enemies: List[Enemy] = []
        
        # Wave state
        self.wave_in_progress = False
        self.wave_start_time = 0
    
    def start_wave(self) -> bool:
        """Start the next wave, returns False if no more waves"""
        if self.current_wave >= len(self.waves):
            return False
        
        wave_def = self.waves[self.current_wave]
        
        # Build spawn queue
        self.spawn_queue = []
        for _ in range(wave_def["walkers"]):
            self.spawn_queue.append("walker")
        for _ in range(wave_def["runners"]):
            self.spawn_queue.append("runner")
        
        # Shuffle for variety
        random.shuffle(self.spawn_queue)
        
        self.spawn_delay = wave_def["delay"]
        self.spawning = True
        self.wave_in_progress = True
        self.wave_start_time = 0  # Will be set on first update
        self.current_wave += 1
        
        return True
    
    def update(self, dt: float, current_time: int) -> dict:
        """
        Update wave manager.
        Returns dict with events: {"enemy_spawned": Enemy, "wave_complete": bool, "all_complete": bool}
        """
        events = {
            "enemy_spawned": None,
            "wave_complete": False,
            "all_complete": False
        }
        
        if not self.wave_in_progress:
            return events
        
        # Set wave start time on first update
        if self.wave_start_time == 0:
            self.wave_start_time = current_time
        
        # Spawn enemies
        if self.spawning and self.spawn_queue:
            if current_time - self.last_spawn_time >= self.spawn_delay:
                enemy_type = self.spawn_queue.pop(0)
                path = self.grid.get_path()
                if path:
                    enemy = create_enemy(enemy_type, path, self.grid)
                    self.enemies.append(enemy)
                    events["enemy_spawned"] = enemy
                self.last_spawn_time = current_time
                
                # Check if done spawning
                if not self.spawn_queue:
                    self.spawning = False
        
        # Update all enemies
        for enemy in self.enemies[:]:
            enemy.update(dt)
            
            if not enemy.alive:
                if enemy.reached_end:
                    events["enemy_reached_end"] = enemy
                else:
                    events["enemy_killed"] = enemy
                self.enemies.remove(enemy)
        
        # Check wave complete (all spawned and all dead)
        if not self.spawning and not self.enemies:
            self.wave_in_progress = False
            events["wave_complete"] = True
            
            # Check if all waves done
            if self.current_wave >= len(self.waves):
                events["all_complete"] = True
        
        return events
    
    def get_enemies(self) -> List[Enemy]:
        """Get all active enemies"""
        return self.enemies
    
    def reset(self):
        """Reset for new game"""
        self.current_wave = 0
        self.spawning = False
        self.spawn_queue = []
        self.enemies = []
        self.wave_in_progress = False
        self.wave_start_time = 0
