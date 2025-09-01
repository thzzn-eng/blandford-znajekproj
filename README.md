# Blandford-Znajek Black Hole Simulation v2.0

## 🌌 Overview
Enhanced modular version of the Blandford-Znajek black hole jet simulation with improved architecture, better organization, and enhanced maintainability.

## 🏗️ Architecture

### Directory Structure
```
blandford-znajek/
├── src/                           # Main source code
│   ├── main/                      # Application entry point
│   │   ├── application.py         # Main application class
│   │   └── __init__.py
│   ├── ui/                        # User interface components
│   │   ├── control_panel.py       # Physics parameter controls
│   │   ├── info_panel.py          # Information display
│   │   └── __init__.py
│   ├── rendering/                 # 3D visualization and rendering
│   │   ├── simulation_renderer.py # Main 3D renderer
│   │   └── __init__.py
│   ├── geometry/                  # 3D geometric components
│   │   ├── black_hole.py          # Event horizon & ergosphere
│   │   ├── accretion_disk.py      # Spiral disk geometry
│   │   ├── jets.py                # Relativistic jets
│   │   └── __init__.py
│   ├── animation/                 # Time-based updates
│   │   ├── animation_manager.py   # Animation control
│   │   ├── disk_animator.py       # Disk motion updates
│   │   └── __init__.py
│   ├── physics/                   # Physics calculations
│   │   ├── blandford_znajek.py    # BZ mechanism physics
│   │   └── __init__.py
│   ├── utils/                     # Utility functions
│   │   ├── constants.py           # Physical constants
│   │   ├── math_helpers.py        # Mathematical functions
│   │   └── __init__.py
│   └── __init__.py
├── bzsim_v2.py                    # New main entry point
├── bzsim.py                       # Original entry point (legacy)
└── [original files...]           # Original monolithic files
```

## 🚀 Running the Simulation

### New Modular Version
```bash
python bzsim_v2.py
```

### Legacy Version
```bash
python bzsim.py
```

## 🎯 Key Improvements

### 1. **Modular Architecture**
- **Separation of Concerns**: Each module has a single responsibility
- **Better Organization**: Related functionality grouped together
- **Easier Maintenance**: Smaller, focused files are easier to understand and modify

### 2. **Enhanced Components**

#### **Physics Module** (`src/physics/`)
- Isolated physics calculations
- Reusable BZ mechanism class
- Clear parameter management

#### **Geometry Module** (`src/geometry/`)
- **Black Hole**: Oblate event horizon and ergosphere
- **Accretion Disk**: Spiral particle system with recycling
- **Jets**: Proper relativistic jet geometry

#### **UI Module** (`src/ui/`)
- **Control Panel**: Physics parameter controls
- **Info Panel**: Real-time physics display
- Clean separation of UI and logic

#### **Rendering Module** (`src/rendering/`)
- **3D Scene Management**: Centralized rendering control
- **Component Integration**: Seamless geometry updates
- **Lighting and Effects**: Enhanced visual quality

#### **Animation Module** (`src/animation/`)
- **Animation Manager**: Centralized timing control
- **Component Animators**: Specialized animation handlers
- **Performance Optimization**: Efficient update scheduling

### 3. **Code Quality Improvements**
- **Type Hints**: Better code documentation
- **Error Handling**: Robust error management
- **Documentation**: Comprehensive docstrings
- **Constants**: Centralized configuration

### 4. **Maintainability Benefits**
- **Easier Testing**: Isolated components can be tested independently
- **Faster Development**: Clear structure speeds up feature additions
- **Bug Isolation**: Issues are easier to locate and fix
- **Code Reuse**: Components can be reused across different visualizations

## 📊 File Size Comparison

### Before Refactoring
- `enhanced_visualizer.py`: **1,615 lines** (too complex)
- `visualizer.py`: **1,544 lines** (duplicate complexity)
- Total complexity: **>3,000 lines** in 2 files

### After Refactoring
- Largest file: **~200 lines** (manageable)
- Average file size: **~100 lines** (focused)
- Total: **Same functionality** in **organized structure**

## 🧩 Module Dependencies

```
application.py
├── ui/
│   ├── control_panel.py
│   └── info_panel.py
├── rendering/
│   └── simulation_renderer.py
│       ├── geometry/
│       │   ├── black_hole.py
│       │   ├── accretion_disk.py
│       │   └── jets.py
│       └── animation/
│           └── disk_animator.py
├── physics/
│   └── blandford_znajek.py
└── utils/
    ├── constants.py
    └── math_helpers.py
```

## 🔬 Physics Features

- **Kerr Black Hole Geometry**: Oblate event horizon and ergosphere
- **Spiral Accretion Disk**: Logarithmic spiral with particle recycling
- **Relativistic Jets**: Proper jet geometry with collar expansion
- **Real-time Calculations**: Live physics parameter updates
- **Magnetic Field Lines**: Optional field line visualization

## 🎮 User Interface

- **Parameter Controls**: Mass, spin, magnetic field
- **Animation Controls**: Play, pause, reset
- **Visualization Options**: Toggle components on/off
- **Real-time Display**: Live physics calculations
- **Dark Theme**: Professional appearance

## 🏃‍♂️ Performance

- **Optimized Updates**: Components update at appropriate frequencies
- **Efficient Rendering**: Smart mesh updates to prevent flashing
- **Memory Management**: Proper resource cleanup
- **Responsive UI**: Non-blocking animation system

## 🔮 Future Enhancements

The modular structure makes it easy to add:
- **Additional Geometry Types**: Easy to add new 3D components
- **Physics Models**: Plug in different physics calculations
- **Rendering Effects**: Add post-processing effects
- **Export Features**: Add data export capabilities
- **Comparison Mode**: Side-by-side parameter comparison

## 🧪 Development

### Adding New Features
1. Identify the appropriate module (geometry, physics, ui, etc.)
2. Create focused, single-purpose classes
3. Use existing utilities and constants
4. Connect through the main application class

### Testing Components
Each module can be tested independently:
```python
# Test physics calculations
from src.physics.blandford_znajek import BlandfordZnajekJet
physics = BlandfordZnajekJet(mass=10, spin=0.9, B=1e4)
print(f"Power: {physics.L_BZ:.2e} erg/s")
```

---

**🌟 The refactored version maintains all original functionality while providing a solid foundation for future development and maintenance.**
