#!/usr/bin/env python3
"""Validation tests"""

import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules import correctly"""
    print("Testing imports...")
    
    try:
        import config
        print("  [OK] config.py")
    except Exception as e:
        print(f"  [FAIL] config.py: {e}")
        return False
    
    try:
        from game.systems.pathfinder import Pathfinder
        print("  [OK] pathfinder.py")
    except Exception as e:
        print(f"  [FAIL] pathfinder.py: {e}")
        return False
    
    try:
        from game.grid import Grid
        print("  [OK] grid.py")
    except Exception as e:
        print(f"  [FAIL] grid.py: {e}")
        return False
    
    try:
        from game.systems.economy import Economy
        from game.systems.wave_manager import WaveManager
        print("  [OK] economy.py, wave_manager.py")
    except Exception as e:
        print(f"  [FAIL] systems: {e}")
        return False
    
    try:
        from game.entities.tower import Tower, create_tower
        from game.entities.enemy import Enemy, create_enemy
        print("  [OK] tower.py, enemy.py")
    except Exception as e:
        print(f"  [FAIL] entities: {e}")
        return False
    
    try:
        from game.ui.hud import HUD
        from game.ui.menus import MainMenu
        print("  [OK] hud.py, menus.py")
    except Exception as e:
        print(f"  [FAIL] ui: {e}")
        return False
    
    try:
        from game.game import Game, GameState
        print("  [OK] game.py")
    except Exception as e:
        print(f"  [FAIL] game.py: {e}")
        return False
    
    return True


def test_pathfinding():
    """Test A* pathfinding"""
    print("\nTesting pathfinding...")
    
    try:
        from game.systems.pathfinder import Pathfinder
        
        pf = Pathfinder(10, 10)
        path = pf.find_path((0, 0), (9, 9))
        
        if path and len(path) > 0:
            print(f"  [OK] Path found: {len(path)} steps")
        else:
            print("  [FAIL] No path found")
            return False
        
        # Test with obstacle
        pf.add_obstacle(5, 5)
        path2 = pf.find_path((0, 0), (9, 9))
        
        if path2 and len(path2) > 0:
            print(f"  [OK] Path around obstacle: {len(path2)} steps")
        else:
            print("  [FAIL] No path around obstacle")
            return False
        
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_grid():
    """Test grid system"""
    print("\nTesting grid...")
    
    try:
        from game.grid import Grid
        
        grid = Grid()
        print(f"  [OK] Grid created: {grid.width}x{grid.height}")
        
        # Test placement validation
        valid = grid.is_valid_placement(5, 5)
        print(f"  [OK] Placement check: {valid}")
        
        # Test path exists
        path = grid.get_path()
        print(f"  [OK] Path exists: {len(path)} steps")
        
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pygame_init():
    """Test pygame can initialize"""
    print("\nTesting Pygame...")
    
    try:
        import pygame
        pygame.init()
        
        # Try to create a display (headless might fail, that's ok)
        try:
            screen = pygame.display.set_mode((640, 480))
            pygame.display.quit()
            print("  [OK] Pygame display works")
        except:
            print("  [OK] Pygame core works (display skipped)")
        
        pygame.quit()
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def main():
    print("=" * 50)
    print("  DEAD END - Game Validation")
    print("=" * 50)
    print()
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_pathfinding()
    all_passed &= test_grid()
    all_passed &= test_pygame_init()
    
    print()
    print("=" * 50)
    if all_passed:
        print("  ALL TESTS PASSED!")
    else:
        print("  SOME TESTS FAILED!")
    print("=" * 50)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
