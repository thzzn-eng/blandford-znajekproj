"""
Physics calculations for the Blandford-Znajek jet simulation
"""
import numpy as np

# Physical constants
C = 2.99792458e10  # speed of light [cm/s]
G = 6.67430e-8     # gravitational constant [cm^3/g/s^2]
MSUN = 1.98847e33  # solar mass [g]

class BlandfordZnajekJet:
    """
    Blandford-Znajek jet physics with fully adjustable parameters.
    
    Parameters:
    - M: Black hole mass in solar masses
    - a: Dimensionless spin parameter (0 < a < 1)
    - B: Magnetic field strength in Gauss
    
    Computed properties:
    - r_H: Event horizon radius
    - Ω_H: Angular velocity of horizon
    - Φ_BH: Magnetic flux through black hole
    - L_BZ: Blandford-Znajek luminosity
    """
    
    def __init__(self, mass=10.0, spin=0.9, B=1e4):
        """
        Initialize with black hole parameters.
        
        Args:
            mass (float): Black hole mass in solar masses (default: 10.0)
            spin (float): Dimensionless spin 0 < a < 1 (default: 0.9)
            B (float): Magnetic field strength in Gauss (default: 1e4)
        """
        self._mass = mass
        self._spin = spin
        self._B = B
        self._update_derived_quantities()
    
    @property
    def mass(self):
        """Black hole mass in solar masses"""
        return self._mass
    
    @mass.setter
    def mass(self, value):
        """Set black hole mass and update derived quantities"""
        self._mass = max(0.1, value)  # Minimum 0.1 solar masses
        self._update_derived_quantities()
    
    @property
    def spin(self):
        """Dimensionless spin parameter (0 < a < 1)"""
        return self._spin
    
    @spin.setter 
    def spin(self, value):
        """Set spin parameter and update derived quantities"""
        self._spin = max(0.0, min(0.999, value))  # Clamp to physical range
        self._update_derived_quantities()
    
    @property
    def B(self):
        """Magnetic field strength in Gauss"""
        return self._B
    
    @B.setter
    def B(self, value):
        """Set magnetic field and update derived quantities"""
        self._B = max(1.0, value)  # Minimum 1 Gauss
        self._update_derived_quantities()
    
    def _update_derived_quantities(self):
        """
        Update all derived quantities from M, a, B using Blandford-Znajek physics.
        
        Key equations:
        - r_H = GM/c² * (1 + √(1-a²))  [Event horizon radius]
        - Ω_H = ac/(2r_H)               [Angular velocity of horizon]
        - Φ_BH ∝ B * r_H²              [Magnetic flux through black hole]
        - L_BZ ∝ (Ω_H * Φ_BH)² / c     [Blandford-Znajek luminosity]
        """
        # Convert mass to CGS
        M_cgs = self._mass * MSUN
        a = self._spin
        
        # Schwarzschild radius: r_s = 2GM/c²
        self.schwarzschild_radius = 2 * G * M_cgs / (C**2)
        
        # Event horizon radius for Kerr black hole: r_H = GM/c² * (1 + √(1-a²))
        self.black_hole_radius = (G * M_cgs / (C**2)) * (1 + np.sqrt(1 - a**2))
        
        # Angular velocity of horizon: Ω_H = ac/(2r_H)
        self.omega_H = a * C / (2 * self.black_hole_radius)
        
        # Magnetic flux through black hole: Φ_BH ∝ B * r_H²
        # Using realistic flux threading factor
        self.phi_BH = self._B * np.pi * (self.black_hole_radius**2)
        
        # Blandford-Znajek luminosity: L_BZ = (1/4π) * (Ω_H * Φ_BH)² / c
        # Includes efficiency factor for realistic power extraction
        efficiency = 0.1 * a**2  # Efficiency increases with spin
        self.power = efficiency * (self.omega_H * self.phi_BH)**2 / (4 * np.pi * C)
        
        # Jet velocity from power (empirical relation for visualization)
        # Higher power → higher velocity, capped at 0.99c
        power_factor = min(self.power / 1e39, 10.0)  # Normalize to typical AGN power
        self.jet_velocity = 0.8 + 0.15 * np.tanh(power_factor / 5.0)
        
        # Update energy density and other jet properties
        self.energy_density = self.power / (np.pi * (self.black_hole_radius * 10)**2)
        
        # ISCO radius (innermost stable circular orbit)
        # For Kerr metric: r_ISCO ≈ 3r_g to 9r_g depending on spin
        if a > 0:
            Z1 = 1 + (1 - a**2)**(1/3) * ((1 + a)**(1/3) + (1 - a)**(1/3))
            Z2 = np.sqrt(3 * a**2 + Z1**2)
            r_ISCO = 3 + Z2 - np.sqrt((3 - Z1) * (3 + Z1 + 2*Z2))
            self.isco_radius = r_ISCO * G * M_cgs / (C**2)
        else:
            self.isco_radius = 6 * G * M_cgs / (C**2)  # Schwarzschild case
    
    @property 
    def L_BZ(self):
        """Blandford-Znajek luminosity in erg/s"""
        return self.power
    
    def get_physical_scales(self):
        """
        Return dictionary of physical scales for geometry calculations.
        """
        return {
            'black_hole_radius': self.black_hole_radius,
            'schwarzschild_radius': self.schwarzschild_radius,
            'isco_radius': self.isco_radius,
            'jet_velocity': self.jet_velocity,
            'power': self.power,
            'energy_density': self.energy_density
        }
    
    def fluctuate(self, t):
        """Simulate time-dependent fluctuations in jet power"""
        # Multiple timescales for realistic variability
        fast_fluct = 0.1 * np.sin(2 * np.pi * t / 3.0)  # 3-second period
        slow_fluct = 0.05 * np.sin(2 * np.pi * t / 20.0)  # 20-second period
        random_fluct = 0.03 * (np.random.random() - 0.5)
        
        fluct_factor = 1.0 + fast_fluct + slow_fluct + random_fluct
        return self.power * fluct_factor

