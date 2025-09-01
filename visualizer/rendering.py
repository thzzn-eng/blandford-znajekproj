"""
Rendering module for the Blandford-Znajek visualizer
Handles 3D scene rendering, visualization effects, and display updates
"""

import numpy as np
import pyvista as pv
from PyQt5 import QtWidgets
from pyvistaqt import QtInteractor


class RenderingEngine:
    """Handles 3D rendering and visualization effects"""
    
    def __init__(self, parent_visualizer):
        self.visualizer = parent_visualizer
        self.plotter = None
    
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
        
        # Store reference in parent
        self.visualizer.plotter = self.plotter
    
    def setup_visualization_overlays(self):
        """Setup scale bars, colorbars, and other overlays"""
        if not self.plotter:
            return
            
        # Add coordinate axes
        self.plotter.add_axes(viewport=(0, 0, 0.2, 0.2))
        
        # Setup camera
        self.plotter.camera_position = [(40, 30, 20), (0, 0, 0), (0, 0, 1)]
        self.plotter.camera.zoom(1.2)
    
    def init_scene(self):
        """Initialize the 3D scene with all components"""
        if not self.plotter:
            return
            
        try:
            # Clear existing scene
            self.plotter.clear()
            
            # Add background elements
            self.add_background_elements()
            
            # Create black hole components
            self.create_black_hole_components()
            
            # Create accretion disk
            self.create_accretion_disk()
            
            # Create jets
            self.create_jets()
            
            # Setup lighting
            self.setup_lighting()
            
            # Set up initial camera view
            self.setup_camera()
            
        except Exception as e:
            print(f"Scene initialization failed: {e}")
    
    def setup_camera(self):
        """Set up initial camera position for optimal viewing"""
        try:
            if self.plotter:
                # Position camera to see the black hole and jets clearly
                bh_radius = self.visualizer.geometry.bh_radius
                camera_distance = bh_radius * 5  # Place camera at 5 times the BH radius
                
                self.plotter.camera_position = [
                    (camera_distance, camera_distance, camera_distance),  # Camera position
                    (0, 0, 0),  # Focal point (center)
                    (0, 0, 1)   # View up vector
                ]
                
                # Set clipping planes to handle large objects
                self.plotter.camera.clipping_range = (bh_radius * 0.1, bh_radius * 50)
                
        except Exception as e:
            print(f"Camera setup failed: {e}")
            import traceback
            traceback.print_exc()
    
    def add_background_elements(self):
        """Add background stars and cosmic elements"""
        if not self.visualizer.layer_states.get('background', True):
            return
            
        try:
            # Always create the cosmic background with stars
            self.create_cosmic_background()
            
            # Legacy background stars (kept as backup)
            try:
                n_stars = 500
                bh_radius = self.visualizer.geometry.bh_radius
                star_distance = bh_radius * 80
                
                # Create random background stars
                star_positions = np.random.uniform(-star_distance, star_distance, (n_stars, 3))
                # Normalize to sphere surface
                norms = np.linalg.norm(star_positions, axis=1)
                star_positions = star_positions / norms[:, np.newaxis] * star_distance
                
                star_colors = np.random.uniform(0.4, 1.0, n_stars)
                
                # Create point cloud for stars
                star_cloud = pv.PolyData(star_positions)
                star_cloud['brightness'] = star_colors
                
                self.plotter.add_mesh(star_cloud, 
                                    point_size=2, 
                                    render_points_as_spheres=True,
                                    scalars='brightness',
                                    cmap='hot',
                                    opacity=0.7,
                                    lighting=False,
                                    name='background_stars_legacy')
            except Exception as e:
                print(f"Legacy background stars failed: {e}")
                                
        except Exception as e:
            print(f"Background creation failed: {e}")
    
    def create_black_hole_components(self):
        """Create black hole event horizon and ergosphere"""
        if not self.visualizer.layer_states.get('black_hole', True):
            return
            
        try:
            bh_radius = self.visualizer.geometry.bh_radius
            
            # Event horizon - perfectly black (no light escapes)
            event_horizon = pv.Sphere(radius=bh_radius, 
                                    center=(0, 0, 0),
                                    phi_resolution=50, 
                                    theta_resolution=50)
            
            # Make it absolutely black with no lighting
            self.plotter.add_mesh(event_horizon, 
                                color='black',  # Pure black
                                opacity=1.0,
                                lighting=False,  # No lighting on black hole
                                ambient=0.0,
                                diffuse=0.0,
                                specular=0.0,
                                name='event_horizon')
            
            # Add gravitational lensing ring at photon sphere (1.5 R_s)
            photon_radius = bh_radius * 1.5
            lensing_ring = pv.ParametricTorus(ringradius=photon_radius, 
                                            crosssectionradius=bh_radius * 0.02)
            
            # Subtle orange glow from gravitational lensing
            self.plotter.add_mesh(lensing_ring,
                                color='orange',
                                opacity=0.4,
                                lighting=True,
                                ambient=0.8,
                                name='photon_sphere')
            
            # Ergosphere (if spinning) - spacetime dragging region
            if self.visualizer.jet.spin > 0.1:
                ergo_radius = bh_radius * (1 + 0.3 * self.visualizer.jet.spin)
                ergosphere = pv.Sphere(radius=ergo_radius, center=(0, 0, 0))
                
                # Create spacetime distortion effect
                points = ergosphere.points
                r = np.linalg.norm(points, axis=1)
                distortion = np.sin(r * 10 + self.visualizer.current_time * 3) * 0.1
                ergosphere['distortion'] = distortion
                
                self.plotter.add_mesh(ergosphere,
                                    scalars='distortion',
                                    cmap='Reds',
                                    opacity=0.1,  # Very subtle
                                    lighting=False,
                                    name='ergosphere')
                                    
        except Exception as e:
            print(f"Black hole creation failed: {e}")
            import traceback
            traceback.print_exc()
    
    def create_accretion_disk(self):
        """Create spinning accretion disk based on black hole spin parameter"""
        if not self.visualizer.layer_states.get('accretion_disk', True):
            return
            
        try:
            # Get basic disk geometry
            disk_mesh, _ = self.visualizer.geometry.create_thick_accretion_disk()
            
            if disk_mesh is not None and disk_mesh.n_points > 0:
                # Calculate spinning disk properties
                points = disk_mesh.points
                distances = np.sqrt(points[:, 0]**2 + points[:, 1]**2 + points[:, 2]**2)
                bh_radius = self.visualizer.geometry.bh_radius
                
                # Simple temperature profile
                r_norm = distances / bh_radius
                temperatures = 1.0 / (r_norm + 0.1)  # Simple falloff
                temperatures = np.clip(temperatures, 0.1, 2.0)
                
                # Add rotation effects based on spin parameter
                spin_effects = self.calculate_disk_rotation(points)
                enhanced_temperatures = temperatures * (0.8 + 0.2 * spin_effects)
                
                # Set mesh properties with rotation effects
                disk_mesh['temperature'] = enhanced_temperatures
                disk_mesh['rotation'] = spin_effects
                
                # Create spinning plasma material
                self.plotter.add_mesh(disk_mesh,
                                    scalars='temperature',
                                    cmap='hot',
                                    opacity=0.8,
                                    name='accretion_disk')
                                    
        except Exception as e:
            print(f"Accretion disk creation failed: {e}")
    
    def calculate_disk_rotation(self, points):
        """Calculate rotation effects based on black hole spin parameter"""
        # Get spin parameter from the black hole
        spin = self.visualizer.jet.spin  # a parameter (0 to 0.999)
        
        # Convert to cylindrical coordinates
        r_cyl = np.sqrt(points[:, 0]**2 + points[:, 1]**2)
        theta = np.arctan2(points[:, 1], points[:, 0])
        
        bh_radius = self.visualizer.geometry.bh_radius
        r_norm = r_cyl / bh_radius
        
        # Keplerian velocity profile modified by spin
        # Faster rotation for higher spin, inner regions rotate faster
        base_rotation = 1.0 / np.sqrt(r_norm + 0.1)  # Keplerian falloff
        
        # Spin enhancement - higher spin increases rotation rate
        spin_factor = 1.0 + spin * 2.0  # Boost factor based on spin
        
        # Frame dragging effect - stronger near the black hole for spinning BH
        frame_drag = spin * np.exp(-r_norm / 2.0)  # Exponential falloff with distance
        
        # Time-dependent rotation for visualization
        time_phase = self.visualizer.current_time * spin_factor * 0.5
        rotation_pattern = np.sin(2 * theta - time_phase * base_rotation)
        
        # Combine effects
        total_rotation = base_rotation * spin_factor * (0.7 + 0.3 * rotation_pattern) + frame_drag
        
        return np.clip(total_rotation, 0.1, 3.0)
    
    # Removed complex plasma calculation methods for performance

    def add_jet_glow_effect(self, jet_mesh, intensities, direction):
        """Add volumetric glow effect around the jet for enhanced visual appeal"""
        try:
            # Sample points along the jet for glow effect
            points = jet_mesh.points
            n_glow = min(len(points), 800)  # Limit for performance
            
            if n_glow > 0:
                # Create glow particles around the jet
                indices = np.random.choice(len(points), n_glow, replace=False)
                glow_points = points[indices].copy()
                
                # Add radial offset for volumetric glow
                bh_radius = self.visualizer.geometry.bh_radius
                offset_magnitude = bh_radius * 0.15  # Glow radius
                
                # Random radial offsets
                phi = np.random.uniform(0, 2*np.pi, n_glow)
                theta = np.random.uniform(0, np.pi, n_glow)
                r_offset = np.random.uniform(0, offset_magnitude, n_glow)
                
                offset_x = r_offset * np.sin(theta) * np.cos(phi)
                offset_y = r_offset * np.sin(theta) * np.sin(phi)
                offset_z = r_offset * np.cos(theta) * 0.3  # Less offset in z direction
                
                glow_points[:, 0] += offset_x
                glow_points[:, 1] += offset_y
                glow_points[:, 2] += offset_z
                
                # Create glow intensity based on distance from jet axis
                glow_intensity = np.exp(-r_offset / (offset_magnitude * 0.5))  # Gaussian falloff
                glow_intensity *= intensities[indices] if len(intensities) > max(indices) else 0.8
                
                glow_cloud = pv.PolyData(glow_points)
                glow_cloud['intensity'] = glow_intensity
                
                # Add glowing particles with bright colors
                self.plotter.add_mesh(glow_cloud,
                                    scalars='intensity',
                                    cmap='hot',  # Hot colormap for bright glow
                                    point_size=12,  # Larger points for visibility
                                    render_points_as_spheres=True,
                                    opacity=0.6,  # Semi-transparent for blending
                                    lighting=False,  # No lighting for pure glow
                                    name=f'jet_glow_{direction}')
                
        except Exception as e:
            print(f"Jet glow effect failed: {e}")
    
    def add_volumetric_glow(self, disk_mesh, temperatures):
        """Add volumetric glow effect for hottest plasma regions"""
        # Find hottest regions
        hot_mask = temperatures > 2.0
        if np.any(hot_mask):
            hot_points = disk_mesh.points[hot_mask]
            
            # Create glow particles around hot regions
            n_glow = min(len(hot_points), 1000)  # Limit for performance
            if n_glow > 0:
                indices = np.random.choice(len(hot_points), n_glow, replace=False)
                glow_points = hot_points[indices]
                
                # Add slight random offset for volumetric effect
                offset = np.random.normal(0, self.visualizer.geometry.bh_radius * 0.1, glow_points.shape)
                glow_points += offset
                
                glow_cloud = pv.PolyData(glow_points)
                glow_intensity = temperatures[hot_mask][indices]
                glow_cloud['intensity'] = glow_intensity
                
                self.plotter.add_mesh(glow_cloud,
                                    scalars='intensity',
                                    cmap='plasma',
                                    point_size=8,
                                    render_points_as_spheres=True,
                                    opacity=0.3,
                                    name='disk_glow')
    
    def create_jets(self):
        """Create simplified jets for better performance"""
        try:
            # Create jet spine (bright core) - simplified version with glow
            if self.visualizer.layer_states.get('jet_spine', True):
                jet_pos, jet_neg, jet_colors = self.visualizer.geometry.create_jets()
                
                # Simple jet properties for performance
                jet_pos['intensity'] = jet_colors
                jet_neg['intensity'] = jet_colors
                
                # Bright glowing jet core with enhanced visual effects
                self.plotter.add_mesh(jet_pos,
                                    scalars='intensity',
                                    cmap='plasma',
                                    opacity=0.95,
                                    lighting=True,
                                    ambient=0.6,  # Increased ambient light for glow
                                    diffuse=0.8,  # Enhanced diffuse lighting
                                    specular=0.4, # Added specular highlights
                                    specular_power=20,  # Sharp specular highlights
                                    name='jet_spine_pos')
                
                self.plotter.add_mesh(jet_neg,
                                    scalars='intensity',
                                    cmap='plasma',
                                    opacity=0.95,
                                    lighting=True,
                                    ambient=0.6,  # Increased ambient light for glow
                                    diffuse=0.8,  # Enhanced diffuse lighting
                                    specular=0.4, # Added specular highlights
                                    specular_power=20,  # Sharp specular highlights
                                    name='jet_spine_neg')
                
                # Add volumetric glow effect around jets
                self.add_jet_glow_effect(jet_pos, jet_colors, 'pos')
                self.add_jet_glow_effect(jet_neg, jet_colors, 'neg')
            
            # Jet sheath disabled for cleaner visualization
            # if self.visualizer.layer_states.get('jet_sheath', True):
            #     sheath_pos, sheath_neg, sheath_colors = self.visualizer.geometry.create_conical_glow()
            #     
            #     # Ultra-light transparent sheath
            #     sheath_pos['intensity'] = sheath_colors * 0.1
            #     sheath_neg['intensity'] = sheath_colors * 0.1
            #     
            #     self.plotter.add_mesh(sheath_pos,
            #                         scalars='intensity',
            #                         cmap='cool',
            #                         opacity=0.01,  # Barely visible
            #                         name='jet_sheath_pos')
            #     
            #     self.plotter.add_mesh(sheath_neg,
            #                         scalars='intensity',
            #                         cmap='cool',
            #                         opacity=0.01,  # Barely visible
            #                         name='jet_sheath_neg')
                                    
        except Exception as e:
            print(f"Jet creation failed: {e}")
    
    def calculate_jet_properties(self, points):
        """Calculate realistic jet plasma properties"""
        # Distance along jet axis (z-direction)
        z_dist = np.abs(points[:, 2])
        bh_radius = self.visualizer.geometry.bh_radius
        
        # Jet intensity decreases with distance (energy dissipation)
        z_norm = z_dist / (bh_radius * 10)  # Normalize to jet length scale
        base_intensity = np.exp(-z_norm * 0.3)  # Exponential decay
        
        # Add Kelvin-Helmholtz instabilities (turbulence at jet boundary)
        r_cyl = np.sqrt(points[:, 0]**2 + points[:, 1]**2)
        theta = np.arctan2(points[:, 1], points[:, 0])
        
        # Turbulence pattern
        kh_instability = np.sin(8 * theta + z_norm * 5 + self.visualizer.current_time * 2)
        kh_instability *= np.exp(-r_cyl / (bh_radius * 0.5))  # Stronger near axis
        
        # Internal jet structure (magnetic reconnection sites)
        reconnection = np.sin(z_norm * 10 + self.visualizer.current_time) * 0.3
        
        # Combine effects
        turbulence = 0.5 + 0.3 * kh_instability + 0.2 * reconnection
        enhanced_intensity = base_intensity * (0.8 + 0.2 * turbulence)
        
        return enhanced_intensity, turbulence
    
    def apply_relativistic_beaming(self, intensities, points):
        """Apply relativistic Doppler beaming effects"""
        # Jet velocity (highly relativistic)
        beta = self.visualizer.jet.jet_velocity  # Fraction of speed of light
        gamma = 1.0 / np.sqrt(1 - beta**2)
        
        # Viewing angle effect
        viewing_angle = np.radians(self.visualizer.viewing_angle)
        
        # Doppler factor for approaching jet (+z direction)
        z_sign = np.sign(points[:, 2])
        doppler_factor = 1.0 / (gamma * (1 - beta * np.cos(viewing_angle) * z_sign))
        
        # Beaming enhances approaching jet, dims receding jet
        beamed_intensities = intensities * (doppler_factor ** 3)  # Relativistic beaming
        
        return beamed_intensities
    
    def jet_temperature_to_rgb(self, intensities, turbulence):
        """Convert jet intensity to blue-white RGB colors"""
        # High-energy plasma: blue-white with slight variations
        intensity_norm = np.clip(intensities, 0, 2)
        
        # Base blue-white color for relativistic plasma
        blue = np.ones_like(intensity_norm)
        green = 0.8 + 0.2 * intensity_norm
        red = 0.6 + 0.4 * intensity_norm
        
        # Add turbulence color variations (slight red/orange flashes)
        red += 0.3 * turbulence * np.sin(self.visualizer.current_time * 5)
        green += 0.1 * turbulence * np.cos(self.visualizer.current_time * 3)
        
        rgb_colors = np.column_stack([red, green, blue])
        return np.clip(rgb_colors, 0, 1)
    
    def add_jet_core_glow(self, jet_mesh, intensities, direction):
        """Add luminous core glow to brightest jet regions"""
        # Find brightest regions in jet core
        bright_mask = intensities > np.percentile(intensities, 80)
        if np.any(bright_mask):
            bright_points = jet_mesh.points[bright_mask]
            
            # Create concentrated glow along jet axis
            n_glow = min(len(bright_points), 500)
            if n_glow > 0:
                indices = np.random.choice(len(bright_points), n_glow, replace=False)
                glow_points = bright_points[indices]
                
                glow_cloud = pv.PolyData(glow_points)
                glow_cloud['intensity'] = intensities[bright_mask][indices] * 1.5
                
                self.plotter.add_mesh(glow_cloud,
                                    scalars='intensity',
                                    cmap='hot',
                                    point_size=6,
                                    render_points_as_spheres=True,
                                    opacity=0.4,
                                    name=f'jet_glow_{direction}')
    
    def add_magnetic_field_structure(self, points):
        """Add helical magnetic field structure to jet sheath"""
        # Convert to cylindrical coordinates
        r_cyl = np.sqrt(points[:, 0]**2 + points[:, 1]**2)
        theta = np.arctan2(points[:, 1], points[:, 0])
        z = points[:, 2]
        
        bh_radius = self.visualizer.geometry.bh_radius
        z_norm = z / (bh_radius * 5)
        
        # Helical magnetic field pattern
        helix_pattern = np.sin(3 * theta + 0.5 * z_norm)
        helix_pattern *= np.cos(2 * theta - 0.3 * z_norm)
        
        # Magnetic field intensity varies with radius
        field_strength = np.exp(-r_cyl / (bh_radius * 2))
        
        magnetic_structure = 0.5 + 0.5 * helix_pattern * field_strength
        return magnetic_structure
    
    def sheath_to_rgb(self, intensities):
        """Convert sheath intensity to cooler RGB colors"""
        # Cooler plasma: blue to purple with magnetic field coloring
        intensity_norm = np.clip(intensities, 0, 1)
        
        red = 0.3 + 0.4 * intensity_norm
        green = 0.2 + 0.3 * intensity_norm
        blue = 0.6 + 0.4 * intensity_norm
        
        rgb_colors = np.column_stack([red, green, blue])
        return np.clip(rgb_colors, 0, 1)
    
    def add_magnetic_field_lines(self):
        """Add magnetic field line visualization"""
        try:
            # Create simple magnetic field lines
            n_lines = 12
            line_points = []
            
            for i in range(n_lines):
                theta = i * 2 * np.pi / n_lines
                r_start = self.visualizer.geometry.bh_radius * 1.1
                
                # Create field line from disk to jet
                z_vals = np.linspace(0, 20, 50)
                r_vals = r_start * np.exp(-z_vals / 10)  # Exponential decay
                
                line_coords = []
                for j, z in enumerate(z_vals):
                    x = r_vals[j] * np.cos(theta)
                    y = r_vals[j] * np.sin(theta)
                    line_coords.append([x, y, z])
                    line_coords.append([x, y, -z])  # Mirror for bottom
                
                if len(line_coords) > 1:
                    line = pv.Spline(np.array(line_coords))
                    self.plotter.add_mesh(line,
                                        color='cyan',
                                        line_width=2,
                                        opacity=0.6,
                                        name=f'field_line_{i}')
                                        
        except Exception as e:
            print(f"Magnetic field lines creation failed: {e}")
    
    def setup_lighting(self):
        """Setup physically-based lighting for photorealistic rendering"""
        if not self.plotter:
            return
            
        try:
            # Remove default lights for custom setup
            try:
                self.plotter.remove_all_lights()
            except:
                pass  # May not have lights to remove initially
            
            # Simplified lighting setup to avoid shader issues
            # Primary emission from hot gas (accretion disk)
            disk_light = pv.Light(position=(0, 0, 2), 
                                 focal_point=(0, 0, 0),
                                 color='orange',
                                 intensity=1.0)
            self.plotter.add_light(disk_light)
            
            # Secondary light for jets
            jet_light = pv.Light(position=(2, 2, 3),
                               focal_point=(0, 0, 0),
                               color='lightblue',
                               intensity=0.8)
            self.plotter.add_light(jet_light)
            
            # Ambient cosmic background radiation
            ambient_light = pv.Light(light_type='scenelight',
                                   color='darkblue',
                                   intensity=0.2)
            self.plotter.add_light(ambient_light)
            
            # Setup simplified volumetric lighting effects
            self.setup_volumetric_lighting()
            
            # Configure basic rendering properties
            try:
                self.plotter.enable_anti_aliasing()
            except:
                pass  # May not be supported
            
            # Create cosmic background with stars and galaxy
            self.create_cosmic_background()
            
        except Exception as e:
            print(f"Lighting setup failed: {e}")
    
    def create_cosmic_background(self):
        """Create a realistic cosmic background with stars and galaxy"""
        try:
            # Create distant star field
            self.create_star_field()
            
            # Create galaxy background
            self.create_galaxy_background()
            
            # Set deep space background color
            self.plotter.set_background((0.01, 0.01, 0.05))  # Very dark cosmic blue
            
        except Exception as e:
            print(f"Cosmic background creation failed: {e}")
    
    def create_star_field(self):
        """Create a field of distant stars"""
        try:
            # Create a large sphere for star positions
            star_distance = self.visualizer.geometry.bh_radius * 150
            n_stars = 3000  # More stars for better effect
            
            # Generate random star positions on a sphere
            phi = np.random.uniform(0, 2*np.pi, n_stars)
            costheta = np.random.uniform(-1, 1, n_stars)
            theta = np.arccos(costheta)
            
            x = star_distance * np.sin(theta) * np.cos(phi)
            y = star_distance * np.sin(theta) * np.sin(phi)
            z = star_distance * np.cos(theta)
            
            star_points = np.column_stack([x, y, z])
            
            # Create star brightness (some bright, most dim)
            star_brightness = np.random.exponential(0.5, n_stars)
            star_brightness = np.clip(star_brightness, 0.2, 3.0)
            
            # Create star colors (mostly white, some blue/red giants)
            star_types = np.random.choice(['white', 'blue', 'red', 'yellow'], n_stars, 
                                        p=[0.6, 0.15, 0.15, 0.1])
            
            # Add stars as point cloud
            star_cloud = pv.PolyData(star_points)
            star_cloud['brightness'] = star_brightness
            
            # Create color array based on star types and brightness
            colors = np.zeros((n_stars, 3))
            for i, star_type in enumerate(star_types):
                brightness_factor = min(star_brightness[i] / 2.0, 1.0)
                if star_type == 'white':
                    colors[i] = [brightness_factor, brightness_factor, brightness_factor]
                elif star_type == 'blue':
                    colors[i] = [0.5 * brightness_factor, 0.7 * brightness_factor, brightness_factor]
                elif star_type == 'red':
                    colors[i] = [brightness_factor, 0.4 * brightness_factor, 0.2 * brightness_factor]
                else:  # yellow
                    colors[i] = [brightness_factor, brightness_factor, 0.6 * brightness_factor]
            
            star_cloud['star_colors'] = colors
            
            # Add stars with enhanced visibility
            self.plotter.add_mesh(star_cloud,
                                scalars='brightness',
                                cmap='hot',
                                point_size=4,  # Larger points for better visibility
                                render_points_as_spheres=True,
                                opacity=1.0,  # Full opacity for stars
                                lighting=False,
                                name='star_field')
            
            print(f"Created star field with {n_stars} stars")
            
        except Exception as e:
            print(f"Star field creation failed: {e}")
            # Fallback: simple star field
            try:
                # Create fewer stars but simpler
                star_distance = self.visualizer.geometry.bh_radius * 100
                n_stars = 1000
                
                # Random positions
                points = np.random.uniform(-star_distance, star_distance, (n_stars, 3))
                # Keep points on sphere surface
                norms = np.linalg.norm(points, axis=1)
                points = points / norms[:, np.newaxis] * star_distance
                
                star_cloud = pv.PolyData(points)
                brightness = np.random.uniform(0.3, 1.0, n_stars)
                star_cloud['brightness'] = brightness
                
                self.plotter.add_mesh(star_cloud,
                                    color='white',
                                    point_size=2,
                                    render_points_as_spheres=True,
                                    opacity=0.8,
                                    lighting=False,
                                    name='star_field_simple')
                
                print(f"Created simplified star field with {n_stars} stars")
                
            except Exception as e2:
                print(f"Simplified star field also failed: {e2}")
    
    def create_galaxy_background(self):
        """Create a subtle galaxy/nebula background using available methods"""
        try:
            # Disable the large galaxy background that creates the purple plate
            # Just keep stars for a cleaner look
            print("Galaxy background disabled - using stars only for cleaner appearance")
            return
            
            # Original galaxy code kept but disabled
            # Create a large cylinder for galaxy structure
            galaxy_radius = self.visualizer.geometry.bh_radius * 100
            
            # Create galaxy cylinder instead of disk
            galaxy_cylinder = pv.Cylinder(center=(0, 0, 0),
                                        direction=(0, 0, 1),
                                        radius=galaxy_radius,
                                        height=galaxy_radius * 0.1)
            
            # Rotate galaxy to interesting angle
            galaxy_cylinder.rotate_x(75)  # Tilted view
            galaxy_cylinder.rotate_z(30)
            
            # Create spiral galaxy pattern
            points = galaxy_cylinder.points
            r = np.sqrt(points[:, 0]**2 + points[:, 1]**2)
            theta = np.arctan2(points[:, 1], points[:, 0])
            
            # Spiral arms
            spiral1 = np.sin(2 * theta + r / (galaxy_radius * 0.1))
            spiral2 = np.sin(2 * theta + np.pi + r / (galaxy_radius * 0.1))
            spiral_intensity = np.maximum(spiral1, spiral2)
            
            # Radial falloff
            radial_falloff = np.exp(-r / (galaxy_radius * 0.4))
            
            # Combine effects
            galaxy_intensity = (0.3 + 0.7 * spiral_intensity) * radial_falloff
            galaxy_intensity = np.clip(galaxy_intensity, 0, 1)
            
            galaxy_cylinder['intensity'] = galaxy_intensity
            
            # Add galaxy with purple/blue colors
            self.plotter.add_mesh(galaxy_cylinder,
                                scalars='intensity',
                                cmap='viridis',
                                opacity=0.12,
                                lighting=False,
                                name='galaxy_background')
                                
        except Exception as e:
            print(f"Galaxy background creation failed: {e}")
            # Fallback: simple nebula effect using sphere
            try:
                nebula_sphere = pv.Sphere(radius=self.visualizer.geometry.bh_radius * 80, phi_resolution=20, theta_resolution=20)
                nebula_intensity = np.random.uniform(0, 0.5, nebula_sphere.n_points)
                nebula_sphere['nebula'] = nebula_intensity
                
                self.plotter.add_mesh(nebula_sphere,
                                    scalars='nebula',
                                    cmap='plasma',
                                    opacity=0.05,
                                    lighting=False,
                                    name='nebula_background')
            except:
                pass  # Skip if this also fails
    
    def setup_volumetric_lighting(self):
        """Setup simplified volumetric lighting for gas emission effects"""
        try:
            # Simplified approach to avoid shader issues
            pass
        except Exception as e:
            print(f"Volumetric lighting setup failed: {e}")
    
    def add_atmospheric_scattering(self):
        """Add simplified atmospheric scattering effects"""
        try:
            # Simplified version - just add a basic cosmic dust layer
            if hasattr(self.visualizer.geometry, 'bh_radius'):
                scatter_radius = self.visualizer.geometry.bh_radius * 15
                
                # Create basic dust sphere
                dust_sphere = pv.Sphere(radius=scatter_radius, phi_resolution=15, theta_resolution=15)
                
                # Simple scattering intensity
                n_points = dust_sphere.n_points
                scatter_intensity = np.ones(n_points) * 0.05
                dust_sphere['scattering'] = scatter_intensity
                
                # Very subtle scattering effect
                self.plotter.add_mesh(dust_sphere,
                                    color='lightblue',
                                    opacity=0.02,
                                    lighting=False,
                                    name='cosmic_dust')
        except Exception as e:
            print(f"Atmospheric scattering failed: {e}")
    
    def add_plasma_emission_effects(self):
        """Add emission effects from hottest plasma regions"""
        # This will be called after plasma objects are created
        # to add emission glows around the hottest regions
        pass
    
    def update_scene(self):
        """Update the entire scene with current parameters"""
        if not self.plotter:
            return
            
        try:
            # Clear and rebuild scene
            self.init_scene()
            
            # Apply current viewing transformations
            self.apply_viewing_transformations()
            
            # Update display
            self.plotter.render()
            
        except Exception as e:
            print(f"Scene update failed: {e}")
    
    def apply_viewing_transformations(self):
        """Apply relativistic and gravitational effects"""
        try:
            # Apply Doppler beaming effects
            self.update_doppler_effects()
            
            # Apply gravitational lensing
            self.update_gravitational_lensing()
            
        except Exception as e:
            print(f"Viewing transformations failed: {e}")
    
    def update_doppler_effects(self):
        """Update Doppler beaming and boosting effects"""
        # Calculate viewing angle effects
        viewing_rad = np.radians(self.visualizer.viewing_angle)
        
        # Doppler factors for approaching/receding jets
        gamma = self.visualizer.jet.jet_velocity / (1 - self.visualizer.jet.jet_velocity**2)**0.5
        beta = self.visualizer.jet.jet_velocity
        
        doppler_approaching = 1 / (gamma * (1 - beta * np.cos(viewing_rad)))
        doppler_receding = 1 / (gamma * (1 + beta * np.cos(viewing_rad)))
        
        # Update jet brightnesses based on Doppler factors
        self.apply_doppler_brightening(doppler_approaching, doppler_receding)
    
    def apply_doppler_brightening(self, doppler_approaching, doppler_receding):
        """Apply Doppler brightening to jets"""
        try:
            # Get jet actors
            for actor_name in ['jet_spine_pos', 'jet_sheath_pos']:
                actor = self.plotter.renderer.actors.get(actor_name)
                if actor:
                    # Brighten approaching jet
                    actor.GetProperty().SetOpacity(min(1.0, 0.9 * doppler_approaching))
            
            for actor_name in ['jet_spine_neg', 'jet_sheath_neg']:
                actor = self.plotter.renderer.actors.get(actor_name)
                if actor:
                    # Dim receding jet
                    actor.GetProperty().SetOpacity(max(0.1, 0.9 * doppler_receding))
                    
        except Exception as e:
            print(f"Doppler brightening failed: {e}")
    
    def update_gravitational_lensing(self):
        """Update gravitational lensing effects"""
        if not self.visualizer.layer_states.get('gravitational_lensing', False):
            return
            
        try:
            # Simple lensing effect on background stars
            # This is a simplified representation
            pass
            
        except Exception as e:
            print(f"Gravitational lensing update failed: {e}")
    
    def export_frame(self, filename):
        """Export current frame as image"""
        if self.plotter:
            self.plotter.screenshot(filename)
    
    def export_movie(self, filename, n_frames=100):
        """Export animation as movie"""
        if not self.plotter:
            return
            
        try:
            self.plotter.open_movie(filename)
            
            for i in range(n_frames):
                # Update scene for current frame
                self.update_scene()
                
                # Write frame
                self.plotter.write_frame()
                
                # Advance time
                self.visualizer.current_time += 0.1
            
            self.plotter.close()
            
        except Exception as e:
            print(f"Movie export failed: {e}")
    
    def cleanup(self):
        """Clean shutdown of rendering engine"""
        try:
            if hasattr(self, 'plotter') and self.plotter:
                self.plotter.close()
        except Exception as e:
            print(f"Cleanup error: {e}")
