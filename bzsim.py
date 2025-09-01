#!/usr/bin/env python3
"""
Enhanced Blandford-Znajek Black Hole Jet Simulation
Main executable file with magnetic field dynamics and energy flow visualization

This simulation visualizes relativistic plasma jets from a black hole,
including magnetic field line dynamics, Poynting flux, energy extraction,
and Kerr vs Schwarzschild comparison modes.
"""

import sys
from PyQt5 import QtWidgets

# Try to import enhanced visualizer, fallback to basic if not available
try:
    from enhanced_visualizer import EnhancedJetVisualizer as JetVisualizer
    print("Loading enhanced simulation with magnetic field dynamics...")
    ENHANCED_MODE = True
except ImportError:
    from visualizer import JetVisualizer
    print("Loading basic simulation (enhanced features not available)")
    ENHANCED_MODE = False

def main():
    """Main application entry point"""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern dark theme
    
    # Create simulation with default parameters
    DEFAULT_MASS = 10.0    # solar masses
    DEFAULT_SPIN = 0.9     # dimensionless (near-maximal rotation)
    DEFAULT_B = 1e4        # Gauss (magnetic field strength)
    
    print("=" * 60)
    print("BLANDFORD-ZNAJEK JET SIMULATION")
    print("=" * 60)
    print(f"Mode: {'Enhanced' if ENHANCED_MODE else 'Basic'}")
    print(f"Black Hole Mass: {DEFAULT_MASS:.1f} M☉")
    print(f"Spin Parameter: {DEFAULT_SPIN:.3f}")
    print(f"Magnetic Field: {DEFAULT_B:.1e} G")
    print("=" * 60)
    
    if ENHANCED_MODE:
        print("Enhanced Features Available:")
        print("• Magnetic field line dynamics with frame dragging")
        print("• Poynting flux energy transport vectors")
        print("• Energy flow arrows (rotational/magnetic/kinetic)")
        print("• Ergosphere visualization with frame dragging")
        print("• Real-time spin-dependent jet power calculation")
        print("• Kerr vs Schwarzschild comparison mode")
        print("• Interactive quality and animation controls")
        print("=" * 60)
    
    # Create and show the main window with enhanced parameters
    window = JetVisualizer(mass=DEFAULT_MASS, spin=DEFAULT_SPIN, B=DEFAULT_B)
    
    title = "Enhanced Blandford-Znajek Simulation" if ENHANCED_MODE else "Blandford-Znajek Simulation"
    window.setWindowTitle(title + " - Interactive Physics Controls")
    window.resize(1600, 900)  # Larger to accommodate enhanced controls
    window.show()
    
    print(f"Simulation started! Window size: 1600x900")
    print("Use the control panels to explore black hole physics!")
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()