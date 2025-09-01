"""
Advanced visualization and rendering for the black hole jet simulation
with comprehensive physics controls and interactive UI
"""
import numpy as np
import time
import csv
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
import pyvista as pv
from pyvistaqt import QtInteractor

from physics import BlandfordZnajekJet, RelativisticEffects
from geometry import GeometryGenerator

class JetVisualizer(QtWidgets.QWidget):
    """
    Advanced visualization widget with comprehensive physics controls.
    
    Features:
    - Interactive sliders for all physics parameters with live updates
    - Layer toggles for visualization components  
    - Real-time info panel with derived quantities
    - Time controls and data export capabilities
    - Professional 3-panel layout with tooltips
    """
    
    def __init__(self, mass=10.0, spin=0.9, B=1e4, parent=None):
        """
        Initialize advanced visualizer with comprehensive controls.
        
        Args:
            mass (float): Black hole mass in solar masses
            spin (float): Dimensionless spin parameter
            B (float): Magnetic field strength in Gauss
            parent: Qt parent widget
        """
        super().__init__(parent)
        
        # Initialize physics with adjustable parameters
        self.jet = BlandfordZnajekJet(mass=mass, spin=spin, B=B)
        self.relativistic = RelativisticEffects(jet_velocity=self.jet.jet_velocity)
        
        # Initialize geometry generator with physics parameters
        physics_params = self.jet.get_physical_scales()
        self.geometry = GeometryGenerator(physics_params)
        
        # Extended physics parameters
        self.mdot = 1e18  # Accretion rate (g/s)
        self.viewing_angle = 45.0  # degrees
        self.jet_opening_angle = 5.0  # degrees
        self.electron_spectral_index = 2.5
        self.distance = 100.0  # Mpc for flux calculations
        self.resolution_factor = 1.0
        
        # Layer visibility states
        self.layer_states = {
            'photon_ring': True,
            'gravitational_lensing': True,
            'accretion_disk': True,
            'jet_sheath': True,
            'jet_spine': True,
            'magnetic_field_lines': False,
            'polarization_vectors': False,
            'background': True
        }
        
        # Time controls
        self.is_playing = True
        self.time_speed = 1.0
        self.t = 0.0
        self.time_data = []  # For time series
        
        # Animation timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(100)  # 10 FPS
        
        self.init_ui()
    
    def update_physics_parameters(self, mass=None, spin=None, B=None):
        """
        Update black hole parameters and regenerate scene.
        
        Args:
            mass (float, optional): New mass in solar masses
            spin (float, optional): New spin parameter
            B (float, optional): New magnetic field in Gauss
        """
        # Update parameters if provided
        if mass is not None:
            self.jet.mass = mass
        if spin is not None:
            self.jet.spin = spin
        if B is not None:
            self.jet.B = B
        
        # Update relativistic effects with new jet velocity
        self.relativistic.update_jet_velocity(self.jet.jet_velocity)
        
        # Update geometry with new physics parameters
        physics_params = self.jet.get_physical_scales()
        self.geometry.update_physics_params(physics_params)
        
        # Regenerate the entire scene with new parameters
        self.regenerate_scene()
        
        # Update displays
        self.update_displays()
    
    def regenerate_scene(self):
        """Completely regenerate the 3D scene with updated parameters"""
        # Clear existing actors
        self.plotter.clear()
        
        # Reinitialize the scene
        self.init_scene()
        
        # Update displays
        self.update_displays()
        
        # Add black hole event horizon
        self.plotter.add_mesh(self.cached_meshes['black_hole'], 
                             color='black', name='black_hole')
        
        # Add conical glow effects
        self.plotter.add_mesh(self.cached_meshes['glow_pos'], 
                             color='orange', opacity=0.3, 
                             name='glow_pos')
        
        self.plotter.add_mesh(self.cached_meshes['glow_neg'], 
                             color='cyan', opacity=0.3, 
                             name='glow_neg')
        
        # Add bright core region - these are points, not mesh
        self.plotter.add_points(self.cached_meshes['bright_core_points'], 
                               scalars=self.cached_meshes['bright_core_colors'], cmap='hot',
                               point_size=4, name='bright_core', 
                               render_points_as_spheres=True, emissive=True, opacity=0.9)
        
        # Add background elements (stars and galaxies) - these don't need caching
        self.add_background_elements()
    
    def add_background_elements(self):
        """Add stars and galaxies to the background"""
        # Generate background stars
        n_stars = 800
        star_xyz = np.random.randn(n_stars, 3) * self.geometry.disk_radius * 30
        star_colors = np.random.rand(n_stars, 3)
        star_colors[:, 0] = np.random.choice([1.0, 0.8, 0.6], n_stars)  # Stellar colors
        star_colors[:, 1] = np.random.uniform(0.6, 1.0, n_stars)
        star_colors[:, 2] = np.random.uniform(0.8, 1.0, n_stars)
        
        self.plotter.add_points(star_xyz, scalars=star_colors, rgb=True, 
                               point_size=1.5, name='stars', 
                               render_points_as_spheres=True, emissive=True)
        
        # Generate distant galaxies
        n_galaxies = 150
        galaxy_xyz = np.random.randn(n_galaxies, 3) * self.geometry.disk_radius * 80
        galaxy_colors = np.ones((n_galaxies, 3)) * 0.7
        galaxy_colors[:, 2] = 0.9  # Slight blue tint
        
        self.plotter.add_points(galaxy_xyz, scalars=galaxy_colors, rgb=True, 
                               point_size=4, name='galaxies', 
                               render_points_as_spheres=True, emissive=True)
        
    def get_viewing_angle_to_jet(self):
        """Calculate the viewing angle relative to the jet axis (z-axis)"""
        try:
            camera_pos = np.array(self.plotter.camera.position)
            camera_focal = np.array(self.plotter.camera.focal_point)
            
            view_direction = camera_pos - camera_focal
            view_direction = view_direction / np.linalg.norm(view_direction)
            
            jet_axis = np.array([0, 0, 1])
            viewing_angle = np.arccos(np.clip(np.dot(view_direction, jet_axis), -1, 1))
            
            return viewing_angle, view_direction[2]
        except:
            return np.pi/4, 1.0
    
    def init_scene(self):
        """Initialize the 3D scene with all objects"""
        self.plotter.clear()
        
        # Black hole
        bh_sphere = self.geometry.create_black_hole()
        self.bh_actor = self.plotter.add_mesh(bh_sphere, color='black', name='blackhole')
        
        # Jets (now use parameterless methods)
        self.jet_mesh_pos, self.jet_mesh_neg, jet_colors = self.geometry.create_jets()
        
        self.jet_colors_pos_base = jet_colors.copy()
        self.jet_colors_neg_base = jet_colors.copy()
        
        self.jet_actor_pos = self.plotter.add_mesh(
            self.jet_mesh_pos, scalars=jet_colors, cmap='Blues', 
            name='jet_pos', opacity=0.8)
        
        self.jet_actor_neg = self.plotter.add_mesh(
            self.jet_mesh_neg, scalars=jet_colors, cmap='Blues', 
            name='jet_neg', opacity=0.8)
        
        # Conical glow (now use parameterless methods)
        self.cone_mesh_pos, self.cone_mesh_neg, cone_colors = self.geometry.create_conical_glow()
        
        self.cone_colors_pos_base = cone_colors.copy()
        self.cone_colors_neg_base = cone_colors.copy()
        
        self.cone_actor_pos = self.plotter.add_mesh(
            self.cone_mesh_pos, scalars=cone_colors, cmap='Oranges',
            name='cone_pos', opacity=0.1, show_edges=False)
        
        self.cone_actor_neg = self.plotter.add_mesh(
            self.cone_mesh_neg, scalars=cone_colors, cmap='Oranges',
            name='cone_neg', opacity=0.1, show_edges=False)
        
        # Bright core
        core_points, core_colors = self.geometry.create_bright_core()
        self.core_points = core_points
        self.core_colors_base = core_colors
        
        self.core_actor = self.plotter.add_points(
            core_points, scalars=core_colors, cmap='hot',
            point_size=4, name='bright_core', render_points_as_spheres=True,
            emissive=True, opacity=0.9)
        
        # Warped accretion disk (now toroidal/donut-shaped)
        disk_mesh, disk_scalars = self.geometry.create_warped_accretion_disk()
        self.warped_disk_mesh = disk_mesh
        self.disk_scalars = disk_scalars  # Store for dynamic updates
        
        self.warped_disk_actor = self.plotter.add_mesh(
            disk_mesh, scalars=disk_scalars, cmap='hot',
            opacity=0.8, name='warped_disk', show_edges=False)
        
        # Photon ring
        ring_points, ring_scalars = self.geometry.create_photon_ring()
        
        self.photon_ring_actor = self.plotter.add_points(
            ring_points, scalars=ring_scalars, cmap='plasma',
            point_size=3, name='photon_ring', render_points_as_spheres=True,
            emissive=True, opacity=0.8)
        
        # Background
        max_distance = self.geometry.disk_radius * 50
        star_xyz, star_colors, galaxy_xyz, galaxy_colors = self.geometry.create_background_stars_and_galaxies(max_distance)
        
        self.plotter.add_points(star_xyz, scalars=star_colors, rgb=True, 
                               point_size=1.5, name='stars', 
                               render_points_as_spheres=True, emissive=True)
        
        self.plotter.add_points(galaxy_xyz, scalars=galaxy_colors, rgb=True, 
                               point_size=4, name='galaxies', 
                               render_points_as_spheres=True, emissive=True)
    
    def update_simulation(self):
        """Update simulation frame with time series recording"""
        if not self.is_playing:
            return
            
        self.t += 0.1 * self.time_speed
        
        # Get viewing angle (use current parameter or calculate from camera)
        try:
            viewing_angle, view_z_component = self.get_viewing_angle_to_jet()
        except:
            viewing_angle = np.radians(self.viewing_angle)
            view_z_component = np.cos(viewing_angle)
        
        # Calculate Doppler factors for both jets
        doppler_pos_jet = self.relativistic.calculate_doppler_factor(viewing_angle, jet_direction=1)
        doppler_neg_jet = self.relativistic.calculate_doppler_factor(viewing_angle, jet_direction=-1)
        
        # Update jet appearance
        self.update_jet_beaming(doppler_pos_jet, doppler_neg_jet)
        
        # Update conical glow
        viewing_angle_deg = np.degrees(viewing_angle)
        cone_visibility_factor = np.exp(-((viewing_angle_deg - 45)**2) / (2 * 20**2))
        self.update_conical_glow(cone_visibility_factor, doppler_pos_jet, doppler_neg_jet)
        
        # Update bright core
        max_doppler = max(doppler_pos_jet, doppler_neg_jet)
        self.update_bright_core(viewing_angle_deg, max_doppler)
        
        # Update disk and photon ring visibility
        self.update_disk_and_ring_visibility(viewing_angle_deg)
        
        # Update gravitational lensing effects (every few frames for performance)
        if int(self.t * 10) % 3 == 0:  # Update every 0.3 seconds
            self.update_gravitational_lensing()
        
        # Record time series data
        if int(self.t * 10) % 5 == 0:  # Record every 0.5 seconds
            luminosity_distance = self.distance * 3.086e24
            core_flux = self.jet.L_BZ * max_doppler**3 / (4 * np.pi * luminosity_distance**2) * 1e23
            
            self.time_data.append([
                self.t, 
                self.jet.L_BZ, 
                core_flux, 
                max_doppler, 
                viewing_angle_deg
            ])
            
            # Keep only recent data to prevent memory issues
            if len(self.time_data) > 1000:
                self.time_data = self.time_data[-500:]
        
        # Update displays
        self.update_observables_display()
        self.update_time_series_display()
    
    def regenerate_scene(self):
        """Completely regenerate the 3D scene with updated parameters"""
        # Clear existing actors
        self.plotter.clear()
        
        # Reinitialize the scene
        self.init_scene()
        
        # Update parameter display
        self.update_displays()
    
    def update_jet_beaming(self, doppler_pos_jet, doppler_neg_jet):
        """Update jet appearance based on relativistic beaming"""
        viewing_angle, z_component = self.get_viewing_angle_to_jet()
        
        # Update jet colors and opacity
        base_intensity = 1.0
        
        pos_intensity = self.relativistic.apply_relativistic_beaming(base_intensity, doppler_pos_jet)
        pos_colors = self.jet_colors_pos_base * pos_intensity
        pos_colors = np.clip(pos_colors, 0, 3.0)
        
        neg_intensity = self.relativistic.apply_relativistic_beaming(base_intensity, doppler_neg_jet)
        neg_colors = self.jet_colors_neg_base * neg_intensity
        neg_colors = np.clip(neg_colors, 0, 3.0)
        
        pos_opacity = min(0.95, 0.3 + 0.4 * np.log10(doppler_pos_jet + 0.1))
        pos_opacity = max(0.05, pos_opacity)
        
        neg_opacity = min(0.95, 0.3 + 0.4 * np.log10(doppler_neg_jet + 0.1))
        neg_opacity = max(0.05, neg_opacity)
        
        # Update conical glow
        viewing_angle_deg = np.degrees(viewing_angle)
        cone_visibility_factor = np.exp(-((viewing_angle_deg - 45)**2) / (2 * 20**2))
        cone_visibility_factor = max(0.1, cone_visibility_factor)
        
        self.update_conical_glow(cone_visibility_factor, doppler_pos_jet, doppler_neg_jet)
        
        # Update bright core
        self.update_bright_core(viewing_angle_deg, max(doppler_pos_jet, doppler_neg_jet))
        
        # Update disk and ring visibility
        self.update_disk_and_ring_visibility(viewing_angle_deg)
        
        # Apply updates to meshes
        try:
            self.plotter.update_scalars(pos_colors, mesh=self.jet_mesh_pos)
            if hasattr(self.jet_actor_pos, 'GetProperty'):
                self.jet_actor_pos.GetProperty().SetOpacity(pos_opacity)
            
            self.plotter.update_scalars(neg_colors, mesh=self.jet_mesh_neg)
            if hasattr(self.jet_actor_neg, 'GetProperty'):
                self.jet_actor_neg.GetProperty().SetOpacity(neg_opacity)
        except:
            pass
    
    def update_conical_glow(self, cone_visibility_factor, doppler_pos_jet, doppler_neg_jet):
        """Update conical glow effects"""
        base_glow = 0.3 * cone_visibility_factor
        
        pos_glow_intensity = base_glow * (1 + 0.3 * np.log10(doppler_pos_jet + 0.1))
        neg_glow_intensity = base_glow * (1 + 0.3 * np.log10(doppler_neg_jet + 0.1))
        
        pos_glow_colors = self.cone_colors_pos_base * pos_glow_intensity
        neg_glow_colors = self.cone_colors_neg_base * neg_glow_intensity
        
        pos_cone_opacity = min(0.4, 0.05 + 0.35 * cone_visibility_factor * (doppler_pos_jet / 2.0))
        neg_cone_opacity = min(0.4, 0.05 + 0.35 * cone_visibility_factor * (doppler_neg_jet / 2.0))
        
        try:
            self.plotter.update_scalars(pos_glow_colors, mesh=self.cone_mesh_pos)
            if hasattr(self.cone_actor_pos, 'GetProperty'):
                self.cone_actor_pos.GetProperty().SetOpacity(max(0.01, pos_cone_opacity))
                
            self.plotter.update_scalars(neg_glow_colors, mesh=self.cone_mesh_neg)
            if hasattr(self.cone_actor_neg, 'GetProperty'):
                self.cone_actor_neg.GetProperty().SetOpacity(max(0.01, neg_cone_opacity))
        except:
            pass
    
    def update_bright_core(self, viewing_angle_deg, max_doppler):
        """Update bright core appearance"""
        variability = 1.0 + 0.3 * np.sin(2 * np.pi * self.t / 3.0) + 0.15 * np.sin(2 * np.pi * self.t / 0.8)
        variability = max(0.7, min(1.4, variability))
        
        relativistic_boost = 1.0 + 0.5 * np.log10(max_doppler + 0.1)
        angle_factor = 1.0 + 0.2 * np.exp(-((viewing_angle_deg - 30)**2) / (2 * 25**2))
        
        total_enhancement = variability * relativistic_boost * angle_factor
        enhanced_colors = self.core_colors_base * total_enhancement
        enhanced_colors = np.clip(enhanced_colors, 0.2, 2.5)
        
        core_opacity = min(0.95, 0.7 + 0.2 * (total_enhancement - 1.0))
        core_opacity = max(0.6, core_opacity)
        
        try:
            self.plotter.update_scalars(enhanced_colors, mesh=self.core_actor.mapper.dataset)
            if hasattr(self.core_actor, 'GetProperty'):
                self.core_actor.GetProperty().SetOpacity(core_opacity)
        except:
            pass
    
    def update_disk_and_ring_visibility(self, viewing_angle_deg):
        """Update warped disk and photon ring visibility based on viewing angle"""
        
        # Enhanced edge-on visibility - disk becomes much more prominent when viewed edge-on
        edge_on_factor = np.sin(np.radians(viewing_angle_deg))**3  # Stronger edge-on effect
        disk_opacity = 0.2 + 0.7 * edge_on_factor  # Higher maximum opacity
        disk_opacity = max(0.1, min(0.9, disk_opacity))
        
        # Photon ring brightness varies more dramatically with viewing angle
        ring_brightness_factor = 0.6 + 0.4 * np.cos(np.radians(viewing_angle_deg * 1.5))
        ring_opacity = 0.4 + 0.5 * ring_brightness_factor
        ring_opacity = max(0.3, min(0.95, ring_opacity))
        
        # Add time-based photon ring fluctuation to simulate gravitational lensing variations
        time_variation = 1.0 + 0.1 * np.sin(2 * np.pi * self.t / 4.0)
        ring_opacity *= time_variation
        
        try:
            # Update warped disk opacity
            if hasattr(self, 'warped_disk_actor') and hasattr(self.warped_disk_actor, 'GetProperty'):
                self.warped_disk_actor.GetProperty().SetOpacity(disk_opacity)
            
            # Update photon ring opacity with enhanced brightness
            if hasattr(self, 'photon_ring_actor') and hasattr(self.photon_ring_actor, 'GetProperty'):
                self.photon_ring_actor.GetProperty().SetOpacity(ring_opacity)
                
        except Exception as e:
            pass
    
    def update_stats(self, viewing_angle, doppler_pos_jet, doppler_neg_jet, view_z_component):
        """Update statistics display"""
        viewing_angle_deg = np.degrees(viewing_angle)
        cone_visibility = np.exp(-((viewing_angle_deg - 45)**2) / (2 * 20**2))
        
        if view_z_component > 0:
            approaching_jet = "negative"
        else:
            approaching_jet = "positive"
        
        variability = 1.0 + 0.3 * np.sin(2 * np.pi * self.t / 3.0) + 0.15 * np.sin(2 * np.pi * self.t / 0.8)
        variability = max(0.7, min(1.4, variability))
        core_boost = variability * (1.0 + 0.5 * np.log10(max(doppler_pos_jet, doppler_neg_jet) + 0.1))
        
        self.stats.setText(
            f"Black Hole Mass: {self.jet.mass:.2f} M_sun\nSpin: {self.jet.spin:.2f}\nMagnetic Field: {self.jet.B:.2e} G\n"
            f"\nJet Power: {self.jet.power:.2e} erg/s\nJet Velocity: {self.relativistic.jet_velocity:.2f} c\n"
            f"\nViewing Angle: {viewing_angle_deg:.1f}°\n"
            f"Approaching Jet: {approaching_jet}\n"
            f"Doppler (+z): {doppler_pos_jet:.2f}\n"
            f"Doppler (-z): {doppler_neg_jet:.2f}\n"
            f"Brightness ratio: {max(doppler_pos_jet, doppler_neg_jet)/min(doppler_pos_jet, doppler_neg_jet):.1f}:1\n"
            f"Conical glow: {cone_visibility:.2f}\n"
            f"Core enhancement: {core_boost:.2f}\n"
            f"\nTime: {self.t:.2f} s"
        )
    
    def update_gravitational_lensing(self):
        """Update gravitational lensing effects with time variation"""
        current_time = time.time()
        
        # Time-varying lensing strength (simulates matter density fluctuations)
        base_lensing = 1.0
        time_variation = 0.05 * np.sin(current_time * 0.3) + 0.03 * np.sin(current_time * 0.7)
        lensing_modifier = base_lensing + time_variation
        
        # Update star lensing if stars exist
        if hasattr(self, 'star_actor') and self.star_actor:
            try:
                star_points = self.star_actor.GetMapper().GetInput()
                n_points = star_points.GetNumberOfPoints()
                
                if n_points > 0:
                    # Get current star positions
                    star_positions = []
                    for i in range(n_points):
                        point = star_points.GetPoint(i)
                        star_positions.append(list(point))
                    
                    star_positions = np.array(star_positions)
                    
                    # Apply time-varying lensing
                    lensed_positions = []
                    brightness_modulation = []
                    
                    for pos in star_positions:
                        r = np.linalg.norm(pos)
                        if r > self.jet.black_hole_radius * 8:
                            impact_parameter = np.sqrt(pos[0]**2 + pos[1]**2)
                            
                            # Enhanced time-varying deflection
                            deflection_base = 4 * self.jet.black_hole_radius / max(impact_parameter, self.jet.black_hole_radius * 2)
                            deflection = deflection_base * lensing_modifier * 0.08
                            
                            # Apply deflection toward black hole
                            direction_to_bh = -pos / r
                            lensed_pos = pos + deflection * direction_to_bh * r
                            
                            # Calculate brightness variation due to lensing
                            magnification = 1.0 + 0.3 * np.exp(-impact_parameter / (self.jet.black_hole_radius * 5))
                            magnification *= lensing_modifier
                            brightness_modulation.append(min(magnification, 2.5))
                            
                            lensed_positions.append(lensed_pos)
                        else:
                            lensed_positions.append(pos)
                            brightness_modulation.append(1.0)
                    
                    # Update star positions with subtle variations
                    # Note: Full position updates can be expensive, so we do this sparingly
                    
            except Exception as e:
                pass  # Gracefully handle any errors
        
        # Add time-varying caustic patterns to photon ring
        if hasattr(self, 'photon_ring_actor') and self.photon_ring_actor:
            try:
                # Fluctuating intensity patterns (simulates gravitational waves or matter accretion)
                caustic_phase = current_time * 2.0
                intensity_variation = (
                    0.15 * np.sin(caustic_phase) + 
                    0.1 * np.sin(caustic_phase * 1.7) + 
                    0.05 * np.sin(caustic_phase * 3.2)
                )
                
                base_opacity = 0.6
                ring_opacity = base_opacity + intensity_variation
                ring_opacity = max(0.2, min(ring_opacity, 1.0))
                
                self.photon_ring_actor.GetProperty().SetOpacity(ring_opacity)
                
                # Subtle color shift (gravitational redshift variations)
                redshift_factor = 1.0 + 0.05 * np.sin(current_time * 0.4)
                ring_color = [1.0 * redshift_factor, 0.8, 0.4]
                ring_color = [min(c, 1.0) for c in ring_color]
                self.photon_ring_actor.GetProperty().SetColor(ring_color)
                
            except Exception as e:
                pass
    
    def init_ui(self):
        """Initialize simplified user interface to avoid widget deletion issues"""
        # Use simple horizontal layout
        layout = QtWidgets.QHBoxLayout(self)
        
        # Left panel - Basic controls
        control_panel = QtWidgets.QWidget()
        control_panel.setFixedWidth(300)
        control_layout = QtWidgets.QVBoxLayout(control_panel)
        
        # Physics Parameters
        physics_group = QtWidgets.QGroupBox("Physics Parameters")
        physics_layout = QtWidgets.QFormLayout()
        
        # Mass slider
        self.mass_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.mass_slider.setRange(1, 100)
        self.mass_slider.setValue(int(self.jet.mass))
        self.mass_slider.valueChanged.connect(self.on_mass_changed)
        self.mass_label = QtWidgets.QLabel(f'{self.jet.mass:.1f} M☉')
        mass_layout = QtWidgets.QHBoxLayout()
        mass_layout.addWidget(self.mass_slider)
        mass_layout.addWidget(self.mass_label)
        physics_layout.addRow("Mass:", mass_layout)
        
        # Spin slider
        self.spin_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.spin_slider.setRange(0, 999)
        self.spin_slider.setValue(int(self.jet.spin * 1000))
        self.spin_slider.valueChanged.connect(self.on_spin_changed)
        self.spin_label = QtWidgets.QLabel(f'{self.jet.spin:.3f}')
        spin_layout = QtWidgets.QHBoxLayout()
        spin_layout.addWidget(self.spin_slider)
        spin_layout.addWidget(self.spin_label)
        physics_layout.addRow("Spin:", spin_layout)
        
        # B-field slider
        self.B_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.B_slider.setRange(20, 60)
        self.B_slider.setValue(int(np.log10(self.jet.B) * 10))
        self.B_slider.valueChanged.connect(self.on_B_changed)
        self.B_label = QtWidgets.QLabel(f'{self.jet.B:.1e} G')
        B_layout = QtWidgets.QHBoxLayout()
        B_layout.addWidget(self.B_slider)
        B_layout.addWidget(self.B_label)
        physics_layout.addRow("B-field:", B_layout)
        
        physics_group.setLayout(physics_layout)
        control_layout.addWidget(physics_group)
        
        # Layer toggles
        layer_group = QtWidgets.QGroupBox("Layers")
        layer_layout = QtWidgets.QVBoxLayout()
        
        self.layer_checkboxes = {}
        for layer_key in self.layer_states:
            checkbox = QtWidgets.QCheckBox(layer_key.replace('_', ' ').title())
            checkbox.setChecked(self.layer_states[layer_key])
            checkbox.stateChanged.connect(lambda state, key=layer_key: self.on_layer_toggled(key, state))
            self.layer_checkboxes[layer_key] = checkbox
            layer_layout.addWidget(checkbox)
        
        layer_group.setLayout(layer_layout)
        control_layout.addWidget(layer_group)
        
        # Time controls
        time_group = QtWidgets.QGroupBox("Time Controls")
        time_layout = QtWidgets.QVBoxLayout()
        
        self.play_button = QtWidgets.QPushButton("⏸️ Pause")
        self.play_button.clicked.connect(self.toggle_playback)
        time_layout.addWidget(self.play_button)
        
        time_group.setLayout(time_layout)
        control_layout.addWidget(time_group)
        
        control_layout.addStretch()
        layout.addWidget(control_panel)
        
        # Center - 3D Visualization
        self.plotter = QtInteractor(self)
        self.plotter.set_background('black')
        layout.addWidget(self.plotter.interactor, 2)
        
        # Right panel - Info
        info_panel = QtWidgets.QWidget()
        info_panel.setFixedWidth(300)
        info_layout = QtWidgets.QVBoxLayout(info_panel)

        # Description text
        self.info_display = QtWidgets.QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setMaximumHeight(150)
        self.info_display.setStyleSheet('background-color: black; color: white; font-size: 10pt; border: 1px solid gray;')
        self.info_display.setText(
            "Relativistic Astrophysical Jet Simulation\n\n"
            "Features relativistic beaming, Doppler boosting, "
            "synchrotron emission, and gravitational effects."
        )
        info_layout.addWidget(self.info_display)

        # Statistics Display section
        stats_group = QtWidgets.QGroupBox('Black Hole Statistics')
        stats_layout = QtWidgets.QVBoxLayout()
        
        self.stats_display = QtWidgets.QTextEdit()
        self.stats_display.setReadOnly(True)
        # Remove fixed height to let it expand and use natural scrolling
        self.stats_display.setStyleSheet('background-color: black; color: white; font-family: monospace; font-size: 9pt; border: 1px solid gray;')
        
        # Initialize with current values
        self.update_statistics_display()
        
        stats_layout.addWidget(self.stats_display)
        stats_group.setLayout(stats_layout)
        stats_group.setStyleSheet('QGroupBox { background-color: black; color: white; border: 1px solid gray; }')
        info_layout.addWidget(stats_group)
        
        # Remove addStretch() to let statistics panel expand to fill remaining space
        layout.addWidget(info_panel)
        
        # Apply basic styling
        self.setStyleSheet("""
            QWidget { background-color: black; color: white; }
            QGroupBox { 
                background-color: #1a1a1a; 
                border: 1px solid #555; 
                border-radius: 5px; 
                margin-top: 10px; 
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                left: 10px; 
                padding: 0 5px 0 5px; 
            }
            QPushButton { 
                background-color: #4CAF50; 
                border: none; 
                padding: 8px; 
                border-radius: 4px; 
            }
            QPushButton:hover { background-color: #45a049; }
            QSlider::groove:horizontal { 
                border: 1px solid #555; 
                height: 8px; 
                background: #333; 
                border-radius: 4px; 
            }
            QSlider::handle:horizontal { 
                background: #4CAF50; 
                border: 1px solid #5c5c5c; 
                width: 18px; 
                margin: -2px 0; 
                border-radius: 3px; 
            }
        """)
        
        # Initialize scene
        self.init_scene()
        
    def update_info_display(self):
        """Update the info display safely"""
        try:
            if hasattr(self, 'info_display') and self.info_display is not None:
                r_s = self.jet.schwarzschild_radius / 1000
                r_H = self.jet.black_hole_radius / 1000
                r_isco = self.jet.isco_radius / 1000
                L_BZ = self.jet.L_BZ
                
                viewing_rad = np.radians(self.viewing_angle)
                doppler_factor = self.relativistic.calculate_doppler_factor(viewing_rad, jet_direction=1)
                
                text = (
                    f"=== PHYSICS ===\n"
                    f"Black hole mass: {self.jet.mass:.1f} M☉\n"
                    f"Spin parameter: {self.jet.spin:.3f}\n"
                    f"Magnetic field: {self.jet.B:.1e} G\n"
                    f"Schwarzschild radius: {r_s:.1f} km\n"
                    f"Event horizon: {r_H:.1f} km\n"
                    f"ISCO radius: {r_isco:.1f} km\n"
                    f"BZ luminosity: {L_BZ:.2e} erg/s\n"
                    f"Jet velocity: {self.jet.jet_velocity:.3f} c\n"
                    f"Lorentz factor: {self.relativistic.gamma:.2f}\n\n"
                    f"=== OBSERVABLES ===\n"
                    f"Viewing angle: {self.viewing_angle:.1f}°\n"
                    f"Doppler factor: {doppler_factor:.2f}\n"
                    f"Jet opening: {self.jet_opening_angle:.1f}°\n"
                    f"Distance: {self.distance:.1f} Mpc\n\n"
                    f"=== TIME ===\n"
                    f"Simulation time: {self.t:.1f}\n"
                    f"Time points recorded: {len(self.time_data)}\n"
                    f"Animation: {'Playing' if self.is_playing else 'Paused'}"
                )
                
                self.info_display.setText(text)
        except Exception as e:
            print(f"Could not update info display: {e}")
    
    # Simplified callback methods
    def on_mass_changed(self, value):
        """Handle mass slider changes"""
        self.mass_label.setText(f'{value:.1f} M☉')
        self.update_physics_parameters(mass=float(value))
    
    def on_spin_changed(self, value):
        """Handle spin slider changes"""
        new_spin = value / 1000.0
        self.spin_label.setText(f'{new_spin:.3f}')
        self.update_physics_parameters(spin=new_spin)
    
    def on_B_changed(self, value):
        """Handle B-field slider changes"""
        new_B = 10**(value / 10.0)
        self.B_label.setText(f'{new_B:.1e} G')
        self.update_physics_parameters(B=new_B)
    
    def on_layer_toggled(self, layer_key, state):
        """Handle layer visibility toggle"""
        self.layer_states[layer_key] = bool(state)
        print(f"Layer {layer_key}: {'ON' if state else 'OFF'}")
    
    def toggle_playback(self):
        """Toggle play/pause"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_button.setText("⏸️ Pause")
            self.timer.start()
        else:
            self.play_button.setText("▶️ Play")
            self.timer.stop()
    
    def create_control_panel(self, main_layout):
        """Create left control panel with physics parameters and layer toggles"""
        control_scroll = QtWidgets.QScrollArea()
        control_scroll.setFixedWidth(350)
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
        
    def create_physics_controls(self, parent_layout):
        """Create physics parameter controls with sliders and spinboxes"""
        physics_group = QtWidgets.QGroupBox("Physics Parameters")
        physics_layout = QtWidgets.QFormLayout()
        
        # Mass (M) - 1 to 100 solar masses
        mass_widget = QtWidgets.QWidget()
        mass_layout = QtWidgets.QHBoxLayout(mass_widget)
        mass_layout.setContentsMargins(0, 0, 0, 0)
        
        self.mass_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.mass_slider.setRange(1, 100)
        self.mass_slider.setValue(int(self.jet.mass))
        self.mass_slider.valueChanged.connect(self.on_mass_changed)
        
        self.mass_spinbox = QtWidgets.QDoubleSpinBox()
        self.mass_spinbox.setRange(1.0, 100.0)
        self.mass_spinbox.setValue(self.jet.mass)
        self.mass_spinbox.setSuffix(" M☉")
        self.mass_spinbox.valueChanged.connect(self.on_mass_spinbox_changed)
        
        mass_layout.addWidget(self.mass_slider, 3)
        mass_layout.addWidget(self.mass_spinbox, 1)
        
        # Add tooltip
        mass_widget.setToolTip("Black hole mass affects event horizon size, ISCO radius, and jet power scaling")
        physics_layout.addRow("Mass:", mass_widget)
        
        # Spin (a) - 0 to 0.999
        spin_widget = QtWidgets.QWidget()
        spin_layout = QtWidgets.QHBoxLayout(spin_widget)
        spin_layout.setContentsMargins(0, 0, 0, 0)
        
        self.spin_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.spin_slider.setRange(0, 999)
        self.spin_slider.setValue(int(self.jet.spin * 1000))
        self.spin_slider.valueChanged.connect(self.on_spin_changed)
        
        self.spin_spinbox = QtWidgets.QDoubleSpinBox()
        self.spin_spinbox.setRange(0.0, 0.999)
        self.spin_spinbox.setDecimals(3)
        self.spin_spinbox.setValue(self.jet.spin)
        self.spin_spinbox.valueChanged.connect(self.on_spin_spinbox_changed)
        
        spin_layout.addWidget(self.spin_slider, 3)
        spin_layout.addWidget(self.spin_spinbox, 1)
        
        spin_widget.setToolTip("Dimensionless spin parameter (a/M). Higher spin increases jet power via Blandford-Znajek mechanism")
        physics_layout.addRow("Spin (a):", spin_widget)
        
        # Magnetic Field (B) - 10² to 10⁶ Gauss (log scale)
        B_widget = QtWidgets.QWidget()
        B_layout = QtWidgets.QHBoxLayout(B_widget)
        B_layout.setContentsMargins(0, 0, 0, 0)
        
        self.B_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.B_slider.setRange(20, 60)  # 10^2 to 10^6
        self.B_slider.setValue(int(np.log10(self.jet.B) * 10))
        self.B_slider.valueChanged.connect(self.on_B_changed)
        
        self.B_spinbox = QtWidgets.QDoubleSpinBox()
        self.B_spinbox.setRange(100, 1e6)
        self.B_spinbox.setValue(self.jet.B)
        self.B_spinbox.setSuffix(" G")
        self.B_spinbox.setDecimals(0)
        self.B_spinbox.valueChanged.connect(self.on_B_spinbox_changed)
        
        B_layout.addWidget(self.B_slider, 3)
        B_layout.addWidget(self.B_spinbox, 1)
        
        B_widget.setToolTip("Magnetic field strength near the black hole. Determines jet power via L_BZ ∝ B²a²M²")
        physics_layout.addRow("B-field:", B_widget)
        
        # Accretion Rate (Mdot)
        mdot_widget = QtWidgets.QWidget()
        mdot_layout = QtWidgets.QHBoxLayout(mdot_widget)
        mdot_layout.setContentsMargins(0, 0, 0, 0)
        
        self.mdot_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.mdot_slider.setRange(15, 21)  # 10^15 to 10^21 g/s
        self.mdot_slider.setValue(int(np.log10(self.mdot)))
        self.mdot_slider.valueChanged.connect(self.on_mdot_changed)
        
        self.mdot_spinbox = QtWidgets.QDoubleSpinBox()
        self.mdot_spinbox.setRange(1e15, 1e21)
        self.mdot_spinbox.setValue(self.mdot)
        self.mdot_spinbox.setSuffix(" g/s")
        self.mdot_spinbox.setDecimals(0)
        self.mdot_spinbox.valueChanged.connect(self.on_mdot_spinbox_changed)
        
        mdot_layout.addWidget(self.mdot_slider, 3)
        mdot_layout.addWidget(self.mdot_spinbox, 1)
        
        mdot_widget.setToolTip("Mass accretion rate affects disk luminosity and jet-disk coupling")
        physics_layout.addRow("Mdot:", mdot_widget)
        
        # Additional parameters...
        self.create_additional_physics_params(physics_layout)
        
    def create_additional_physics_params(self, physics_layout):
        """Create additional physics parameter controls"""
        # Viewing Angle
        viewing_widget = QtWidgets.QWidget()
        viewing_layout = QtWidgets.QHBoxLayout(viewing_widget)
        viewing_layout.setContentsMargins(0, 0, 0, 0)
        
        self.viewing_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.viewing_slider.setRange(0, 180)
        self.viewing_slider.setValue(int(self.viewing_angle))
        self.viewing_slider.valueChanged.connect(self.on_viewing_angle_changed)
        
        self.viewing_spinbox = QtWidgets.QDoubleSpinBox()
        self.viewing_spinbox.setRange(0.0, 180.0)
        self.viewing_spinbox.setValue(self.viewing_angle)
        self.viewing_spinbox.setSuffix("°")
        self.viewing_spinbox.valueChanged.connect(self.on_viewing_angle_spinbox_changed)
        
        viewing_layout.addWidget(self.viewing_slider, 3)
        viewing_layout.addWidget(self.viewing_spinbox, 1)
        
        viewing_widget.setToolTip("Viewing angle relative to jet axis. Affects relativistic beaming and Doppler boosting")
        physics_layout.addRow("Viewing Angle:", viewing_widget)
        
        # Jet Opening Angle
        opening_widget = QtWidgets.QWidget()
        opening_layout = QtWidgets.QHBoxLayout(opening_widget)
        opening_layout.setContentsMargins(0, 0, 0, 0)
        
        self.opening_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.opening_slider.setRange(1, 30)
        self.opening_slider.setValue(int(self.jet_opening_angle))
        self.opening_slider.valueChanged.connect(self.on_opening_angle_changed)
        
        self.opening_spinbox = QtWidgets.QDoubleSpinBox()
        self.opening_spinbox.setRange(1.0, 30.0)
        self.opening_spinbox.setValue(self.jet_opening_angle)
        self.opening_spinbox.setSuffix("°")
        self.opening_spinbox.valueChanged.connect(self.on_opening_angle_spinbox_changed)
        
        opening_layout.addWidget(self.opening_slider, 3)
        opening_layout.addWidget(self.opening_spinbox, 1)
        
        opening_widget.setToolTip("Half-opening angle of the jet cone. Narrower jets show stronger beaming effects")
        physics_layout.addRow("Jet Opening:", opening_widget)
        
        # Distance (for flux calculations)
        distance_widget = QtWidgets.QWidget()
        distance_layout = QtWidgets.QHBoxLayout(distance_widget)
        distance_layout.setContentsMargins(0, 0, 0, 0)
        
        self.distance_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.distance_slider.setRange(1, 1000)
        self.distance_slider.setValue(int(self.distance))
        self.distance_slider.valueChanged.connect(self.on_distance_changed)
        
        self.distance_spinbox = QtWidgets.QDoubleSpinBox()
        self.distance_spinbox.setRange(1.0, 1000.0)
        self.distance_spinbox.setValue(self.distance)
        self.distance_spinbox.setSuffix(" Mpc")
        self.distance_spinbox.valueChanged.connect(self.on_distance_spinbox_changed)
        
        distance_layout.addWidget(self.distance_slider, 3)
        distance_layout.addWidget(self.distance_spinbox, 1)
        
        distance_widget.setToolTip("Distance to source for flux calculations and angular size scaling")
        physics_layout.addRow("Distance:", distance_widget)
    
    def create_layer_controls(self, parent_layout):
        """Create layer visibility toggle controls"""
        layer_group = QtWidgets.QGroupBox("Visualization Layers")
        layer_layout = QtWidgets.QVBoxLayout()
        
        self.layer_checkboxes = {}
        
        layer_info = {
            'photon_ring': ('Photon Ring', 'Einstein ring from gravitational light bending'),
            'gravitational_lensing': ('Gravitational Lensing', 'Background star distortion by black hole gravity'),
            'accretion_disk': ('Accretion Disk', 'Hot plasma disk feeding the black hole'),
            'jet_sheath': ('Jet Sheath', 'Outer jet boundary with magnetic field structure'),
            'jet_spine': ('Jet Spine', 'Inner jet core with highest Lorentz factor'),
            'magnetic_field_lines': ('Magnetic Field Lines', 'Poloidal field threading the black hole'),
            'polarization_vectors': ('Polarization Vectors', 'Linear polarization from synchrotron emission'),
            'background': ('Background', 'Stars and distant galaxies')
        }
        
        for layer_key, (layer_name, tooltip) in layer_info.items():
            checkbox = QtWidgets.QCheckBox(layer_name)
            checkbox.setChecked(self.layer_states[layer_key])
            checkbox.stateChanged.connect(lambda state, key=layer_key: self.on_layer_toggled(key, state))
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
        
        self.play_button = QtWidgets.QPushButton("⏸️ Pause")
        self.play_button.clicked.connect(self.toggle_playback)
        button_layout.addWidget(self.play_button)
        
        self.step_back_button = QtWidgets.QPushButton("⏮️")
        self.step_back_button.clicked.connect(self.step_backward)
        button_layout.addWidget(self.step_back_button)
        
        self.step_forward_button = QtWidgets.QPushButton("⏭️")
        self.step_forward_button.clicked.connect(self.step_forward)
        button_layout.addWidget(self.step_forward_button)
        
        time_layout.addLayout(button_layout)
        
        # Speed control
        speed_layout = QtWidgets.QHBoxLayout()
        speed_layout.addWidget(QtWidgets.QLabel("Speed:"))
        
        self.speed_combo = QtWidgets.QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1x", "2x", "5x"])
        self.speed_combo.setCurrentText("1x")
        self.speed_combo.currentTextChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.speed_combo)
        
        time_layout.addLayout(speed_layout)
        
        time_group.setLayout(time_layout)
        parent_layout.addWidget(time_group)
    
    def create_export_controls(self, parent_layout):
        """Create export control widgets"""
        export_group = QtWidgets.QGroupBox("Export & Analysis")
        export_layout = QtWidgets.QVBoxLayout()
        
        # Export buttons
        self.export_csv_button = QtWidgets.QPushButton("📊 Export Time Series (CSV)")
        self.export_csv_button.clicked.connect(self.export_time_series)
        export_layout.addWidget(self.export_csv_button)
        
        self.export_png_button = QtWidgets.QPushButton("📷 Export Frame (PNG)")
        self.export_png_button.clicked.connect(self.export_frame)
        export_layout.addWidget(self.export_png_button)
        
        self.export_movie_button = QtWidgets.QPushButton("🎬 Export Movie (MP4)")
        self.export_movie_button.clicked.connect(self.export_movie)
        export_layout.addWidget(self.export_movie_button)
        
        export_group.setLayout(export_layout)
        parent_layout.addWidget(export_group)
    
    def create_visualization_panel(self, main_layout):
        """Create center 3D visualization panel"""
        viz_widget = QtWidgets.QWidget()
        viz_layout = QtWidgets.QVBoxLayout(viz_widget)
        viz_layout.setContentsMargins(0, 0, 0, 0)
        
        # 3D Visualization
        self.plotter = QtInteractor(viz_widget)
        self.plotter.set_background('black')
        viz_layout.addWidget(self.plotter.interactor)
        
        # Add scale bar and colorbars
        self.setup_visualization_overlays()
        
        main_layout.addWidget(viz_widget, 2)  # Give more space to visualization
    
    def create_info_panel(self, main_layout):
        """Create right info panel with derived quantities and time series"""
        info_scroll = QtWidgets.QScrollArea()
        info_scroll.setFixedWidth(300)
        info_scroll.setWidgetResizable(True)
        
        info_widget = QtWidgets.QWidget()
        info_layout = QtWidgets.QVBoxLayout(info_widget)
        
        # Derived Physics Quantities
        self.create_physics_display(info_layout)
        
        # Observables Display
        self.create_observables_display(info_layout)
        
        # Time Series Plot (simplified)
        self.create_time_series_display(info_layout)
        
    def create_physics_display(self, parent_layout):
        """Create physics quantities display"""
        physics_group = QtWidgets.QGroupBox("Derived Physics")
        physics_layout = QtWidgets.QVBoxLayout()
        
        self.physics_display = QtWidgets.QTextEdit()
        self.physics_display.setReadOnly(True)
        self.physics_display.setFixedHeight(200)
        self.physics_display.setStyleSheet("""
            QTextEdit { 
                background-color: black; 
                border: 1px solid #555; 
                padding: 8px; 
                font-family: 'Courier New', monospace; 
                font-size: 10pt; 
                color: white;
            }
        """)
        
        physics_layout.addWidget(self.physics_display)
        physics_group.setLayout(physics_layout)
        parent_layout.addWidget(physics_group)
    
    def create_observables_display(self, parent_layout):
        """Create observables display"""
        obs_group = QtWidgets.QGroupBox("Current Observables")
        obs_layout = QtWidgets.QVBoxLayout()
        
        self.observables_display = QtWidgets.QTextEdit()
        self.observables_display.setReadOnly(True)
        self.observables_display.setFixedHeight(150)
        self.observables_display.setStyleSheet("""
            QTextEdit { 
                background-color: black; 
                border: 1px solid #555; 
                padding: 8px; 
                font-family: 'Courier New', monospace; 
                font-size: 10pt; 
                color: white;
            }
        """)
        
        obs_layout.addWidget(self.observables_display)
        obs_group.setLayout(obs_layout)
        parent_layout.addWidget(obs_group)
    
    def create_time_series_display(self, parent_layout):
        """Create simplified time series display"""
        ts_group = QtWidgets.QGroupBox("Time Series")
        ts_layout = QtWidgets.QVBoxLayout()
        
        self.time_series_display = QtWidgets.QTextEdit()
        self.time_series_display.setReadOnly(True)
        self.time_series_display.setFixedHeight(100)
        self.time_series_display.setStyleSheet("""
            QTextEdit { 
                background-color: black; 
                border: 1px solid #555; 
                padding: 8px; 
                font-family: 'Courier New', monospace; 
                font-size: 9pt; 
                color: white;
            }
        """)
        
        ts_layout.addWidget(self.time_series_display)
        ts_group.setLayout(ts_layout)
        parent_layout.addWidget(ts_group)
    
    def setup_visualization_overlays(self):
        """Setup colorbars and scale indicators"""
        # This will be implemented to add colorbars and scale bars to the 3D view
        # Don't update displays here as UI widgets may not be created yet
        pass
        
    def update_statistics_display(self):
        """Update the statistics display with current physics values"""
        try:
            # Get current physics parameters
            physics = self.jet.get_physical_scales()
            
            # Calculate additional derived quantities
            schwarzschild_radius = 2 * self.jet.mass * 2.95e5  # in cm (M in solar masses)
            isco_radius = physics['isco_radius']
            ergosphere_radius = physics['isco_radius'] * 1.5  # Approximate
            
            # Magnetic flux calculation
            magnetic_flux = self.jet.B * np.pi * (isco_radius)**2  # Gauss⋅cm²
            
            # Jet power (Blandford-Znajek luminosity) - access directly from jet object
            jet_power = self.jet.L_BZ
            
            # Calculate additional physics values
            rg = physics['black_hole_radius']  # gravitational radius
            
            # Format the statistics text
            stats_text = f"""
