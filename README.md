# Blandford-Znajek Black Hole Jet Simulation

A high-performance, visually stunning simulation of relativistic astrophysical jets powered by rotating black holes. Features an optimized dark-themed interface, glowing plasma effects, and realistic cosmic environments.

![Black Hole Jet Simulation](https://img.shields.io/badge/Physics-Relativistic%20Jets-blue) ![Performance](https://img.shields.io/badge/Performance-Optimized-green) ![UI](https://img.shields.io/badge/UI-Dark%20Theme-black)

## ✨ Key Features

### 🌌 **Realistic Cosmic Environment**
- **3000+ Star Field** - Procedurally generated cosmic background
- **Deep Space Atmosphere** - Authentic dark matter appearance
- **Galaxy-free Design** - Clean visualization without distracting elements

### ⚡ **High-Performance Jet Rendering**
- **Ultra-Thin Jets** - Precise, collimated relativistic streams
- **Volumetric Glow Effects** - 800+ particle-based plasma glow
- **Optimized Geometry** - Streamlined for smooth real-time performance
- **No Sheath Clutter** - Clean jet visualization without unnecessary complexity

### 🎨 **Modern Dark UI**
- **Professional Dark Theme** - Easy on the eyes for extended use
- **Flexible Panel Layout** - Responsive design that adapts to screen size
- **No Horizontal Scrolling** - Optimized for all window sizes
- **Enhanced Readability** - Proper text selection and contrast

### 🚀 **Performance Optimizations**
- **Simplified Physics** - Removed computationally expensive features
- **Efficient Rendering** - Eliminated magnetic field lines and complex calculations
- **Reduced Layer Count** - Streamlined visualization options
- **Faster Startup** - Quick initialization and rendering

## 📁 Project Structure

```
blandford-znajek/
├── bzsim.py                 # Main executable - run this file
├── physics.py              # Core Blandford-Znajek physics calculations
├── geometry.py             # 3D mesh generation (jets, disk, black hole)
└── visualizer/
    ├── main_visualizer.py   # Primary application controller
    ├── ui_controls.py       # User interface panels and controls
    ├── rendering.py         # 3D scene rendering and effects
    └── physics_calculations.py  # Real-time physics display
```

## 🎯 Current Visualization Layers

| Component | Description | Performance Impact |
|-----------|-------------|-------------------|
| **Black Hole** | Event horizon sphere | Minimal |
| **Accretion Disk** | Hot plasma disk with temperature gradients | Low |
| **Jet Spine** | Ultra-thin relativistic jets with glow effects | Medium |
| **Cosmic Background** | 3000+ star field | Low |

*Removed for performance: Photon ring, gravitational lensing, magnetic field lines, polarization vectors, jet sheath*

## 🚀 Quick Start

### Prerequisites
```bash
pip install PyQt5 PyVista numpy
```

### Run the Simulation
```bash
python bzsim.py
```

### Controls
- **Mouse**: Rotate, zoom, and pan around the black hole
- **Left Panel**: Adjust black hole mass, spin, and magnetic field
- **Right Panel**: View calculated physics parameters
- **Layer Toggles**: Show/hide visualization components

## ⚙️ Physics Parameters

### Black Hole Configuration
- **Mass**: 10 M☉ (adjustable 1-100 M☉)
- **Spin Parameter**: 0.9 (adjustable 0-0.999)
- **Magnetic Field**: 10⁴ Gauss (adjustable 10²-10⁶ G)

### Jet Properties
- **Base Radius**: 0.05 × Schwarzschild radius (ultra-thin)
- **Expansion**: Conical opening to 0.8 × Schwarzschild radius
- **Length**: 20 × Schwarzschild radius
- **Velocity**: 95% speed of light
- **Glow Particles**: 800 per jet for volumetric effects

### Accretion Disk
- **Temperature Profile**: Simple 1/r falloff for performance
- **Color Mapping**: Hot plasma colormap
- **Opacity**: 80% for balanced visibility

## 🎨 Visual Enhancements

### Jet Glow System
```python
# Enhanced lighting properties
ambient = 0.6      # Natural glow
diffuse = 0.8      # Surface illumination  
specular = 0.4     # Bright highlights
opacity = 0.95     # Near-solid appearance
```

### Cosmic Environment
- **Star Distribution**: Spherical shell at 150× black hole radius
- **Star Types**: White (60%), Blue (15%), Red (15%), Yellow (10%)
- **Brightness Variation**: Exponential distribution for realism
- **Background Color**: Deep cosmic blue (#010105)

## 🔧 Performance Features

### Optimization Strategies
1. **Reduced Mesh Complexity** - Fewer geometric points
2. **Simplified Physics** - Removed complex calculations
3. **Efficient Memory Usage** - Streamlined data structures
4. **Selective Updates** - Only update what's necessary
5. **GPU-Optimized Rendering** - PyVista/VTK acceleration

### Removed Features (for speed)
- ❌ Photon ring calculations
- ❌ Gravitational lensing effects  
- ❌ Magnetic field line tracing
- ❌ Polarization vector fields
- ❌ Jet sheath complexity
- ❌ Frame-dragging animations

## 🔬 Scientific Accuracy

While optimized for performance, the simulation maintains core physics:

- **Blandford-Znajek Mechanism**: Energy extraction from rotating black holes
- **Relativistic Jets**: Highly collimated plasma streams
- **Temperature Gradients**: Realistic accretion disk heating
- **Cosmic Scale**: Proper size relationships

## 🎯 Ideal Use Cases

- **Educational Demonstrations** - Teaching relativistic astrophysics
- **Research Visualization** - Exploring jet morphology
- **Public Outreach** - Engaging astronomy presentations  
- **Performance Benchmarking** - Testing visualization systems

## 🛠️ Recent Improvements

### Version 2.0 Enhancements
- ✅ Removed jet sheath for cleaner appearance
- ✅ Added volumetric glow effects to jets
- ✅ Implemented responsive UI layout
- ✅ Applied professional dark theme
- ✅ Optimized rendering performance
- ✅ Enhanced cosmic background
- ✅ Streamlined physics calculations

## 📝 Development Notes

This simulation prioritizes **visual impact** and **performance** over complete physical accuracy. Complex relativistic effects have been simplified or removed to ensure smooth real-time interaction on standard hardware.

For research-grade simulations requiring full general relativistic calculations, consider specialized codes like GRMHD simulations.

## 🤝 Contributing

Contributions welcome! Focus areas:
- Additional visual effects
- Performance optimizations  
- UI/UX improvements
- Educational features

## 📄 License

Open source - feel free to use and modify for educational and research purposes.

---
*Simulating the most powerful phenomena in the universe* 🌌

