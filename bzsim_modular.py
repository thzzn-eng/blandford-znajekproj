#!/usr/bin/env python3
"""
Blandford-Znajek Black Hole Jet Simulation - Modular Version
Enhanced version with organized, maintainable code structure
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from visualizer import main

if __name__ == "__main__":
    print("Starting Blandford-Znajek Jet Visualizer (Modular Version)")
    print("=" * 60)
    print("This is the refactored version with organized code modules:")
    print("- UI Controls: visualizer/ui_controls.py")
    print("- 3D Rendering: visualizer/rendering.py") 
    print("- Physics Calculations: visualizer/physics_calculations.py")
    print("- Main Application: visualizer/main_visualizer.py")
    print("=" * 60)
    
    # Run the modular visualizer
    main()