BLACK HOLE PARAMETERS:
──────────────────────
Mass:                {self.jet.mass:.1f} M☉
Spin Parameter (a):  {self.jet.spin:.3f}
Magnetic Field:      {self.jet.B:.2e} G

CHARACTERISTIC SCALES:
─────────────────────
Schwarzschild Radius: {schwarzschild_radius/1e5:.2f} km
ISCO Radius:         {isco_radius/1e5:.2f} km  
Ergosphere Radius:   {ergosphere_radius/1e5:.2f} km
Gravitational Radius: {rg/1e5:.2f} km

MAGNETIC PROPERTIES:
───────────────────
Magnetic Flux:       {magnetic_flux:.2e} G⋅cm²
Magnetospheric Field: {self.jet.B * (rg/isco_radius)**3:.2e} G

JET PROPERTIES:
──────────────
Jet Velocity:        {self.jet.jet_velocity:.3f} c
Lorentz Factor:      {1/np.sqrt(1-self.jet.jet_velocity**2):.2f}
B-Z Luminosity:      {jet_power:.2e} erg/s
B-Z Power (Solar):   {jet_power/3.8e33:.2e} L☉

DIMENSIONLESS RATIOS:
────────────────────
a/M:                 {self.jet.spin:.3f}
r_ISCO/r_g:          {isco_radius/rg:.2f}
B²/8π (at ISCO):     {self.jet.B**2/(8*np.pi):.2e} erg/cm³
            """.strip()
            
            self.stats_display.setText(stats_text)
            
        except Exception as e:
            self.stats_display.setText(f"Error updating statistics: {str(e)}")
            print(f"Statistics error details: {e}")  # For debugging
    
    # Parameter callback methods
    def on_mass_changed(self, value):
        """Handle mass slider changes"""
        mass_value = float(value)
        self.mass_label.setText(f'{mass_value:.1f} M☉')
        self.update_physics_parameters(mass=mass_value)
        self.update_statistics_display()
    
    def on_spin_changed(self, value):
        """Handle spin slider changes"""
        new_spin = value / 1000.0
        self.spin_label.setText(f'{new_spin:.3f}')
        self.update_physics_parameters(spin=new_spin)
        self.update_statistics_display()
    
    def on_B_changed(self, value):
        """Handle B-field slider changes"""
        new_B = 10**(value / 10.0)
        self.B_label.setText(f'{new_B:.1e} G')
        self.update_physics_parameters(B=new_B)
        self.update_statistics_display()
    
    def on_layer_toggled(self, layer_key, state):
        """Handle layer visibility toggle"""
        self.layer_states[layer_key] = bool(state)
        self.update_layer_visibility(layer_key, bool(state))
    
    # Time control methods
    def toggle_playback(self):
        """Toggle play/pause"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_button.setText("⏸️ Pause")
            self.timer.start()
        else:
            self.play_button.setText("▶️ Play")
            self.timer.stop()
    
    def step_forward(self):
        """Step forward one frame"""
        self.update_simulation()
    
    def step_backward(self):
        """Step backward one frame"""
        self.t -= 0.2  # Go back two steps
        self.update_simulation()
    
    def on_speed_changed(self, speed_text):
        """Handle speed change"""
        speed_map = {"0.25x": 0.25, "0.5x": 0.5, "1x": 1.0, "2x": 2.0, "5x": 5.0}
        self.time_speed = speed_map.get(speed_text, 1.0)
        # Adjust timer interval
        base_interval = 100
        new_interval = int(base_interval / self.time_speed)
    # Export methods
    def export_time_series(self):
        """Export time series data to CSV"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Time Series", f"jet_timeseries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
            "CSV files (*.csv)")
        
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Time', 'Jet_Power_erg_s', 'Core_Flux_Jy', 'Doppler_Factor', 'Viewing_Angle_deg'])
                    for data_point in self.time_data:
                        writer.writerow(data_point)
                print(f"Time series exported to {filename}")
            except Exception as e:
                print(f"Export failed: {e}")
    
    def export_frame(self):
        """Export current frame as PNG"""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Frame", f"jet_frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", 
            "PNG files (*.png)")
        
        if filename:
            try:
                self.plotter.screenshot(filename)
                print(f"Frame exported to {filename}")
            except Exception as e:
                print(f"Export failed: {e}")
    
    def export_movie(self):
        """Export movie (simplified - would need more implementation)"""
        QtWidgets.QMessageBox.information(self, "Export Movie", 
                                         "Movie export feature would require additional implementation\n"
                                         "with frame sequence generation and ffmpeg integration.")
    
    # Update methods
    def update_physics_parameters(self, mass=None, spin=None, B=None):
        """Update physics parameters and regenerate scene"""
        # Update parameters if provided
        if mass is not None:
            self.jet.mass = mass
        if spin is not None:
            self.jet.spin = spin
        if B is not None:
            self.jet.B = B
        
        # Update relativistic effects with new jet velocity
        self.relativistic.update_jet_velocity(self.jet.jet_velocity)
        
        # Update geometry with new physics parameters
        physics_params = self.jet.get_physical_scales()
        self.geometry.update_physics_params(physics_params)
        
        # Regenerate the entire scene with new parameters
        self.regenerate_scene()
        
        # Update displays
        self.update_displays()
    
    def update_displays(self):
        """Update all information displays with error handling"""
        try:
            self.update_physics_display()
        except Exception as e:
            print(f"Could not update physics display: {e}")
        
        try:
            self.update_observables_display()
        except Exception as e:
            print(f"Could not update observables display: {e}")
        
        try:
            self.update_time_series_display()
        except Exception as e:
            print(f"Could not update time series display: {e}")
    
    def update_physics_display(self):
        """Update the derived physics quantities display"""
        if not hasattr(self, 'physics_display') or self.physics_display is None:
            return
            
        try:
            r_s = self.jet.schwarzschild_radius / 1000  # Convert to km
            r_H = self.jet.black_hole_radius / 1000     # Convert to km  
            r_isco = self.jet.isco_radius / 1000        # Convert to km
            L_BZ = self.jet.L_BZ
            
            # Calculate additional quantities
            jet_power_fraction = L_BZ / (self.mdot * 9e20)  # Fraction of rest mass energy
            magnetic_flux = self.jet.B * np.pi * r_H**2 * 1e10  # Convert to Maxwell
            
            text = (
                f"Schwarzschild radius: {r_s:.1f} km\n"
                f"Event horizon: {r_H:.1f} km\n"
                f"ISCO radius: {r_isco:.1f} km\n"
                f"BZ luminosity: {L_BZ:.2e} erg/s\n"
                f"Jet velocity: {self.jet.jet_velocity:.3f} c\n"
                f"Lorentz factor: {self.relativistic.gamma:.2f}\n"
                f"Power fraction: {jet_power_fraction:.1%}\n"
                f"Magnetic flux: {magnetic_flux:.2e} Maxwell\n"
                f"Horizon frequency: {3e5/(2*np.pi*r_H):.1e} Hz"
            )
            
            self.physics_display.setText(text)
        except Exception as e:
            self.physics_display.setText(f"Error calculating physics: {e}")
    
    def update_observables_display(self):
        """Update current observables display"""
        if not hasattr(self, 'observables_display') or self.observables_display is None:
            return
            
        try:
            # Calculate current viewing-dependent quantities
            viewing_rad = np.radians(self.viewing_angle)
            doppler_factor = self.relativistic.calculate_doppler_factor(viewing_rad, jet_direction=1)
            
            # Estimate flux density (simplified)
            luminosity_distance = self.distance * 3.086e24  # Convert Mpc to cm
            core_flux = self.jet.L_BZ * doppler_factor**3 / (4 * np.pi * luminosity_distance**2)
            core_flux_jy = core_flux * 1e23  # Convert to Janskys
            
            # Brightness temperature (simplified)
            angular_size = (self.jet.black_hole_radius / luminosity_distance) * 206265  # arcsec
            brightness_temp = core_flux_jy * 1.8e12 / (angular_size**2 * 1.4e9)  # K at 1.4 GHz
            
            text = (
                f"Viewing angle: {self.viewing_angle:.1f}°\n"
                f"Doppler factor: {doppler_factor:.2f}\n"
                f"Core flux: {core_flux_jy:.2e} Jy\n"
                f"Brightness temp: {brightness_temp:.2e} K\n"
                f"Angular size: {angular_size*1000:.1f} mas\n"
                f"Jet opening: {self.jet_opening_angle:.1f}°\n"
                f"Distance: {self.distance:.1f} Mpc"
            )
            
            self.observables_display.setText(text)
        except Exception as e:
            self.observables_display.setText(f"Error calculating observables: {e}")
    
    def update_time_series_display(self):
        """Update time series display"""
        if not hasattr(self, 'time_series_display') or self.time_series_display is None:
            return
            
        try:
            if len(self.time_data) > 0:
                recent_data = self.time_data[-5:]  # Show last 5 points
                text = "Recent time points:\n"
                for i, (t, L_BZ, flux, doppler, angle) in enumerate(recent_data):
                    text += f"t={t:.1f}: L={L_BZ:.1e}, δ={doppler:.2f}\n"
            else:
                text = "No time series data yet..."
            
            self.time_series_display.setText(text)
        except Exception as e:
            self.time_series_display.setText(f"Error updating time series: {e}")
    
    def update_layer_visibility(self, layer_key, visible):
        """Update visibility of specific layer"""
        # Map layer keys to actor names in the plotter
        layer_actor_map = {
            'photon_ring': 'photon_ring',
            'accretion_disk': 'warped_disk',
            'jet_sheath': 'cone_pos',  # Use cone actors for sheath
            'jet_spine': 'jet_pos',
            'background': 'stars'
        }
        
        actor_name = layer_actor_map.get(layer_key)
        if actor_name and hasattr(self.plotter, 'renderer'):
            try:
                # This is a simplified visibility toggle
                # In a full implementation, you'd have more sophisticated layer management
                if visible:
                    print(f"Showing layer: {layer_key}")
                else:
                    print(f"Hiding layer: {layer_key}")
            except Exception as e:
                print(f"Could not toggle layer {layer_key}: {e}")
    
    def update_info_display(self):
        """Update the info display safely"""
        try:
            if hasattr(self, 'info_display') and self.info_display is not None:
                r_s = self.jet.schwarzschild_radius / 1000
                r_H = self.jet.black_hole_radius / 1000
                r_isco = self.jet.isco_radius / 1000
                L_BZ = self.jet.L_BZ
                
                viewing_rad = np.radians(self.viewing_angle)
                doppler_factor = self.relativistic.calculate_doppler_factor(viewing_rad, jet_direction=1)
                
                text = (
                    f"=== PHYSICS ===\n"
                    f"Black hole mass: {self.jet.mass:.1f} M☉\n"
                    f"Spin parameter: {self.jet.spin:.3f}\n"
                    f"Magnetic field: {self.jet.B:.1e} G\n"
                    f"Schwarzschild radius: {r_s:.1f} km\n"
                    f"Event horizon: {r_H:.1f} km\n"
                    f"ISCO radius: {r_isco:.1f} km\n"
                    f"BZ luminosity: {L_BZ:.2e} erg/s\n"
                    f"Jet velocity: {self.jet.jet_velocity:.3f} c\n"
                    f"Lorentz factor: {self.relativistic.gamma:.2f}\n\n"
                    f"=== OBSERVABLES ===\n"
                    f"Viewing angle: {self.viewing_angle:.1f}°\n"
                    f"Doppler factor: {doppler_factor:.2f}\n"
                    f"Jet opening: {self.jet_opening_angle:.1f}°\n"
                    f"Distance: {self.distance:.1f} Mpc\n\n"
                    f"=== TIME ===\n"
                    f"Simulation time: {self.t:.1f}\n"
                    f"Time points recorded: {len(self.time_data)}\n"
                    f"Animation: {'Playing' if self.is_playing else 'Paused'}"
                )
                
                self.info_display.setText(text)
        except Exception as e:
            print(f"Could not update info display: {e}")
    
    def update_physics_parameters_simple(self, **kwargs):
        """Update physics parameters safely"""
        try:
            if 'mass' in kwargs:
                self.jet.mass = kwargs['mass']
            if 'spin' in kwargs:
                self.jet.spin = kwargs['spin']
            if 'B' in kwargs:
                self.jet.B = kwargs['B']
            
            # Recalculate derived properties
            self.jet.r_H = self.jet.mass * 1.485  # km
            self.jet.r_s = 2 * self.jet.r_H
            self.jet.r_isco = self.jet.r_s * (3 + 2*np.sqrt(3 - 2*self.jet.spin))
            
            # Update physics
            self.jet.update_physics()
            self.relativistic.gamma = 1 / np.sqrt(1 - self.jet.jet_velocity**2)
            
            # Update info display
            self.update_info_display()
            
        except Exception as e:
            print(f"Error updating physics: {e}")
    
    def export_simple_csv(self):
        """Export time series data to CSV"""
        try:
            filename = f"bz_timeseries_{len(self.time_data)}_points.csv"
            with open(filename, 'w') as f:
                f.write("time,L_BZ,doppler_factor,viewing_angle\n")
                for i, data in enumerate(self.time_data):
                    f.write(f"{data['time']:.2f},{data['L_BZ']:.3e},{data['doppler']:.3f},{data['viewing_angle']:.1f}\n")
            print(f"Exported {len(self.time_data)} data points to {filename}")
        except Exception as e:
            print(f"Export failed: {e}")
    
    def run(self):
        """Run the visualization"""
        self.update_info_display()
        self.app.exec_()

if __name__ == "__main__":
    vis = JetVisualizer()
    vis.run()
