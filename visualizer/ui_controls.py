"""
UI Controls module for the Blandford-Znajek visualizer
Handles creation of control panels, sliders, and interactive widgets
"""

import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui


class UIControls:
    """Handles creation and management of UI control panels"""
    
    def __init__(self, parent_visualizer):
        self.visualizer = parent_visualizer
        self.layer_checkboxes = {}
    
    def create_control_panel(self, main_layout):
        """Create left control panel with physics parameters and layer toggles"""
        control_scroll = QtWidgets.QScrollArea()
        control_scroll.setMinimumWidth(250)  # Minimum width instead of fixed
        control_scroll.setWidgetResizable(True)
        
        control_widget = QtWidgets.QWidget()
        control_layout = QtWidgets.QVBoxLayout(control_widget)
        
        # Physics Parameters Group
        self.create_physics_controls(control_layout)
        
        # Layer Toggle Group
        self.create_layer_controls(control_layout)
        
        # Time Controls Group
        self.create_time_controls(control_layout)
        
        # Export Controls Group
        self.create_export_controls(control_layout)
        
        control_scroll.setWidget(control_widget)
        main_layout.addWidget(control_scroll)
    
    def create_physics_controls(self, parent_layout):
        """Create physics parameter controls with sliders and spinboxes"""
        physics_group = QtWidgets.QGroupBox("Physics Parameters")
        physics_layout = QtWidgets.QFormLayout()
        
        # Mass (M) - 1 to 100 solar masses
        mass_widget = self._create_slider_spinbox_widget(
            "mass", 1, 100, self.visualizer.jet.mass, " M☉", 
            "Black hole mass affects event horizon size, ISCO radius, and jet power scaling"
        )
        physics_layout.addRow("Mass:", mass_widget)
        
        # Spin (a) - 0 to 0.999
        spin_widget = self._create_slider_spinbox_widget(
            "spin", 0, 999, self.visualizer.jet.spin * 1000, "", 
            "Dimensionless spin parameter (a/M). Higher spin increases jet power via Blandford-Znajek mechanism",
            slider_scale=1000, decimals=3, spinbox_range=(0.0, 0.999)
        )
        physics_layout.addRow("Spin (a):", spin_widget)
        
        # Magnetic Field (B) - 10² to 10⁶ Gauss (log scale)
        B_widget = self._create_log_slider_spinbox_widget(
            "B", 20, 60, self.visualizer.jet.B, " G",
            "Magnetic field strength near the black hole. Determines jet power via L_BZ ∝ B²a²M²",
            log_range=(100, 1e6)
        )
        physics_layout.addRow("B-field:", B_widget)
        
        # Additional parameters
        self.create_additional_physics_params(physics_layout)
        
        physics_group.setLayout(physics_layout)
        parent_layout.addWidget(physics_group)
    
    def create_additional_physics_params(self, physics_layout):
        """Create additional physics parameter controls"""
        # Accretion Rate (Mdot)
        mdot_widget = self._create_log_slider_spinbox_widget(
            "mdot", 15, 21, self.visualizer.mdot, " g/s",
            "Mass accretion rate affects disk luminosity and jet-disk coupling",
            log_range=(1e15, 1e21)
        )
        physics_layout.addRow("Mdot:", mdot_widget)
        
        # Viewing Angle
        viewing_widget = self._create_slider_spinbox_widget(
            "viewing", 0, 180, self.visualizer.viewing_angle, "°",
            "Viewing angle relative to jet axis. Affects relativistic beaming and Doppler boosting"
        )
        physics_layout.addRow("Viewing Angle:", viewing_widget)
        
        # Jet Opening Angle
        opening_widget = self._create_slider_spinbox_widget(
            "opening", 1, 30, self.visualizer.jet_opening_angle, "°",
            "Half-opening angle of the jet cone. Narrower jets show stronger beaming effects"
        )
        physics_layout.addRow("Jet Opening:", opening_widget)
        
        # Distance
        distance_widget = self._create_slider_spinbox_widget(
            "distance", 1, 1000, self.visualizer.distance, " Mpc",
            "Distance to source for flux calculations and angular size scaling"
        )
        physics_layout.addRow("Distance:", distance_widget)
    
    def _create_slider_spinbox_widget(self, param_name, min_val, max_val, current_val, suffix, tooltip, 
                                    slider_scale=1, decimals=1, spinbox_range=None):
        """Create a slider-spinbox widget pair"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Slider
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(int(current_val * slider_scale) if slider_scale != 1 else int(current_val))
        
        # Spinbox
        spinbox = QtWidgets.QDoubleSpinBox()
        if spinbox_range:
            spinbox.setRange(*spinbox_range)
        else:
            spinbox.setRange(min_val / slider_scale if slider_scale != 1 else min_val, 
                           max_val / slider_scale if slider_scale != 1 else max_val)
        spinbox.setDecimals(decimals)
        spinbox.setValue(current_val)
        spinbox.setSuffix(suffix)
        
        # Connect signals
        slider.valueChanged.connect(getattr(self.visualizer, f'on_{param_name}_changed'))
        spinbox.valueChanged.connect(getattr(self.visualizer, f'on_{param_name}_spinbox_changed'))
        
        # Store references
        setattr(self.visualizer, f'{param_name}_slider', slider)
        setattr(self.visualizer, f'{param_name}_spinbox', spinbox)
        
        layout.addWidget(slider, 3)
        layout.addWidget(spinbox, 1)
        
        widget.setToolTip(tooltip)
        return widget
    
    def _create_log_slider_spinbox_widget(self, param_name, min_log, max_log, current_val, suffix, tooltip, log_range):
        """Create a logarithmic slider-spinbox widget pair"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Slider (logarithmic)
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(min_log, max_log)
        slider.setValue(int(np.log10(current_val) * 10))
        
        # Spinbox
        spinbox = QtWidgets.QDoubleSpinBox()
        spinbox.setRange(*log_range)
        spinbox.setValue(current_val)
        spinbox.setSuffix(suffix)
        spinbox.setDecimals(0)
        
        # Connect signals
        slider.valueChanged.connect(getattr(self.visualizer, f'on_{param_name}_changed'))
        spinbox.valueChanged.connect(getattr(self.visualizer, f'on_{param_name}_spinbox_changed'))
        
        # Store references
        setattr(self.visualizer, f'{param_name}_slider', slider)
        setattr(self.visualizer, f'{param_name}_spinbox', spinbox)
        
        layout.addWidget(slider, 3)
        layout.addWidget(spinbox, 1)
        
        widget.setToolTip(tooltip)
        return widget
    
    def create_layer_controls(self, parent_layout):
        """Create layer visibility toggle controls"""
        layer_group = QtWidgets.QGroupBox("Visualization Layers")
        layer_layout = QtWidgets.QVBoxLayout()
        
        layer_info = {
            'accretion_disk': ('Accretion Disk', 'Hot plasma disk feeding the black hole'),
            'jet_spine': ('Jet Spine', 'Inner jet core with highest Lorentz factor'),
            'background': ('Background', 'Stars and distant galaxies')
        }
        
        for layer_key, (layer_name, tooltip) in layer_info.items():
            checkbox = QtWidgets.QCheckBox(layer_name)
            checkbox.setChecked(self.visualizer.layer_states[layer_key])
            checkbox.stateChanged.connect(lambda state, key=layer_key: self.visualizer.on_layer_toggled(key, state))
            checkbox.setToolTip(tooltip)
            self.layer_checkboxes[layer_key] = checkbox
            layer_layout.addWidget(checkbox)
        
        layer_group.setLayout(layer_layout)
        parent_layout.addWidget(layer_group)
    
    def create_time_controls(self, parent_layout):
        """Create time control widgets"""
        time_group = QtWidgets.QGroupBox("Time Controls")
        time_layout = QtWidgets.QVBoxLayout()
        
        # Play/Pause buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.visualizer.play_button = QtWidgets.QPushButton("⏸️ Pause")
        self.visualizer.play_button.clicked.connect(self.visualizer.toggle_playback)
        button_layout.addWidget(self.visualizer.play_button)
        
        self.visualizer.step_back_button = QtWidgets.QPushButton("⏮️")
        self.visualizer.step_back_button.clicked.connect(self.visualizer.step_backward)
        button_layout.addWidget(self.visualizer.step_back_button)
        
        self.visualizer.step_forward_button = QtWidgets.QPushButton("⏭️")
        self.visualizer.step_forward_button.clicked.connect(self.visualizer.step_forward)
        button_layout.addWidget(self.visualizer.step_forward_button)
        
        time_layout.addLayout(button_layout)
        
        # Speed control
        speed_layout = QtWidgets.QHBoxLayout()
        speed_layout.addWidget(QtWidgets.QLabel("Speed:"))
        
        self.visualizer.speed_combo = QtWidgets.QComboBox()
        self.visualizer.speed_combo.addItems(["0.25x", "0.5x", "1x", "2x", "5x"])
        self.visualizer.speed_combo.setCurrentText("1x")
        self.visualizer.speed_combo.currentTextChanged.connect(self.visualizer.on_speed_changed)
        speed_layout.addWidget(self.visualizer.speed_combo)
        
        time_layout.addLayout(speed_layout)
        
        time_group.setLayout(time_layout)
        parent_layout.addWidget(time_group)
    
    def create_export_controls(self, parent_layout):
        """Create export control widgets"""
        export_group = QtWidgets.QGroupBox("Export & Analysis")
        export_layout = QtWidgets.QVBoxLayout()
        
        # Export buttons
        self.visualizer.export_csv_button = QtWidgets.QPushButton("📊 Export Time Series (CSV)")
        self.visualizer.export_csv_button.clicked.connect(self.visualizer.export_time_series)
        export_layout.addWidget(self.visualizer.export_csv_button)
        
        self.visualizer.export_png_button = QtWidgets.QPushButton("📷 Export Frame (PNG)")
        self.visualizer.export_png_button.clicked.connect(self.visualizer.export_frame)
        export_layout.addWidget(self.visualizer.export_png_button)
        
        self.visualizer.export_movie_button = QtWidgets.QPushButton("🎬 Export Movie (MP4)")
        self.visualizer.export_movie_button.clicked.connect(self.visualizer.export_movie)
        export_layout.addWidget(self.visualizer.export_movie_button)
        
        export_group.setLayout(export_layout)
        parent_layout.addWidget(export_group)
    
    def update_parameter_displays(self):
        """Update parameter display labels (placeholder for now)"""
        # This method can be expanded to update any parameter display labels
        # For now, it's just a placeholder to satisfy the interface
        pass
