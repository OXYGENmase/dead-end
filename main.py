#!/usr/bin/env python3
"""Dead End - Zombie tower defense"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.game import Game


def main():
    print("DEAD END")
    print("Controls:")
    print("  Click      - Place tower")
    print("  R-Click    - Cancel")
    print("  Space      - Start wave")
    print("  ESC        - Pause")
    print()
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
