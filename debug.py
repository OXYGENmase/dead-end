#!/usr/bin/env python3
"""Snapshot analyzer"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List


def load_snapshot(filepath: str) -> Dict:
    """Load a snapshot JSON file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def analyze_game_state(snapshot: Dict):
    """Analyze overall game state"""
    print("\n" + "=" * 60)
    print("GAME STATE ANALYSIS")
    print("=" * 60)
    
    game = snapshot.get("game", {})
    print(f"Game State: {game.get('state', 'N/A')}")
    print(f"Frame: {game.get('frame', 'N/A')}")
    print(f"FPS: {game.get('fps', 0):.1f}")
    print(f"Selected Tower: {game.get('selected_tower', 'None')}")
    print(f"Hover Position: {game.get('hover_pos', 'N/A')}")


def analyze_economy(snapshot: Dict):
    """Analyze economy state"""
    print("\n" + "-" * 60)
    print("ECONOMY")
    print("-" * 60)
    
    econ = snapshot.get("economy", {})
    print(f"Money: ${econ.get('money', 0)}")
    print(f"Lives: {econ.get('lives', 0)}")
    print(f"Total Earned: ${econ.get('total_earned', 0)}")
    print(f"Total Spent: ${econ.get('total_spent', 0)}")
    print(f"Enemies Killed: {econ.get('enemies_killed', 0)}")
    print(f"Waves Completed: {econ.get('waves_completed', 0)}")
    
    # Efficiency metrics
    if econ.get('total_earned', 0) > 0:
        spend_ratio = econ.get('total_spent', 0) / econ.get('total_earned', 1) * 100
        print(f"Spending Efficiency: {spend_ratio:.1f}% spent")


def analyze_wave(snapshot: Dict):
    """Analyze wave state"""
    print("\n" + "-" * 60)
    print("WAVE STATUS")
    print("-" * 60)
    
    wave = snapshot.get("wave", {})
    print(f"Current Wave: {wave.get('current_wave', 0)}")
    print(f"In Progress: {wave.get('in_progress', False)}")
    print(f"Spawning: {wave.get('spawning', False)}")
    print(f"Spawn Queue: {wave.get('spawn_queue_size', 0)} remaining")
    print(f"Enemies Alive: {wave.get('enemies_alive', 0)}")


def analyze_towers(snapshot: Dict):
    """Analyze tower placement and stats"""
    print("\n" + "-" * 60)
    print("TOWERS")
    print("-" * 60)
    
    towers = snapshot.get("towers", [])
    grid = snapshot.get("grid", {})
    
    print(f"Total Towers: {len(towers)}")
    
    if not towers:
        print("  No towers placed!")
        return
    
    # Count by type
    tower_counts = {}
    for tower in towers:
        ttype = tower.get('type', 'unknown')
        tower_counts[ttype] = tower_counts.get(ttype, 0) + 1
    
    print("\nBy Type:")
    for ttype, count in sorted(tower_counts.items()):
        print(f"  {ttype}: {count}")
    
    # Analyze coverage
    print("\nCoverage Analysis:")
    total_dps = 0
    total_range = 0
    for tower in towers:
        if tower.get('damage', 0) > 0:
            fire_rate = 1.0  # Default
            dps = tower['damage'] / 1.0  # Simplified
            total_dps += dps
            total_range += tower.get('range', 0)
    
    if towers:
        avg_range = total_range / len(towers)
        print(f"  Average Range: {avg_range:.0f} pixels")
        print(f"  Estimated Total DPS: {total_dps:.1f}")
    
    # Placement analysis
    print("\nPositions:")
    for tower in towers[:10]:  # Show first 10
        pos = tower.get('position', [0, 0])
        hp_pct = (tower.get('hp', 0) / max(1, tower.get('max_hp', 1))) * 100
        print(f"  {tower.get('type', '?')} at ({pos[0]}, {pos[1]}) - HP: {hp_pct:.0f}%")
    
    if len(towers) > 10:
        print(f"  ... and {len(towers) - 10} more")


def analyze_enemies(snapshot: Dict):
    """Analyze enemy state"""
    print("\n" + "-" * 60)
    print("ENEMIES")
    print("-" * 60)
    
    enemies = snapshot.get("enemies", [])
    
    if not enemies:
        print("  No active enemies")
        return
    
    print(f"Active Enemies: {len(enemies)}")
    
    # Group by type
    enemy_types = {}
    for enemy in enemies:
        etype = enemy.get('type', 'unknown')
        enemy_types[etype] = enemy_types.get(etype, 0) + 1
    
    print("\nBy Type:")
    for etype, count in sorted(enemy_types.items()):
        print(f"  {etype}: {count}")
    
    # Analyze positions
    print("\nEnemy Positions:")
    for enemy in enemies[:5]:
        pos = enemy.get('position', [0, 0])
        hp_pct = (enemy.get('hp', 0) / max(1, enemy.get('max_hp', 1))) * 100
        path_idx = enemy.get('path_index', 0)
        print(f"  {enemy.get('type', '?')} at ({pos[0]:.0f}, {pos[1]:.0f}) - HP: {hp_pct:.0f}%, Path: {path_idx}")
    
    if len(enemies) > 5:
        print(f"  ... and {len(enemies) - 5} more")