class RelativisticEffects:
    """
    Relativistic effects calculations for jets and emissions.
    
    Handles Doppler factors, relativistic beaming, and gravitational lensing
    with adjustable jet velocity from the BZ mechanism.
    """
    
    def __init__(self, jet_velocity=0.95):
        """
        Initialize relativistic effects calculator.
        
        Args:
            jet_velocity (float): Jet velocity in units of c (default: 0.95)
        """
        self.jet_velocity = jet_velocity
        self.gamma = 1 / np.sqrt(1 - jet_velocity**2)  # Lorentz factor
        
    def update_jet_velocity(self, new_velocity):
        """Update jet velocity and recalculate Lorentz factor"""
        self.jet_velocity = max(0.1, min(0.999, new_velocity))  # Physical limits
        self.gamma = 1 / np.sqrt(1 - self.jet_velocity**2)
        
    def calculate_doppler_factor(self, viewing_angle, jet_direction=1):
        """
        Calculate relativistic Doppler factor.
        
        Formula: δ = 1 / [γ(1 - β cos θ)]
        
        Args:
            viewing_angle (float): Angle between jet and line of sight (radians)
            jet_direction (int): +1 for approaching jet, -1 for receding jet
            
        Returns:
            float: Doppler factor
        """
        beta = self.jet_velocity
        cos_theta = np.cos(viewing_angle) * jet_direction
        doppler_factor = 1 / (self.gamma * (1 - beta * cos_theta))
        
        # Clamp to reasonable range to avoid numerical issues
        return max(0.01, min(doppler_factor, 50.0))
    
    def apply_relativistic_beaming(self, base_intensity, doppler_factor, spectral_index=-0.7):
        """
        Apply relativistic beaming to emission intensity.
        
        For synchrotron radiation: I ∝ δ^(3+α) where α is spectral index
        
        Args:
            base_intensity (float): Intrinsic emission intensity
            doppler_factor (float): Relativistic Doppler factor
            spectral_index (float): Spectral index (default: -0.7 for synchrotron)
            
        Returns:
            float: Beamed intensity
        """
        beaming_power = 3 + spectral_index
        beamed_intensity = base_intensity * (doppler_factor ** beaming_power)
        return beamed_intensity
    
    def gravitational_lensing_deflection(self, impact_parameter, schwarzschild_radius):
        """
        Calculate gravitational lensing deflection angle.
        
        Einstein formula: α = 4GM/c²r = 2r_s/r (weak field approximation)
        
        Args:
            impact_parameter (float): Distance from light ray to black hole center
            schwarzschild_radius (float): Schwarzschild radius of black hole
            
        Returns:
            float: Deflection angle in radians
        """
        if impact_parameter > schwarzschild_radius:
            # Weak field approximation
            deflection = 2 * schwarzschild_radius / impact_parameter
            return min(deflection, np.pi/2)  # Cap at 90 degrees
        return 0
    
    def calculate_time_dilation(self, radius, schwarzschild_radius):
        """
        Calculate gravitational time dilation factor.
        
        Formula: dt/dt_∞ = √(1 - r_s/r)
        
        Args:
            radius (float): Distance from black hole center
            schwarzschild_radius (float): Schwarzschild radius
            
        Returns:
            float: Time dilation factor
        """
        if radius > schwarzschild_radius:
            time_dilation = np.sqrt(1 - schwarzschild_radius / radius)
            return max(time_dilation, 0.1)  # Avoid extreme values
        return 0.1  # Near horizon limit
