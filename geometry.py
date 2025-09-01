"""
Geometry creation for the black hole jet simulation
"""
import numpy as np
import pyvista as pv

class GeometryGenerator:
    """
    Generates 3D geometries for black hole jet simulation with adjustable parameters.
    
    All geometry scales are computed from the physics parameters to ensure
    physical consistency when parameters change.
    """
    
    def __init__(self, physics_params):
        """
        Initialize geometry generator with physics parameters.
        
        Args:
            physics_params (dict): Physical scales from BlandfordZnajekJet.get_physical_scales()
        """
        self.update_physics_params(physics_params)
        
    def update_physics_params(self, physics_params):
        """
        Update all geometry scales based on new physics parameters.
        
        Args:
            physics_params (dict): Updated physical scales
        """
        # Convert from CGS (cm) to km for visualization
        self.bh_radius = physics_params['black_hole_radius'] / 1e5  # cm to km
        self.schwarzschild_radius = physics_params['schwarzschild_radius'] / 1e5  # cm to km
        self.isco_radius = physics_params['isco_radius'] / 1e5  # cm to km
        self.jet_velocity = physics_params['jet_velocity']
        self.power = physics_params['power']
        self.energy_density = physics_params['energy_density']
        
        # Scale dependent quantities
        self.disk_radius = max(10 * self.bh_radius, 3 * self.isco_radius)  # Reasonable disk size
        self.jet_length = 20 * self.bh_radius  # Jet length scales with BH size
        self.jet_radius_base = 0.1 * self.bh_radius  # Jet base radius
        self.jet_radius_collar = 0.5 * self.bh_radius  # Jet collar radius
        
    def create_black_hole(self):
        """Create black hole sphere"""
        sphere = pv.Sphere(radius=self.bh_radius, center=(0, 0, 0))
        return sphere
    
    def create_jets(self):
        """Create thin conical jets that start much smaller than the sheath"""
        n_z = 120
        n_theta = 12  # Reduced for thinner appearance (was 24)
        z = np.linspace(self.bh_radius * 1.5, self.jet_length, n_z)
        theta = np.linspace(0, 2*np.pi, n_theta)
        
        # Much thinner jet - reduced width significantly
        jet_base_radius = self.bh_radius * 0.05    # Very thin starting radius (reduced from 0.2)
        jet_tip_radius = self.bh_radius * 0.8      # Much less expansion (reduced from 2.0)
        
        # Positive jet (+z direction) - proper conic shape
        jet_points_pos = np.zeros((n_z, n_theta, 3))
        for i, zi in enumerate(z):
            # Linear conic expansion (constant opening angle)
            z_fraction = (zi - self.bh_radius * 1.5) / (self.jet_length - self.bh_radius * 1.5)
            rj = jet_base_radius + (jet_tip_radius - jet_base_radius) * z_fraction
            
            for j, th in enumerate(theta):
                xj = rj * np.cos(th)
                yj = rj * np.sin(th)
                jet_points_pos[i, j] = [xj, yj, zi]
        
        jet_mesh_pos = pv.StructuredGrid()
        jet_mesh_pos.points = jet_points_pos.reshape(-1, 3)
        jet_mesh_pos.dimensions = (n_z, n_theta, 1)
        
        # Negative jet (-z direction)
        jet_points_neg = np.zeros((n_z, n_theta, 3))
        for i, zi in enumerate(z):
            z_fraction = (zi - self.bh_radius * 1.5) / (self.jet_length - self.bh_radius * 1.5)
            rj = jet_base_radius + (jet_tip_radius - jet_base_radius) * z_fraction
            
            for j, th in enumerate(theta):
                xj = rj * np.cos(th)
                yj = rj * np.sin(th)
                jet_points_neg[i, j] = [xj, yj, -zi]
        
        jet_mesh_neg = pv.StructuredGrid()
        jet_mesh_neg.points = jet_points_neg.reshape(-1, 3)
        jet_mesh_neg.dimensions = (n_z, n_theta, 1)
        
        # Jet colors - brighter at base, dimmer at tip
        jet_colors = np.linspace(1, 0.3, n_z).repeat(n_theta)
        
        return jet_mesh_pos, jet_mesh_neg, jet_colors
    
    def create_conical_glow(self):
        """Create ultra-transparent conical sheath that barely outlines the jet"""
        cone_height = self.jet_length * 1.1
        
        # Much thinner sheath for better transparency
        sheath_base_radius = self.bh_radius * 0.6   # Smaller base radius
        sheath_tip_radius = self.bh_radius * 3.0    # Less expansion
        
        # Fewer points for better performance and less visual density
        n_z_cone = 40  # Reduced from 80
        n_theta_cone = 18  # Reduced from 36
        
        z_cone = np.linspace(self.bh_radius * 1.5, cone_height, n_z_cone)
        theta_cone = np.linspace(0, 2*np.pi, n_theta_cone)
        
        # Positive cone
        cone_points_pos = np.zeros((n_z_cone, n_theta_cone, 3))
        for i, zi in enumerate(z_cone):
            # Linear conic expansion for sheath (more subtle)
            z_fraction = (zi - self.bh_radius * 1.5) / (cone_height - self.bh_radius * 1.5)
            r_cone = sheath_base_radius + (sheath_tip_radius - sheath_base_radius) * z_fraction
            
            for j, th in enumerate(theta_cone):
                x_cone = r_cone * np.cos(th)
                y_cone = r_cone * np.sin(th)
                cone_points_pos[i, j] = [x_cone, y_cone, zi]
        
        cone_mesh_pos = pv.StructuredGrid()
        cone_mesh_pos.points = cone_points_pos.reshape(-1, 3)
        cone_mesh_pos.dimensions = (n_z_cone, n_theta_cone, 1)
        
        # Negative cone
        cone_points_neg = np.zeros((n_z_cone, n_theta_cone, 3))
        for i, zi in enumerate(z_cone):
            z_fraction = (zi - self.bh_radius * 1.5) / (cone_height - self.bh_radius * 1.5)
            r_cone = sheath_base_radius + (sheath_tip_radius - sheath_base_radius) * z_fraction
            
            for j, th in enumerate(theta_cone):
                x_cone = r_cone * np.cos(th)
                y_cone = r_cone * np.sin(th)
                cone_points_neg[i, j] = [x_cone, y_cone, -zi]
        
        cone_mesh_neg = pv.StructuredGrid()
        cone_mesh_neg.points = cone_points_neg.reshape(-1, 3)
        cone_mesh_neg.dimensions = (n_z_cone, n_theta_cone, 1)
        
        # Much weaker color intensity for transparency
        cone_colors = np.linspace(0.2, 0.01, n_z_cone).repeat(n_theta_cone)
        
        return cone_mesh_pos, cone_mesh_neg, cone_colors
    
    def create_bright_core(self):
        """Create bright core region near the black hole"""
        core_radius = self.bh_radius * 2.5
        core_height = self.bh_radius * 1.0
        
        n_r_core = 25
        n_theta_core = 48
        n_z_core = 12
        
        r_core = np.linspace(self.bh_radius * 1.1, core_radius, n_r_core)
        theta_core = np.linspace(0, 2*np.pi, n_theta_core)
        z_core = np.linspace(-core_height/2, core_height/2, n_z_core)
        
        core_points = []
        core_colors = []
        
        for i, ri in enumerate(r_core):
            for j, thi in enumerate(theta_core):
                for k, zi in enumerate(z_core):
                    x = ri * np.cos(thi)
                    y = ri * np.sin(thi)
                    z = zi
                    core_points.append([x, y, z])
                    
                    r_factor = 1.0 - (ri / core_radius)
                    z_factor = 1.0 - abs(zi) / (core_height/2)
                    brightness = (r_factor * z_factor) ** 0.5
                    brightness = max(0.3, min(1.0, brightness))
                    core_colors.append(brightness)
        
        return np.array(core_points), np.array(core_colors)
    
    def create_thick_accretion_disk(self):
        """Create a thin, flat accretion disk with realistic structure"""
        inner_radius = max(self.isco_radius, self.bh_radius * 3.0)
        outer_radius = self.disk_radius
        
        n_r = 50  # Radial resolution
        n_theta = 100  # Azimuthal resolution
        n_z = 5  # Much fewer vertical layers for flatter disk
        
        r = np.linspace(inner_radius, outer_radius, n_r)
        theta = np.linspace(0, 2*np.pi, n_theta)
        
        disk_points = []
        disk_scalars = []
        
        for i, ri in enumerate(r):
            # Much flatter disk - realistic scale height
            radius_ratio = ri / inner_radius
            
            # Realistic thin disk: H/R ~ 0.01-0.1 (much thinner!)
            scale_height = self.bh_radius * 0.1 * (radius_ratio ** 0.125)
            scale_height = min(scale_height, self.bh_radius * 0.3)  # Cap at very thin
            
            # Create very limited vertical distribution
            z_max = scale_height * 1.0  # Only ±1 scale height (much flatter)
            z_values = np.linspace(-z_max, z_max, n_z)
            
            for j, thi in enumerate(theta):
                x_base = ri * np.cos(thi)
                y_base = ri * np.sin(thi)
                
                # Subtle spiral density waves
                spiral_phase = 2 * thi + ri / (self.bh_radius * 4)
                spiral_amplitude = 0.1 * scale_height  # Much smaller spiral
                spiral_offset = spiral_amplitude * np.sin(spiral_phase)
                
                for k, z in enumerate(z_values):
                    # Apply subtle spiral structure
                    z_final = z + spiral_offset
                    
                    # Minimal turbulent variations
                    turbulence = 0.05 * scale_height * (np.random.random() - 0.5)
                    z_final += turbulence
                    
                    disk_points.append([x_base, y_base, z_final])
                    
                    # Calculate temperature/brightness based on radius and height
                    radius_fraction = (ri - inner_radius) / (outer_radius - inner_radius)
                    height_fraction = abs(z) / z_max
                    
                    # Radial temperature profile: T ∝ r^(-3/4)
                    radial_temp = (1.0 - radius_fraction) ** 0.75
                    
                    # Vertical temperature profile: hotter in midplane
                    vertical_temp = np.exp(-height_fraction**2 / 0.5)  # Gaussian in z
                    
                    # Combine effects
                    temperature = radial_temp * vertical_temp
                    
                    # Add density enhancement in spiral arms
                    spiral_enhancement = 1 + 0.5 * np.exp(-((spiral_phase % (2*np.pi/2)) - np.pi/2)**2 / 0.3)
                    temperature *= spiral_enhancement
                    
                    # Final temperature scaling
                    if temperature > 0.8:  # Very hot inner regions - white
                        temp_factor = 0.9 + 0.1 * temperature
                    elif temperature > 0.5:  # Intermediate - yellow/orange
                        temp_factor = 0.5 + 0.4 * temperature
                    elif temperature > 0.2:  # Outer warm - orange/red
                        temp_factor = 0.2 + 0.3 * temperature
                    else:  # Cool outer regions - dark red
                        temp_factor = 0.05 + 0.15 * temperature
                    
                    temp_factor = np.clip(temp_factor, 0.02, 1.0)
                    disk_scalars.append(temp_factor)
        
        disk_points = np.array(disk_points)
        disk_scalars = np.array(disk_scalars)
        
        # Create unstructured grid for irregular point distribution
        disk_mesh = pv.PolyData(disk_points)
        disk_mesh['temperature'] = disk_scalars
        
        return disk_mesh, disk_scalars
    
    def create_warped_accretion_disk(self):
        """Create curved accretion disk that wraps around the black hole like a bowl"""
        # Use ISCO radius for inner edge (more physically accurate)
        inner_radius = max(self.isco_radius, self.bh_radius * 3.0)
        outer_radius = self.disk_radius
        n_r = 60
        n_theta = 120
        
        r = np.linspace(inner_radius, outer_radius, n_r)
        theta = np.linspace(0, 2*np.pi, n_theta)
        
        disk_points = []
        disk_scalars = []
        
        for i, ri in enumerate(r):
            for j, thi in enumerate(theta):
                x = ri * np.cos(thi)
                y = ri * np.sin(thi)
                
                # Create a bowl/saddle shape that curves up at the edges
                # The disk should dip down near the black hole and curve up at outer edges
                radius_factor = (ri - inner_radius) / (outer_radius - inner_radius)
                
                # Parabolic curve: starts low near black hole, curves up at edges
                bowl_height = self.bh_radius * 2.0 * (radius_factor - 0.5)**2
                
                # Add some warping due to frame-dragging
                warp_amplitude = self.bh_radius * 0.5 * (inner_radius / ri)**1.5
                frame_drag_warp = warp_amplitude * np.sin(2 * thi + ri / self.bh_radius)
                
                # Combine bowl shape with frame dragging
                z = bowl_height + frame_drag_warp
                
                disk_points.append([x, y, z])
                
                # Create dramatic temperature gradient
                radius_fraction = (ri - inner_radius) / (outer_radius - inner_radius)
                
                # Very hot inner regions, cool outer regions
                if radius_fraction < 0.2:  # Very inner region - white hot
                    temp_factor = 0.8 + 0.2 * (1.0 - radius_fraction / 0.2)
                elif radius_fraction < 0.5:  # Middle region - yellow to orange
                    temp_factor = 0.4 + 0.4 * (1.0 - (radius_fraction - 0.2) / 0.3)
                else:  # Outer region - red to dark
                    temp_factor = 0.1 + 0.3 * (1.0 - (radius_fraction - 0.5) / 0.5)
                
                temp_factor = max(0.0, min(1.0, temp_factor))
                disk_scalars.append(temp_factor)
        
        disk_points = np.array(disk_points)
        disk_scalars = np.array(disk_scalars)
        
        disk_mesh = pv.StructuredGrid()
        disk_mesh.points = disk_points
        disk_mesh.dimensions = (n_r, n_theta, 1)
        
        return disk_mesh, disk_scalars
    
    def create_photon_ring(self):
        """Create photon ring effect at critical photon orbit"""
        # Critical photon orbit at r = 1.5 * r_s for Schwarzschild (2.6 for Kerr)
        photon_radius = 2.6 * self.schwarzschild_radius / 2  # Approximate for rotating BH
        ring_thickness = self.schwarzschild_radius * 0.1
        
        n_ring = 180
        n_thickness = 12
        
        theta_ring = np.linspace(0, 2*np.pi, n_ring)
        r_ring = np.linspace(photon_radius - ring_thickness/2, 
                            photon_radius + ring_thickness/2, n_thickness)
        
        ring_points = []
        ring_scalars = []
        
        for i, ri in enumerate(r_ring):
            for j, thi in enumerate(theta_ring):
                x = ri * np.cos(thi)
                y = ri * np.sin(thi)
                z = 0
                
                ring_points.append([x, y, z])
                
                distance_from_center = abs(ri - photon_radius) / (ring_thickness/2)
                brightness = np.exp(-distance_from_center**2)
                ring_scalars.append(brightness)
        
        return np.array(ring_points), np.array(ring_scalars)
    
    def create_background_stars_and_galaxies(self, max_distance):
        """Create background stars and galaxies with enhanced gravitational lensing"""
        # Stars
        n_stars = 8000  # Increased number for better effect
        star_xyz = np.random.uniform(-max_distance, max_distance, (n_stars, 3))
        
        lensed_stars = []
        star_brightness = []
        
        for pos in star_xyz:
            r = np.linalg.norm(pos)
            if r > self.bh_radius * 8:  # Apply lensing to more distant objects
                # Enhanced lensing calculation - stronger near the black hole
                impact_parameter = np.sqrt(pos[0]**2 + pos[1]**2)  # Distance from z-axis
                
                if impact_parameter > self.bh_radius * 2:
                    # Einstein ring radius approximation
                    lensing_strength = (self.bh_radius * 6) / impact_parameter
                    deflection_angle = 4 * self.bh_radius / impact_parameter
                    
                    # Calculate deflection vector (toward black hole)
                    direction_to_bh = -pos / r
                    deflection_magnitude = deflection_angle * 0.15
                    
                    # Apply deflection
                    lensed_pos = pos + deflection_magnitude * direction_to_bh * r
                    
                    # Magnification effect - stars near critical curves appear brighter
                    magnification = 1.0 + np.exp(-impact_parameter / (self.bh_radius * 4))
                    star_brightness.append(min(magnification, 2.0))
                    
                    lensed_stars.append(lensed_pos)
                else:
                    # Very close to black hole - extreme lensing or hidden
                    if impact_parameter > self.bh_radius * 2.6:  # Outside photon sphere
                        # Strong deflection, possible multiple images
                        deflection_factor = 2.0
                        direction_to_bh = -pos / r
                        lensed_pos = pos + deflection_factor * direction_to_bh * self.bh_radius
                        lensed_stars.append(lensed_pos)
                        star_brightness.append(0.3)  # Dimmed by strong lensing
                    # Stars inside photon sphere are not visible (captured)
            else:
                lensed_stars.append(pos)
                star_brightness.append(1.0)
        
        star_xyz = np.array(lensed_stars)
        
        # Apply brightness modulation to star colors
        star_colors = []
        for i, brightness in enumerate(star_brightness):
            base_color = np.random.uniform(0.6, 1.0, 3)
            enhanced_color = base_color * brightness
            enhanced_color = np.clip(enhanced_color, 0.2, 1.5)  # Allow some overbrightening
            star_colors.append(enhanced_color)
        
        star_colors = np.array(star_colors)
        
        # Galaxies with more sophisticated lensing
        n_galaxies = 300  # Increased number
        galaxy_xyz = np.random.uniform(-max_distance*1.8, max_distance*1.8, (n_galaxies, 3))
        
        lensed_galaxies = []
        galaxy_distortions = []
        
        for pos in galaxy_xyz:
            r = np.linalg.norm(pos)
            if r > self.bh_radius * 12:
                # Apply shear and magnification
                impact_parameter = np.sqrt(pos[0]**2 + pos[1]**2)
                
                if impact_parameter > self.bh_radius * 3:
                    # Weak lensing regime - small distortions
                    lensing_strength = (self.bh_radius * 10) / impact_parameter
                    shear_factor = lensing_strength * 0.3
                    
                    # Add elliptical distortion (shear)
                    direction_to_bh = -pos / r
                    tangential_direction = np.array([-direction_to_bh[1], direction_to_bh[0], 0])
                    
                    # Apply weak lensing distortion
                    distortion = shear_factor * tangential_direction * self.bh_radius * 0.5
                    lensed_pos = pos + distortion
                    
                    # Calculate magnification
                    magnification = 1.0 + np.exp(-impact_parameter / (self.bh_radius * 6))
                    galaxy_distortions.append(min(magnification, 1.8))
                    
                    lensed_galaxies.append(lensed_pos)
                else:
                    # Strong lensing - possible arcs or multiple images
                    deflection_strength = (self.bh_radius * 15) / impact_parameter
                    direction_to_bh = -pos / r
                    lensed_pos = pos + deflection_strength * direction_to_bh * self.bh_radius * 0.3
                    lensed_galaxies.append(lensed_pos)
                    galaxy_distortions.append(1.5)  # Brightened by strong lensing
            else:
                lensed_galaxies.append(pos)
                galaxy_distortions.append(1.0)
        
        galaxy_xyz = np.array(lensed_galaxies)
        
        # Enhanced galaxy colors with lensing effects
        galaxy_colors = []
        for i, distortion in enumerate(galaxy_distortions):
            if np.random.random() < 0.6:  # Red galaxies
                base_color = [0.8 + 0.2*np.random.random(), 
                            0.4 + 0.3*np.random.random(),
                            0.2 + 0.2*np.random.random()]
            else:  # Blue galaxies
                base_color = [0.3 + 0.2*np.random.random(),
                            0.4 + 0.3*np.random.random(), 
                            0.7 + 0.3*np.random.random()]
            
            # Apply lensing brightness enhancement
            enhanced_color = [c * distortion for c in base_color]
            enhanced_color = [min(c, 1.2) for c in enhanced_color]  # Cap brightness
            galaxy_colors.append(enhanced_color)
        
        galaxy_colors = np.array(galaxy_colors)
        
        return star_xyz, star_colors, galaxy_xyz, galaxy_colors
