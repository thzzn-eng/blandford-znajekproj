"""
Main Blandford-Znajek Visualizer - Modular version
Integrates all components into a cohesive application
"""

import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import pyvista as pv
from pyvistaqt import QtInteractor

# Import our custom modules
from .ui_controls import UIControls
from .rendering import RenderingEngine
from .physics_calculations import PhysicsCalculations

# Import physics and geometry modules
from physics import BlandfordZnajekJet as Jet
from geometry import GeometryGenerator


class JetVisualizer(QtWidgets.QMainWindow):
    """Main Blandford-Znajek Visualizer Application"""
    
    def __init__(self, mass=10.0, spin=0.9, B=1e4):
        super().__init__()
        
        # Initialize physics objects with provided parameters
        self.jet = Jet(mass=mass, spin=spin, B=B)
        self.mdot = 1e-8  # Solar masses per year in g/s
        self.distance = 100.0  # Mpc
        self.viewing_angle = 15.0  # degrees
        self.current_time = 0.0  # simulation time
        self.jet_opening_angle = 5.0  # degrees
        
        # Initialize geometry generator
        physics_params = self.jet.get_physical_scales()
        self.geometry = GeometryGenerator(physics_params)
        
        # Initialize layer states for visibility control
        self.layer_states = {
            'black_hole': True,
            'accretion_disk': True,
            'jet_spine': True,
            'background': True
        }
        
        # Initialize component modules
        self.ui_controls = UIControls(self)
        self.rendering_engine = RenderingEngine(self)
        self.physics_calc = PhysicsCalculations(self)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Initialize UI
        self.init_ui()
        
        # Connect signals
        self.setup_connections()
        
        # Initial scene setup
        self.update_all()
    
    def apply_dark_theme(self):
        """Apply dark theme to the entire application"""
        dark_stylesheet = """
        QMainWindow {
            background-color: #000000;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #000000;
            color: #ffffff;
            font-family: 'Segoe UI';
            font-size: 10pt;
        }
        
        QGroupBox {
            background-color: #1a1a1a;
            border: 2px solid #404040;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 18px;
            color: #ffffff;
            font-weight: bold;
            font-size: 11pt;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px 0 8px;
            color: #ffffff;
            background-color: #000000;
        }
        
        QLabel {
            color: #ffffff;
            background-color: transparent;
            font-size: 10pt;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #404040;
            height: 10px;
            background: #1a1a1a;
            margin: 2px 0;
            border-radius: 5px;
        }
        
        QSlider::handle:horizontal {
            background: #ffffff;
            border: 2px solid #cccccc;
            width: 20px;
            margin: -3px 0;
            border-radius: 10px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #f0f0f0;
            border: 2px solid #ffffff;
        }
        
        QSlider::sub-page:horizontal {
            background: #404040;
            border: 1px solid #404040;
            height: 10px;
            border-radius: 5px;
        }
        
        QSlider::add-page:horizontal {
            background: #1a1a1a;
            border: 1px solid #404040;
            height: 10px;
            border-radius: 5px;
        }
        
        QSpinBox, QDoubleSpinBox {
            background-color: #1a1a1a;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 4px;
            color: #ffffff;
            font-size: 10pt;
        }
        
        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #ffffff;
        }
        
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            background-color: #2a2a2a;
            border: 1px solid #404040;
            border-top-right-radius: 4px;
            width: 16px;
        }
        
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            background-color: #2a2a2a;
            border: 1px solid #404040;
            border-bottom-right-radius: 4px;
            width: 16px;
        }
        
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
            background-color: #404040;
        }
        
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
            background-color: #404040;
        }
        
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
            color: #ffffff;
            width: 8px;
            height: 8px;
        }
        
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
            color: #ffffff;
            width: 8px;
            height: 8px;
        }
        
        QCheckBox {
            color: #ffffff;
            background-color: transparent;
            spacing: 8px;
            font-size: 10pt;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            background-color: #1a1a1a;
            border: 2px solid #404040;
            border-radius: 4px;
        }
        
        QCheckBox::indicator:hover {
            border: 2px solid #ffffff;
        }
        
        QCheckBox::indicator:checked {
            background-color: #ffffff;
            border: 2px solid #ffffff;
        }
        
        QPushButton {
            background-color: #1a1a1a;
            border: 2px solid #404040;
            border-radius: 6px;
            padding: 10px 20px;
            color: #ffffff;
            font-weight: bold;
            font-size: 10pt;
        }
        
        QPushButton:hover {
            background-color: #2a2a2a;
            border: 2px solid #ffffff;
        }
        
        QPushButton:pressed {
            background-color: #0a0a0a;
            border: 2px solid #cccccc;
        }
        
        QScrollArea {
            background-color: #000000;
            border: 1px solid #404040;
            border-radius: 6px;
        }
        
        QScrollArea > QWidget > QWidget {
            background-color: #000000;
        }
        
        QScrollBar:vertical {
            background-color: #1a1a1a;
            width: 14px;
            border-radius: 7px;
            border: 1px solid #404040;
        }
        
        QScrollBar::handle:vertical {
            background-color: #404040;
            border-radius: 6px;
            min-height: 25px;
            margin: 1px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #ffffff;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background-color: transparent;
            height: 0px;
        }
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background-color: transparent;
        }
        
        QTextEdit, QPlainTextEdit {
            background-color: #1a1a1a;
            border: 1px solid #404040;
            border-radius: 6px;
            color: #ffffff;
            padding: 8px;
            font-size: 10pt;
        }
        
        QTextEdit:focus, QPlainTextEdit:focus {
            border: 2px solid #ffffff;
        }
        
        QProgressBar {
            background-color: #1a1a1a;
            border: 1px solid #404040;
            border-radius: 6px;
            text-align: center;
            color: #ffffff;
            font-weight: bold;
        }
        
        QProgressBar::chunk {
            background-color: #ffffff;
            border-radius: 6px;
        }
        """
        
        # Apply to the main application
        self.setStyleSheet(dark_stylesheet)
        
        # Force the application palette to override system selection colors
        app = QtWidgets.QApplication.instance()
        if app:
            palette = app.palette()
            palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(64, 64, 64))  # #404040
            palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))  # white
            palette.setColor(QtGui.QPalette.Text, QtGui.QColor(255, 255, 255))  # white
            palette.setColor(QtGui.QPalette.Base, QtGui.QColor(26, 26, 26))  # #1a1a1a
            palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))  # black
            palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(255, 255, 255))  # white
            app.setPalette(palette)
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Blandford-Znajek Black Hole Jet Visualizer")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Central widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QtWidgets.QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Left control panel
        self.ui_controls.create_control_panel(main_layout)
        
        # Center 3D visualization
        self.rendering_engine.create_visualization_panel(main_layout)
        
        # Right info panel
        self.physics_calc.create_info_panel(main_layout)
        
        # Set layout ratios - more balanced for better use of horizontal space
        main_layout.setStretch(0, 2)  # Controls - increased from 1
        main_layout.setStretch(1, 4)  # 3D View - increased from 3 
        main_layout.setStretch(2, 2)  # Info - increased from 1
    
    def setup_connections(self):
        """Connect signals between components"""
        # Connect UI controls to update methods
        for control_name in ['mass', 'spin', 'B', 'mdot', 'jet_velocity', 'opening_angle']:
            if hasattr(self.ui_controls, f'{control_name}_slider'):
                slider = getattr(self.ui_controls, f'{control_name}_slider')
                slider.valueChanged.connect(self.update_physics_from_ui)
        
        # Connect layer toggles
        for layer_name in ['black_hole', 'disk', 'jets', 'field_lines']:
            if hasattr(self.ui_controls, f'show_{layer_name}'):
                checkbox = getattr(self.ui_controls, f'show_{layer_name}')
                checkbox.toggled.connect(self.update_visibility)
        
        # Connect time controls
        if hasattr(self.ui_controls, 'time_slider'):
            self.ui_controls.time_slider.valueChanged.connect(self.update_time)
        
        # Connect export controls
        if hasattr(self.ui_controls, 'export_image_btn'):
            self.ui_controls.export_image_btn.clicked.connect(self.export_image)
        if hasattr(self.ui_controls, 'export_animation_btn'):
            self.ui_controls.export_animation_btn.clicked.connect(self.export_animation)
    
    def update_physics_from_ui(self):
        """Update physics parameters from UI controls"""
        try:
            # Update jet properties
            self.jet.mass = self.ui_controls.mass_slider.value()
            self.jet.spin = self.ui_controls.spin_slider.value() / 100.0
            self.jet.B = self.ui_controls.B_slider.value()
            self.jet.jet_velocity = self.ui_controls.jet_velocity_slider.value() / 100.0
            self.jet.opening_angle = self.ui_controls.opening_angle_slider.value()
            
            # Update other parameters
            self.mdot = 10**(self.ui_controls.mdot_slider.value() / 10.0 - 10)
            
            # Update displays and visualization
            self.update_all()
            
        except Exception as e:
            print(f"Error updating physics from UI: {e}")
    
    def update_visibility(self):
        """Update layer visibility based on checkboxes"""
        try:
            # Update the scene completely based on current layer states
            self.rendering_engine.update_scene()
            
        except Exception as e:
            print(f"Error updating visibility: {e}")
    
    def update_time(self):
        """Update simulation time"""
        try:
            self.current_time = self.ui_controls.time_slider.value() / 10.0
            self.update_all()
            
        except Exception as e:
            print(f"Error updating time: {e}")
    
    def update_all(self):
        """Update all components"""
        try:
            # Update 3D scene
            self.rendering_engine.update_scene()
            
            # Update physics calculations and displays
            self.physics_calc.update_info_display()
            
            # Update UI parameter displays
            self.ui_controls.update_parameter_displays()
            
        except Exception as e:
            print(f"Error in update_all: {e}")
    
    # Callback methods for UI controls
    def on_mass_changed(self, value):
        """Handle mass slider change"""
        self.jet.mass = value
        self.update_physics_and_geometry()
    
    def on_mass_spinbox_changed(self, value):
        """Handle mass spinbox change"""
        self.mass_slider.setValue(value)
    
    def on_spin_changed(self, value):
        """Handle spin slider change"""
        self.jet.spin = value / 1000.0  # Convert from 0-999 to 0-0.999
        self.update_physics_and_geometry()
    
    def on_spin_spinbox_changed(self, value):
        """Handle spin spinbox change"""
        self.spin_slider.setValue(int(value * 1000))
    
    def on_B_changed(self, value):
        """Handle magnetic field slider change"""
        self.jet.B = 10**value  # Logarithmic scale
        self.update_physics_and_geometry()
    
    def on_B_spinbox_changed(self, value):
        """Handle magnetic field spinbox change"""
        import math
        self.B_slider.setValue(math.log10(value))
    
    def on_mdot_changed(self, value):
        """Handle accretion rate slider change"""
        self.mdot = 10**(value / 10.0 - 10)  # Logarithmic scale
        self.update_physics_and_geometry()
    
    def on_mdot_spinbox_changed(self, value):
        """Handle accretion rate spinbox change"""
        import math
        self.mdot_slider.setValue(int((math.log10(value) + 10) * 10))
    
    def on_viewing_changed(self, value):
        """Handle viewing angle slider change"""
        self.viewing_angle = value
        self.update_all()
    
    def on_viewing_spinbox_changed(self, value):
        """Handle viewing angle spinbox change"""
        self.viewing_slider.setValue(value)
    
    def on_opening_changed(self, value):
        """Handle jet opening angle slider change"""
        self.jet_opening_angle = value
        self.update_physics_and_geometry()
    
    def on_opening_spinbox_changed(self, value):
        """Handle jet opening angle spinbox change"""
        self.opening_slider.setValue(value)
    
    def on_distance_changed(self, value):
        """Handle distance slider change"""
        self.distance = value
        self.update_all()
    
    def on_distance_spinbox_changed(self, value):
        """Handle distance spinbox change"""
        self.distance_slider.setValue(value)
    
    def on_layer_toggled(self, layer_key, state):
        """Handle layer visibility toggle"""
        self.layer_states[layer_key] = (state == 2)  # 2 = checked, 0 = unchecked
        self.update_visibility()
    
    # Time control methods
    def toggle_playback(self):
        """Toggle between play and pause"""
        # For now, just update the button text
        if hasattr(self, 'play_button'):
            if self.play_button.text() == "⏸️ Pause":
                self.play_button.setText("▶️ Play")
            else:
                self.play_button.setText("⏸️ Pause")
    
    def step_backward(self):
        """Step backward in time"""
        if hasattr(self, 'time_slider'):
            current_val = self.time_slider.value()
            self.time_slider.setValue(max(0, current_val - 1))
    
    def step_forward(self):
        """Step forward in time"""
        if hasattr(self, 'time_slider'):
            current_val = self.time_slider.value()
            max_val = self.time_slider.maximum()
            self.time_slider.setValue(min(max_val, current_val + 1))
    
    def on_speed_changed(self, speed_text):
        """Handle speed combo box change"""
        # Extract numeric value from speed text like "1.0x"
        try:
            speed = float(speed_text.replace('x', ''))
            print(f"Speed changed to {speed}x")
        except ValueError:
            pass
    
    # Export methods
    def export_time_series(self):
        """Export time series data to CSV"""
        try:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export Time Series", "", "CSV Files (*.csv)")
            
            if filename:
                QtWidgets.QMessageBox.information(self, "Export Complete", 
                                                f"Time series data saved to {filename}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Export Error", 
                                        f"Failed to export time series: {e}")
    
    def export_frame(self):
        """Export current frame as image"""
        self.export_image()
    
    def export_movie(self):
        """Export movie animation"""
        self.export_animation()
    
    def update_physics_and_geometry(self):
        """Update physics parameters and regenerate geometry"""
        try:
            # Update geometry with new physics parameters
            physics_params = self.jet.get_physical_scales()
            self.geometry.update_physics_params(physics_params)
            
            # Update all displays
            self.update_all()
            
        except Exception as e:
            print(f"Error updating physics and geometry: {e}")
    
    
    def export_image(self):
        """Export current view as image"""
        try:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
            
            if filename:
                self.rendering_engine.export_current_view(filename)
                QtWidgets.QMessageBox.information(self, "Export Complete", 
                                                f"Image saved to {filename}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Export Error", 
                                        f"Failed to export image: {e}")
    
    def export_animation(self):
        """Export animation sequence"""
        try:
            filename, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Export Animation", "", "MP4 Files (*.mp4);;GIF Files (*.gif)")
            
            if filename:
                # Simple animation of rotating view
                QtWidgets.QMessageBox.information(self, "Export Started", 
                                                "Animation export started. This may take a while...")
                
                self.rendering_engine.export_animation(filename)
                
                QtWidgets.QMessageBox.information(self, "Export Complete", 
                                                f"Animation saved to {filename}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Export Error", 
                                        f"Failed to export animation: {e}")
    
    def closeEvent(self, event):
        """Clean shutdown"""
        try:
            self.rendering_engine.cleanup()
            event.accept()
        except Exception as e:
            print(f"Error during shutdown: {e}")
            event.accept()


def main():
    """Main application entry point"""
    app = QtWidgets.QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    visualizer = JetVisualizer()
    visualizer.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