def analyze_path(snapshot: Dict):
    """Analyze pathfinding state"""
    print("\n" + "-" * 60)
    print("PATHFINDING")
    print("-" * 60)
    
    path = snapshot.get("path", {})
    grid = snapshot.get("grid", {})
    
    print(f"Path Length: {path.get('length', 0)} tiles")
    
    if grid:
        start = grid.get('start', [0, 0])
        end = grid.get('end', [0, 0])
        obstacles = grid.get('obstacles', [])
        
        print(f"Start: {start}")
        print(f"End: {end}")
        print(f"Obstacles: {len(obstacles)} (towers/barricades)")
        
        # Calculate path efficiency
        grid_width = grid.get('size', [30, 20])[0]
        grid_height = grid.get('size', [30, 20])[1]
        
        direct_distance = abs(end[0] - start[0]) + abs(end[1] - start[1])
        actual_path = path.get('length', 0)
        
        if direct_distance > 0:
            maze_factor = actual_path / direct_distance
            print(f"\nPath Efficiency:")
            print(f"  Direct distance: {direct_distance} tiles")
            print(f"  Actual path: {actual_path} tiles")
            print(f"  Maze factor: {maze_factor:.2f}x (higher = better maze)")


def analyze_events(snapshot: Dict):
    """Analyze recent events"""
    print("\n" + "-" * 60)
    print("RECENT EVENTS")
    print("-" * 60)
    
    events = snapshot.get("recent_events", [])
    
    if not events:
        print("  No recent events")
        return
    
    print(f"Last {len(events)} events:")
    for event in events[-20:]:  # Show last 20
        etype = event.get('type', 'unknown')
        frame = event.get('frame', 0)
        data = event.get('data', {})
        print(f"  [{frame}] {etype}: {data}")


def analyze_performance(snapshot: Dict):
    """Analyze performance metrics"""
    print("\n" + "-" * 60)
    print("PERFORMANCE")
    print("-" * 60)
    
    perf = snapshot.get("performance", {})
    print(f"Average FPS: {perf.get('avg_fps', 0):.1f}")
    print(f"Frame Count: {perf.get('frame_count', 0)}")
    print(f"Event Log Size: {perf.get('event_log_size', 0)}")


def give_recommendations(snapshot: Dict):
    """Give gameplay recommendations"""
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    towers = snapshot.get("towers", [])
    enemies = snapshot.get("enemies", [])
    wave = snapshot.get("wave", {})
    econ = snapshot.get("economy", {})
    
    recommendations = []
    
    # Tower recommendations
    if len(towers) == 0:
        recommendations.append("Place some towers! Start with Riflemen near the spawn.")
    elif len(towers) < 3:
        recommendations.append("Consider placing more towers to lengthen the maze.")
    
    # Check for barricades
    barricade_count = sum(1 for t in towers if t.get('type') == 'barricade')
    if barricade_count == 0 and len(towers) >= 2:
        recommendations.append("Try using Barricades to force longer paths.")
    
    # Wave recommendations
    if wave.get('in_progress', False):
        if len(enemies) > 5:
            recommendations.append("Many enemies incoming - check if your DPS is sufficient.")
        
        runners = sum(1 for e in enemies if e.get('type') == 'runner')
        if runners > 0:
            recommendations.append(f"{runners} Runners detected - fast towers recommended.")
    
    # Economy recommendations
    if econ.get('money', 0) > 100 and len(towers) < 5:
        recommendations.append("You have money to spend - consider upgrading or placing more towers.")
    
    # Path recommendations
    path = snapshot.get("path", {})
    if path.get('length', 0) < 40:
        recommendations.append("Your maze is short - use Barricades to create a longer path.")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    else:
        print("Your setup looks good! Keep it up.")


def main():
    if len(sys.argv) < 2:
        # List available snapshots
        debug_dir = "debug_output"
        snapshot_dir = os.path.join(debug_dir, "snapshots")
        
        if not os.path.exists(snapshot_dir):
            print("No debug_output/snapshots directory found!")
            print("Run the game with F6 to export snapshots.")
            return 1
        
        snapshots = sorted([f for f in os.listdir(snapshot_dir) if f.endswith('.json')])
        
        if not snapshots:
            print("No snapshots found!")
            print("Run the game and press F6 to export a snapshot.")
            return 1
        
        print("Available snapshots:")
        for i, snap in enumerate(snapshots[-10:], 1):  # Show last 10
            print(f"  {i}. {snap}")
        
        print(f"\nUsage: python analyze_snapshot.py <snapshot_file>")
        print(f"   or: python analyze_snapshot.py debug_output/snapshots/{snapshots[-1]}")
        return 0
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return 1
    
    try:
        snapshot = load_snapshot(filepath)
        
        print("=" * 60)
        print(f"DEAD END - Snapshot Analysis")
        print(f"File: {os.path.basename(filepath)}")
        print(f"Timestamp: {snapshot.get('timestamp', 'N/A')}")
        print("=" * 60)
        
        analyze_game_state(snapshot)
        analyze_economy(snapshot)
        analyze_wave(snapshot)
        analyze_towers(snapshot)
        analyze_enemies(snapshot)
        analyze_path(snapshot)
        analyze_events(snapshot)
        analyze_performance(snapshot)
        give_recommendations(snapshot)
        
        print("\n" + "=" * 60)
        print("Analysis complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error analyzing snapshot: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
