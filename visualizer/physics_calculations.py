"""
Physics calculations module for the Blandford-Znajek visualizer
Handles derived quantities, observables, and physics computations
"""

import numpy as np
from PyQt5 import QtWidgets


class PhysicsCalculations:
    """Handles physics calculations and derived quantities"""
    
    def __init__(self, parent_visualizer):
        self.visualizer = parent_visualizer
        self.physics_labels = {}
        self.observables_labels = {}
    
    def create_info_panel(self, main_layout):
        """Create right info panel with derived quantities and time series"""
        info_scroll = QtWidgets.QScrollArea()
        info_scroll.setMinimumWidth(200)  # Minimum width instead of fixed
        info_scroll.setWidgetResizable(True)
        
        info_widget = QtWidgets.QWidget()
        info_layout = QtWidgets.QVBoxLayout(info_widget)
        
        # Derived Physics Quantities
        self.create_physics_display(info_layout)
        
        # Observables Display
        self.create_observables_display(info_layout)
        
        # Time Series Plot (simplified)
        self.create_time_series_display(info_layout)
        
        info_scroll.setWidget(info_widget)
        main_layout.addWidget(info_scroll)
    
    def create_physics_display(self, parent_layout):
        """Create physics quantities display"""
        physics_group = QtWidgets.QGroupBox("Derived Physics")
        physics_layout = QtWidgets.QFormLayout()
        
        # Initialize labels for physics quantities
        physics_quantities = [
            ('schwarzschild_radius', 'Rs:', 'km'),
            ('isco_radius', 'ISCO:', 'Rs'),
            ('jet_power', 'Jet Power:', 'erg/s'),
            ('disk_luminosity', 'Disk Lum:', 'erg/s'),
            ('efficiency', 'Efficiency:', '%'),
            ('event_horizon_area', 'BH Area:', 'km²'),
            ('angular_momentum', 'J:', 'g⋅cm²/s'),
            ('magnetic_flux', 'Φ_B:', 'G⋅cm²')
        ]
        
        for key, label, unit in physics_quantities:
            value_label = QtWidgets.QLabel("Calculating...")
            value_label.setStyleSheet("QLabel { font-family: monospace; }")
            self.physics_labels[key] = value_label
            physics_layout.addRow(f"{label} ({unit})", value_label)
        
        physics_group.setLayout(physics_layout)
        parent_layout.addWidget(physics_group)
    
    def create_observables_display(self, parent_layout):
        """Create observables display"""
        obs_group = QtWidgets.QGroupBox("Observables")
        obs_layout = QtWidgets.QFormLayout()
        
        # Initialize labels for observables
        observable_quantities = [
            ('flux_density', 'Flux Density:', 'Jy'),
            ('spectral_index', 'Spectral Index:', ''),
            ('polarization_fraction', 'Pol. Fraction:', '%'),
            ('brightness_temp', 'Tb:', 'K'),
            ('angular_size', 'Angular Size:', 'mas'),
            ('doppler_factor', 'Doppler Factor:', ''),
            ('redshift', 'Redshift:', ''),
            ('luminosity_distance', 'DL:', 'Mpc')
        ]
        
        for key, label, unit in observable_quantities:
            value_label = QtWidgets.QLabel("Calculating...")
            value_label.setStyleSheet("QLabel { font-family: monospace; }")
            self.observables_labels[key] = value_label
            obs_layout.addRow(f"{label} ({unit})" if unit else f"{label}", value_label)
        
        obs_group.setLayout(obs_layout)
        parent_layout.addWidget(obs_group)
    
    def create_time_series_display(self, parent_layout):
        """Create simplified time series display"""
        time_group = QtWidgets.QGroupBox("Time Series")
        time_layout = QtWidgets.QVBoxLayout()
        
        # Simple text display for time series data
        self.time_series_text = QtWidgets.QTextEdit()
        self.time_series_text.setMaximumHeight(150)
        self.time_series_text.setReadOnly(True)
        self.time_series_text.setStyleSheet("QTextEdit { font-family: monospace; font-size: 9pt; }")
        
        time_layout.addWidget(self.time_series_text)
        time_group.setLayout(time_layout)
        parent_layout.addWidget(time_group)
    
    def update_info_display(self):
        """Update all physics and observable displays"""
        try:
            self.update_physics_quantities()
            self.update_observables()
            self.update_time_series()
        except Exception as e:
            print(f"Info display update failed: {e}")
    
    def update_physics_quantities(self):
        """Calculate and update derived physics quantities"""
        try:
            # Schwarzschild radius
            rs = self.calculate_schwarzschild_radius()
            self.physics_labels['schwarzschild_radius'].setText(f"{rs:.2e}")
            
            # ISCO radius
            isco = self.calculate_isco_radius()
            self.physics_labels['isco_radius'].setText(f"{isco:.2f}")
            
            # Jet power
            jet_power = self.calculate_jet_power()
            self.physics_labels['jet_power'].setText(f"{jet_power:.2e}")
            
            # Disk luminosity
            disk_lum = self.calculate_disk_luminosity()
            self.physics_labels['disk_luminosity'].setText(f"{disk_lum:.2e}")
            
            # Efficiency
            efficiency = self.calculate_efficiency()
            self.physics_labels['efficiency'].setText(f"{efficiency:.1f}")
            
            # Event horizon area
            area = self.calculate_event_horizon_area()
            self.physics_labels['event_horizon_area'].setText(f"{area:.2e}")
            
            # Angular momentum
            J = self.calculate_angular_momentum()
            self.physics_labels['angular_momentum'].setText(f"{J:.2e}")
            
            # Magnetic flux
            flux = self.calculate_magnetic_flux()
            self.physics_labels['magnetic_flux'].setText(f"{flux:.2e}")
            
        except Exception as e:
            print(f"Physics quantities update failed: {e}")
    
    def update_observables(self):
        """Calculate and update observable quantities"""
        try:
            # Flux density
            flux = self.calculate_flux_density()
            self.observables_labels['flux_density'].setText(f"{flux:.2f}")
            
            # Spectral index
            alpha = self.calculate_spectral_index()
            self.observables_labels['spectral_index'].setText(f"{alpha:.2f}")
            
            # Polarization fraction
            pol_frac = self.calculate_polarization_fraction()
            self.observables_labels['polarization_fraction'].setText(f"{pol_frac:.1f}")
            
            # Brightness temperature
            Tb = self.calculate_brightness_temperature()
            self.observables_labels['brightness_temp'].setText(f"{Tb:.2e}")
            
            # Angular size
            size = self.calculate_angular_size()
            self.observables_labels['angular_size'].setText(f"{size:.2f}")
            
            # Doppler factor
            doppler = self.calculate_doppler_factor()
            self.observables_labels['doppler_factor'].setText(f"{doppler:.2f}")
            
            # Redshift (assumed cosmological)
            z = self.calculate_redshift()
            self.observables_labels['redshift'].setText(f"{z:.3f}")
            
            # Luminosity distance
            DL = self.visualizer.distance
            self.observables_labels['luminosity_distance'].setText(f"{DL:.1f}")
            
        except Exception as e:
            print(f"Observables update failed: {e}")
    
    def update_time_series(self):
        """Update time series display"""
        try:
            # Simple time series text
            current_time = getattr(self.visualizer, 'current_time', 0.0)
            jet_power = self.calculate_jet_power()
            
            time_text = f"Time: {current_time:.2f} s\\n"
            time_text += f"Jet Power: {jet_power:.2e} erg/s\\n"
            time_text += f"Viewing Angle: {self.visualizer.viewing_angle:.1f}°\\n"
            
            self.time_series_text.setPlainText(time_text)
            
        except Exception as e:
            print(f"Time series update failed: {e}")
    
    # Physics calculation methods
    def calculate_schwarzschild_radius(self):
        """Calculate Schwarzschild radius in km"""
        G = 6.67430e-11  # m³/kg⋅s²
        c = 2.99792458e8  # m/s
        M_sun = 1.98847e30  # kg
        
        M = self.visualizer.jet.mass * M_sun  # kg
        rs = 2 * G * M / c**2  # meters
        return rs / 1000  # km
    
    def calculate_isco_radius(self):
        """Calculate ISCO radius in units of Schwarzschild radii"""
        a = self.visualizer.jet.spin
        
        # Bardeen, Press & Teukolsky (1972) formula for prograde ISCO
        Z1 = 1 + (1 - a**2)**(1/3) * ((1 + a)**(1/3) + (1 - a)**(1/3))
        Z2 = (3 * a**2 + Z1**2)**0.5
        r_isco = 3 + Z2 - ((3 - Z1) * (3 + Z1 + 2*Z2))**0.5
        
        return r_isco
    
    def calculate_jet_power(self):
        """Calculate Blandford-Znajek jet power in erg/s"""
        # Simplified BZ power formula
        G = 6.67430e-11  # m³/kg⋅s²
        c = 2.99792458e8  # m/s
        M_sun = 1.98847e30  # kg
        
        M = self.visualizer.jet.mass * M_sun  # kg
        a = self.visualizer.jet.spin
        B = self.visualizer.jet.B * 1e-4  # Tesla
        
        # BZ power ~ B² a² M² c (very simplified)
        rs = 2 * G * M / c**2  # Schwarzschild radius
        L_BZ = 6e20 * (B / 1e-4)**2 * a**2 * (M / M_sun)**2  # erg/s
        
        return L_BZ
    
    def calculate_disk_luminosity(self):
        """Calculate accretion disk luminosity"""
        # Simple disk luminosity from accretion rate
        efficiency = 0.1  # 10% efficiency
        c = 2.99792458e10  # cm/s
        mdot = self.visualizer.mdot  # g/s
        
        L_disk = efficiency * mdot * c**2  # erg/s
        return L_disk
    
    def calculate_efficiency(self):
        """Calculate energy extraction efficiency"""
        jet_power = self.calculate_jet_power()
        disk_lum = self.calculate_disk_luminosity()
        
        if disk_lum > 0:
            efficiency = (jet_power / disk_lum) * 100  # percent
            return min(efficiency, 100)  # Cap at 100%
        return 0.0
    
    def calculate_event_horizon_area(self):
        """Calculate event horizon area in km²"""
        rs = self.calculate_schwarzschild_radius() * 1000  # meters
        a = self.visualizer.jet.spin
        
        # Kerr black hole horizon area
        rp = rs/2 * (1 + (1 - a**2)**0.5)  # outer horizon radius
        area = 4 * np.pi * (rp**2 + a**2 * (rs/2)**2)  # m²
        
        return area / 1e6  # km²
    
    def calculate_angular_momentum(self):
        """Calculate black hole angular momentum"""
        G = 6.67430e-11  # m³/kg⋅s²
        c = 2.99792458e8  # m/s
        M_sun = 1.98847e30  # kg
        
        M = self.visualizer.jet.mass * M_sun  # kg
        a = self.visualizer.jet.spin
        
        J = a * G * M**2 / c  # kg⋅m²/s
        return J * 1e7  # g⋅cm²/s
    
    def calculate_magnetic_flux(self):
        """Calculate magnetic flux through black hole"""
        rs = self.calculate_schwarzschild_radius() * 1e5  # cm
        B = self.visualizer.jet.B  # Gauss
        
        # Approximate flux through horizon
        area = np.pi * (rs/2)**2  # cm²
        flux = B * area  # G⋅cm²
        
        return flux
    
    def calculate_flux_density(self):
        """Calculate observed flux density in Jy"""
        # Very simplified calculation
        jet_power = self.calculate_jet_power()  # erg/s
        distance = self.visualizer.distance * 3.086e24  # cm
        
        # Assume 1% of jet power goes to radio emission
        radio_power = 0.01 * jet_power  # erg/s
        
        # Convert to flux density (very rough)
        flux_density = radio_power / (4 * np.pi * distance**2)  # erg/s/cm²
        flux_density *= 1e23  # Convert to Jy
        
        return flux_density
    
    def calculate_spectral_index(self):
        """Calculate spectral index"""
        # Typical values for AGN jets
        return -0.7
    
    def calculate_polarization_fraction(self):
        """Calculate polarization fraction"""
        # Typical values for AGN jets
        return 15.0  # percent
    
    def calculate_brightness_temperature(self):
        """Calculate brightness temperature"""
        flux = self.calculate_flux_density()  # Jy
        size = self.calculate_angular_size()  # mas
        
        # Brightness temperature formula
        if size > 0:
            Tb = 1.22e12 * flux / (size**2)  # K
            return Tb
        return 0.0
    
    def calculate_angular_size(self):
        """Calculate angular size in milliarcseconds"""
        rs = self.calculate_schwarzschild_radius() * 1e5  # cm
        distance = self.visualizer.distance * 3.086e24  # cm
        
        # Angular size of ~10 Schwarzschild radii
        physical_size = 10 * rs  # cm
        angular_size = physical_size / distance  # radians
        angular_size *= 206265000  # milliarcseconds
        
        return angular_size
    
    def calculate_doppler_factor(self):
        """Calculate Doppler factor for current viewing angle"""
        beta = self.visualizer.jet.jet_velocity
        gamma = 1 / (1 - beta**2)**0.5
        theta = np.radians(self.visualizer.viewing_angle)
        
        doppler = 1 / (gamma * (1 - beta * np.cos(theta)))
        return doppler
    
    def calculate_redshift(self):
        """Calculate redshift based on distance (Hubble law)"""
        H0 = 70  # km/s/Mpc
        distance = self.visualizer.distance  # Mpc
        
        # Hubble law: v = H0 * D
        v = H0 * distance  # km/s
        c = 299792.458  # km/s
        
        # Non-relativistic redshift
        z = v / c
        return z
