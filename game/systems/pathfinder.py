"""A* Pathfinding for maze-based tower defense"""
import heapq
from typing import List, Tuple, Optional, Set


class Pathfinder:
    """A* pathfinding with grid obstacles"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Store obstacles as set of (x, y) tuples
        self.obstacles: Set[Tuple[int, int]] = set()
    
    def set_obstacles(self, obstacles: Set[Tuple[int, int]]):
        """Update obstacle set"""
        self.obstacles = obstacles.copy()
    
    def add_obstacle(self, x: int, y: int):
        """Add single obstacle"""
        self.obstacles.add((x, y))
    
    def remove_obstacle(self, x: int, y: int):
        """Remove single obstacle"""
        self.obstacles.discard((x, y))
    
    def is_valid(self, x: int, y: int) -> bool:
        """Check if position is within bounds and not blocked"""
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                (x, y) not in self.obstacles)
    
    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Manhattan distance heuristic"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring positions (4-directional)"""
        x, y = pos
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def find_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Find path from start to end using A*.
        Returns list of positions from start to end, or None if no path exists.
        """
        if not self.is_valid(start[0], start[1]) or not self.is_valid(end[0], end[1]):
            return None
        
        # A* algorithm
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            _, current = heapq.heappop(frontier)
            
            if current == end:
                # Reconstruct path
                path = []
                while current is not None:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]
            
            for next_pos in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(next_pos, end)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        return None  # No path found
    
    def has_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Quick check if path exists without returning full path"""
        return self.find_path(start, end) is not None
