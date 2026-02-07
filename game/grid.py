"""Grid system for Dead End"""
import pygame
from typing import Tuple, Optional, Set, List
from config import *
from game.systems.pathfinder import Pathfinder


class Grid:
    """Manages the game grid, towers, and pathfinding"""
    
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.tile_size = TILE_SIZE
        self.offset_x = GRID_OFFSET_X
        self.offset_y = GRID_OFFSET_Y
        
        # Grid cells: None = empty, "tower_id" = tower
        self.cells: List[List[Optional[str]]] = [
            [None for _ in range(self.height)] for _ in range(self.width)
        ]
        
        # Tower instances stored by position
        self.towers: dict = {}
        
        # Pathfinding
        self.pathfinder = Pathfinder(self.width, self.height)
        
        # Start and end points
        self.start_pos = (0, self.height // 2)
        self.end_pos = (self.width - 1, self.height // 2)
        
        # Current path (list of grid positions)
        self.current_path: List[Tuple[int, int]] = []
        
        self._update_path()
    
    def grid_to_screen(self, gx: int, gy: int) -> Tuple[int, int]:
        """Convert grid coordinates to screen pixels (center of tile)"""
        x = self.offset_x + gx * self.tile_size + self.tile_size // 2
        y = self.offset_y + gy * self.tile_size + self.tile_size // 2
        return (x, y)
    
    def screen_to_grid(self, sx: int, sy: int) -> Optional[Tuple[int, int]]:
        """Convert screen pixels to grid coordinates"""
        gx = (sx - self.offset_x) // self.tile_size
        gy = (sy - self.offset_y) // self.tile_size
        if 0 <= gx < self.width and 0 <= gy < self.height:
            return (gx, gy)
        return None
    
    def get_cell_rect(self, gx: int, gy: int) -> pygame.Rect:
        """Get pygame Rect for a grid cell"""
        x = self.offset_x + gx * self.tile_size
        y = self.offset_y + gy * self.tile_size
        return pygame.Rect(x, y, self.tile_size, self.tile_size)
    
    def is_valid_placement(self, gx: int, gy: int) -> bool:
        """Check if tower can be placed at position"""
        # Can't place on start/end
        if (gx, gy) == self.start_pos or (gx, gy) == self.end_pos:
            return False
        # Must be empty
        if self.cells[gx][gy] is not None:
            return False
        
        # Check if placing here would block all paths
        test_obstacles = self.pathfinder.obstacles | {(gx, gy)}
        test_pathfinder = Pathfinder(self.width, self.height)
        test_pathfinder.set_obstacles(test_obstacles)
        
        return test_pathfinder.has_path(self.start_pos, self.end_pos)
    
    def place_tower(self, gx: int, gy: int, tower_type: str, tower_instance) -> bool:
        """Place a tower on the grid"""
        if not self.is_valid_placement(gx, gy):
            return False
        
        self.cells[gx][gy] = tower_type
        self.towers[(gx, gy)] = tower_instance
        self.pathfinder.add_obstacle(gx, gy)
        self._update_path()
        return True
    
    def remove_tower(self, gx: int, gy: int) -> bool:
        """Remove a tower from the grid"""
        if self.cells[gx][gy] is None:
            return False
        
        self.cells[gx][gy] = None
        if (gx, gy) in self.towers:
            del self.towers[(gx, gy)]
        self.pathfinder.remove_obstacle(gx, gy)
        self._update_path()
        return True
    
    def _update_path(self):
        """Recalculate the optimal path"""
        self.current_path = self.pathfinder.find_path(self.start_pos, self.end_pos) or []
    
    def get_path(self) -> List[Tuple[int, int]]:
        """Get the current path from start to end"""
        return self.current_path.copy()
    
    def get_tower_at(self, gx: int, gy: int) -> Optional[object]:
        """Get tower instance at position"""
        return self.towers.get((gx, gy))
    
    def is_tower(self, gx: int, gy: int) -> bool:
        """Check if there's a tower at position"""
        return self.cells[gx][gy] is not None
    
    def draw(self, surface: pygame.Surface, hover_pos: Optional[Tuple[int, int]] = None):
        """Draw the grid"""
        for x in range(self.width):
            for y in range(self.height):
                rect = self.get_cell_rect(x, y)
                
                # Determine cell color
                if (x, y) == self.start_pos:
                    color = COLOR_START
                elif (x, y) == self.end_pos:
                    color = COLOR_END
                elif self.cells[x][y] is not None:
                    # Tower - use tower's color
                    tower = self.towers.get((x, y))
                    color = tower.color if tower else COLOR_TOWER
                elif hover_pos == (x, y):
                    color = COLOR_GRID_HOVER
                elif (x, y) in self.current_path:
                    color = COLOR_PATH
                else:
                    color = COLOR_GRID
                
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, COLOR_BG, rect, 1)
