"""Grid system for Dead End"""
import pygame
import random
from typing import Tuple, Optional, Set, List
from config import *
from game.systems.pathfinder import Pathfinder


class Decoration:
    """Map decoration - loads sprite or uses fallback"""
    
    # Shared sprite cache
    _sprites = {}
    
    # Scale factors - bigger is better
    _scales = {
        "rock": 1.3,
        "rock-2-flat-boulder": 1.25,
        "bush": 1.8,
        "bush-tall": 2.0,
        "tree-stump": 1.6,
        "tree-stump2": 1.5,
        "crates": 1.4,
    }
    
    def __init__(self, gx: int, gy: int, dec_type: str):
        self.gx = gx
        self.gy = gy
        self.type = dec_type
        self.scale = self._scales.get(dec_type, 1.0)
        self.sprite = self._load_sprite(dec_type)
        
        # Fallback colors if no sprite
        self.colors = {
            "rock": (120, 120, 110),
            "bush": (60, 100, 50),
            "grass_tuft": (70, 130, 60),
        }
        self.color = self.colors.get(dec_type, (150, 150, 150))
    
    def _load_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Load sprite from assets, cache it"""
        if name in Decoration._sprites:
            return Decoration._sprites[name]
        
        try:
            path = f"assets/decorations/{name}.png"
            sprite = pygame.image.load(path).convert_alpha()
            Decoration._sprites[name] = sprite
            return sprite
        except:
            Decoration._sprites[name] = None
            return None
    
    def draw(self, surface: pygame.Surface, grid):
        x, y = grid.grid_to_screen(self.gx, self.gy)
        tile_size = grid.tile_size
        
        # Darken ground beneath decoration (smaller, circular)
        ground_r = int(tile_size * 0.4)
        ground_surf = pygame.Surface((ground_r * 2, ground_r * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(ground_surf, (0, 0, 0, 40), (0, 0, ground_r * 2, ground_r * 2))
        surface.blit(ground_surf, (int(x) - ground_r, int(y) - ground_r // 2))
        
        if self.sprite:
            # Scale sprite
            size = int(tile_size * self.scale)
            scaled = pygame.transform.scale(self.sprite, (size, size))
            
            # Different positioning for rocks vs bushes
            if "rock" in self.type:
                # Rocks sit LOW, almost embedded in ground
                rect = scaled.get_rect(center=(int(x), int(y) + size//8))
                # Smaller, tighter shadow for rocks
                shadow_w = int(tile_size * self.scale * 0.7)
                shadow_h = int(tile_size * self.scale * 0.3)
                shadow_color = (0, 0, 0, 120)
                shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surf, shadow_color, (0, 0, shadow_w, shadow_h))
                surface.blit(shadow_surf, (int(x) - shadow_w//2, int(y) + 4))
            else:
                # Bushes/trees sit higher with bigger shadow
                rect = scaled.get_rect(center=(int(x), int(y) - size//8))
                shadow_w = int(tile_size * self.scale * 0.9)
                shadow_h = int(tile_size * self.scale * 0.5)
                shadow_color = (0, 0, 0, 100)
                shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surf, shadow_color, (0, 0, shadow_w, shadow_h))
                surface.blit(shadow_surf, (int(x) - shadow_w//2, int(y) - 2))
            
            surface.blit(scaled, rect)
        else:
            # Fallback: colored circle
            pygame.draw.circle(surface, self.color, (int(x), int(y)), 12)


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
        
        # Visual decorations (1 per grid cell, blocks tower placement)
        self.decorations: List[List[Optional[Decoration]]] = [
            [None for _ in range(self.height)] for _ in range(self.width)
        ]
        self._generate_decorations()
        
        # Load tile textures (grass, dirt, concrete)
        self.tile_textures = self._load_tile_textures()
        
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
        # Can't place on decorations
        if self.decorations[gx][gy] is not None:
            return False
        
        # Check if placing here would block all paths
        test_obstacles = self.pathfinder.obstacles | {(gx, gy)}
        test_pathfinder = Pathfinder(self.width, self.height)
        test_pathfinder.set_obstacles(test_obstacles)
        
        return test_pathfinder.has_path(self.start_pos, self.end_pos)
    
    def _load_tile_textures(self) -> List[pygame.Surface]:
        """Load all tile textures"""
        textures = []
        texture_files = ["grass.png", "dirt.png", "concreate-floor-tile.png"]
        
        for filename in texture_files:
            try:
                texture = pygame.image.load(f"assets/tiles/{filename}").convert()
                textures.append(texture)
            except:
                pass
        
        return textures if textures else [None]
    
    def _generate_decorations(self):
        """Generate decorations spread out across map"""
        decor_types = ["rock", "rock-2-flat-boulder", "bush", "bush-tall", 
                      "tree-stump", "tree-stump2", "crates"]
        count = 0
        min_distance = 4  # Tiles between decorations
        
        for _ in range(300):  # Try many times
            if count >= 35:  # 35 decorations
                break
            
            gx = random.randint(0, self.width - 1)
            gy = random.randint(0, self.height - 1)
            
            # Don't place on start, end, or existing decor
            if (gx, gy) in [self.start_pos, self.end_pos]:
                continue
            if self.decorations[gx][gy] is not None:
                continue
            
            # Check distance from other decorations
            too_close = False
            for dx in range(-min_distance, min_distance + 1):
                for dy in range(-min_distance, min_distance + 1):
                    check_x, check_y = gx + dx, gy + dy
                    if 0 <= check_x < self.width and 0 <= check_y < self.height:
                        if self.decorations[check_x][check_y] is not None:
                            too_close = True
                            break
                if too_close:
                    break
            if too_close:
                continue
            
            # Test if placing here blocks path
            test_obstacles = self.pathfinder.obstacles | {(gx, gy)}
            test_pf = Pathfinder(self.width, self.height)
            test_pf.set_obstacles(test_obstacles)
            
            if not test_pf.has_path(self.start_pos, self.end_pos):
                continue
            
            dec_type = random.choice(decor_types)
            self.decorations[gx][gy] = Decoration(gx, gy, dec_type)
            self.pathfinder.add_obstacle(gx, gy)
            count += 1
    
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
        # Draw tile textures as base - randomly selected per tile
        if self.tile_textures:
            for gx in range(self.width):
                for gy in range(self.height):
                    rect = self.get_cell_rect(gx, gy)
                    # Use hash of position to pick consistent random texture
                    tex_index = (gx * 7 + gy * 13) % len(self.tile_textures)
                    texture = self.tile_textures[tex_index]
                    if texture:
                        scaled = pygame.transform.scale(texture, 
                                                        (self.tile_size, self.tile_size))
                        surface.blit(scaled, rect)
        
        # Grid border
        border_rect = pygame.Rect(
            self.offset_x - 2, self.offset_y - 2,
            self.width * self.tile_size + 4,
            self.height * self.tile_size + 4
        )
        pygame.draw.rect(surface, (80, 80, 90), border_rect, 2)
        
        for x in range(self.width):
            for y in range(self.height):
                rect = self.get_cell_rect(x, y)
                
                # Determine if we need to draw this tile
                # Let grass show through for empty tiles
                if (x, y) == self.start_pos:
                    pygame.draw.rect(surface, COLOR_START, rect)
                elif (x, y) == self.end_pos:
                    pygame.draw.rect(surface, COLOR_END, rect)
                elif self.cells[x][y] is not None:
                    # Tower - use tower's color
                    tower = self.towers.get((x, y))
                    color = tower.color if tower else COLOR_TOWER
                    pygame.draw.rect(surface, color, rect)
                elif hover_pos == (x, y):
                    # Semi-transparent hover
                    hover_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    hover_surf.fill((*COLOR_GRID_HOVER, 80))
                    surface.blit(hover_surf, rect)
                elif (x, y) in self.current_path:
                    # Path overlay on grass
                    path_surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    path_surf.fill((*COLOR_PATH, 100))
                    surface.blit(path_surf, rect)
                # else: empty tile - grass shows through, no draw
                
                # Subtle inner highlight for path tiles
                if (x, y) in self.current_path and (x, y) not in [self.start_pos, self.end_pos]:
                    inner = rect.inflate(-4, -4)
                    pygame.draw.rect(surface, (100, 90, 80), inner, 2)
        
        # Draw decorations (visual only, under towers/enemies)
        for x in range(self.width):
            for y in range(self.height):
                dec = self.decorations[x][y]
                if dec is not None:
                    dec.draw(surface, self)
