"""
Astrophysical Jet Simulation: Blandford–Znajek Process
Standalone PyQt5 + PyVista GUI
"""
import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
import pyvista as pv
from pyvistaqt import QtInteractor

# Physical constants
C = 2.99792458e10  # speed of light [cm/s]
G = 6.67430e-8     # gravitational constant [cm^3/g/s^2]
MSUN = 1.98847e33  # solar mass [g]
KAPPA = 0.05       # efficiency factor (typical value)

class BlandfordZnajekJet:
    def __init__(self, mass, spin, B):
        self.mass = mass  # in solar masses
        self.spin = spin  # dimensionless (0 < a < 1)
        self.B = B        # in Gauss
        self.update_jet_power()

    def update_jet_power(self):
        M_cgs = self.mass * MSUN
        a = self.spin
        B = self.B
        # Blandford–Znajek formula (simplified)
        self.power = (KAPPA / (4 * np.pi * C)) * (a ** 2) * (B ** 2) * (M_cgs ** 2)
        self.energy_density = self.power / (np.pi * (1e15)**2)  # arbitrary cross-section

    def fluctuate(self, t):
        # Simulate fluctuations in jet power
        fluct = 1 + 0.2 * np.sin(2 * np.pi * t / 5) + 0.1 * np.random.randn()
        self.power *= fluct
        self.energy_density *= fluct

class JetVisualizer(QtWidgets.QWidget):
    def __init__(self, jet, parent=None):
        super().__init__(parent)
        self.jet = jet
        self.init_ui()
    def init_scene(self):
        self.plotter.clear()
        # Black hole (supermassive, small sphere)
        self.bh_radius = 1.0
        sphere = pv.Sphere(radius=self.bh_radius, center=(0,0,0), theta_resolution=64, phi_resolution=64)
        self.plotter.add_mesh(sphere, color='black', name='bh')
        # Set a fully black background for the left panel
        self.plotter.set_background('black')
        # Uniform star distribution across the entire visible volume
        self.disk_radius = 10 * self.bh_radius
        # Define the maximum zoomable region
        max_zoom_box = self.disk_radius * 30
        n_stars = 8000
        star_xyz = np.random.uniform(-max_zoom_box, max_zoom_box, (n_stars, 3))
        star_colors = np.random.uniform(0.7, 1.0, (n_stars, 3))
        self.plotter.add_points(star_xyz, scalars=star_colors, rgb=True, point_size=2, name='stars', render_points_as_spheres=True, emissive=True)
        # Add faint nebulae/star clusters (galaxy features)
        n_nebulae = 10
        for i in range(n_nebulae):
            neb_type = np.random.choice(['spiral', 'globular', 'filament'])
            neb_center = np.random.uniform(-max_zoom_box*0.7, max_zoom_box*0.7, 3)
            if neb_type == 'spiral':
                # Spiral arm: points along a spiral curve
                t = np.linspace(0, 4*np.pi, 400)
                r = np.linspace(self.disk_radius*1.5, self.disk_radius*3, 400)
                x = neb_center[0] + r * np.cos(t)
                y = neb_center[1] + r * np.sin(t)
                z = neb_center[2] + np.random.normal(0, self.disk_radius*0.3, 400)
                neb_points = np.column_stack([x, y, z])
                neb_color = np.array([0.6, 0.4, 0.9]) + np.random.normal(0, 0.08, 3)
                neb_opacity = 0.12
            elif neb_type == 'globular':
                # Spherical cluster
                neb_points = neb_center + np.random.normal(0, self.disk_radius*1.2, (350, 3))
                neb_color = np.array([0.7, 0.5, 0.8]) + np.random.normal(0, 0.1, 3)
                neb_opacity = 0.18
            else:
                # Filament: elongated cloud
                direction = np.random.normal(0, 1, 3)
                direction /= np.linalg.norm(direction)
                base = neb_center + np.random.normal(0, self.disk_radius*0.5, (350, 3))
                filament = np.linspace(-self.disk_radius*3, self.disk_radius*3, 350).reshape(-1,1) * direction
                neb_points = base + filament
                neb_color = np.array([0.5, 0.3, 0.7]) + np.random.normal(0, 0.09, 3)
                neb_opacity = 0.10
            neb_colors = np.tile(np.clip(neb_color, 0, 1), (neb_points.shape[0], 1))
            self.plotter.add_points(neb_points, scalars=neb_colors, rgb=True, point_size=10, opacity=neb_opacity, name=f'nebula_{i}', render_points_as_spheres=True, emissive=False)
        # Optionally add a faint volumetric mesh for a galaxy cluster
        cluster_center = np.random.uniform(-max_zoom_box*0.5, max_zoom_box*0.5, 3)
        cluster = pv.Sphere(radius=self.disk_radius*4, center=cluster_center, theta_resolution=32, phi_resolution=32)
        self.plotter.add_mesh(cluster, color=[0.4,0.3,0.7], opacity=0.05, name='galaxy_cluster')
        # Set camera zoom limits and initial view
        self.plotter.camera.zoom(1.0)
        self.plotter.camera.clipping_range = [self.disk_radius * 0.2, max_zoom_box * 2]
        self.plotter.reset_camera()
        # Accretion disk (flat, wide, color gradient)
        disk_thickness = 0.3  # very flat
        n_ring, n_sides = 180, 80
        theta = np.linspace(0, 2*np.pi, n_ring)
        r = np.linspace(self.bh_radius * 1.2, self.disk_radius, n_sides)
        theta, r = np.meshgrid(theta, r)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        z = disk_thickness * (np.random.rand(*r.shape) - 0.5) * 0.1  # add slight noise for realism
        pts = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
        # Color gradient: red/orange in center, gray at edge
        radii = np.sqrt(x.ravel()**2 + y.ravel()**2)
        disk_colors = np.zeros((radii.size, 3))
        # Center: red/orange, edge: gray
        disk_colors[:,0] = np.clip(1 - (radii - self.bh_radius)/(self.disk_radius - self.bh_radius), 0, 1)  # red
        disk_colors[:,1] = np.clip(0.5 * (1 - (radii - self.bh_radius)/(self.disk_radius - self.bh_radius)), 0, 0.5)  # orange
        disk_colors[:,2] = np.clip(0.5 + 0.5 * (radii - self.bh_radius)/(self.disk_radius - self.bh_radius), 0.5, 1)  # gray
        # Faces
        faces = []
        for i in range(n_sides - 1):
            for j in range(n_ring - 1):
                p0 = i * n_ring + j
                p1 = p0 + 1
                p2 = p0 + n_ring + 1
                p3 = p0 + n_ring
                faces.extend([4, p0, p1, p2, p3])
        faces = np.array(faces)
        disk_mesh = pv.PolyData(pts, faces)
        self.disk = disk_mesh
        self.disk_colors = disk_colors
        self.plotter.add_mesh(self.disk, scalars=self.disk_colors, rgb=True, opacity=0.85, name='disk')
        # Jet: collimated, extends well beyond disk
        self.jet_length = self.disk_radius * 2.5
        self.jet_radius_base = 0.3 * self.bh_radius
        self.jet_radius_collar = 0.7 * self.bh_radius
        n_z = 120
        n_theta = 24
        z = np.linspace(self.bh_radius * 1.1, self.jet_length, n_z)
        theta = np.linspace(0, 2*np.pi, n_theta)
        # Jet in +z direction
        jet_points_pos = np.zeros((n_z, n_theta, 3))
        for i, zi in enumerate(z):
            if zi < self.disk_radius * 1.2:
                rj = self.jet_radius_base + (self.jet_radius_collar - self.jet_radius_base) * (zi/(self.disk_radius*1.2))
            else:
                rj = self.jet_radius_collar
            for j, th in enumerate(theta):
                xj = rj * np.cos(th)
                yj = rj * np.sin(th)
                jet_points_pos[i, j] = [xj, yj, zi]
        jet_mesh_pos = pv.StructuredGrid()
        jet_mesh_pos.points = jet_points_pos.reshape(-1, 3)
        jet_mesh_pos.dimensions = (n_z, n_theta, 1)
        jet_colors_pos = np.zeros(n_z * n_theta)
        jet_colors_pos[:] = np.linspace(1, 0.3, n_z).repeat(n_theta)
        self.jet_mesh = jet_mesh_pos
        self.jet_colors = jet_colors_pos
        self.plotter.add_mesh(jet_mesh_pos, scalars=jet_colors_pos, cmap='Blues', name='jet_pos', opacity=0.95)
        # Jet in -z direction (mirror)
        jet_points_neg = np.zeros((n_z, n_theta, 3))
        for i, zi in enumerate(z):
            if zi < self.disk_radius * 1.2:
                rj = self.jet_radius_base + (self.jet_radius_collar - self.jet_radius_base) * (zi/(self.disk_radius*1.2))
            else:
                rj = self.jet_radius_collar
            for j, th in enumerate(theta):
                xj = rj * np.cos(th)
                yj = rj * np.sin(th)
                jet_points_neg[i, j] = [xj, yj, -zi]
        jet_mesh_neg = pv.StructuredGrid()
        jet_mesh_neg.points = jet_points_neg.reshape(-1, 3)
        jet_mesh_neg.dimensions = (n_z, n_theta, 1)
        jet_colors_neg = np.zeros(n_z * n_theta)
        jet_colors_neg[:] = np.linspace(1, 0.3, n_z).repeat(n_theta)
        self.plotter.add_mesh(jet_mesh_neg, scalars=jet_colors_neg, cmap='Blues', name='jet_neg', opacity=0.95)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(100)
        self.t = 0

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        # 3D Visualization
        self.plotter = QtInteractor(self)
        self.plotter.set_background('black')
        layout.addWidget(self.plotter.interactor)
        # Right panel: description + stats + controls
        right_panel = QtWidgets.QVBoxLayout()
        self.desc = QtWidgets.QTextEdit()
        self.desc.setReadOnly(True)
        self.desc.setFixedHeight(180)
        self.desc.setStyleSheet('background-color: black; color: #fff; font-size: 12pt; border: none;')
        self.stats = QtWidgets.QTextEdit()
        self.stats.setReadOnly(True)
        self.stats.setFixedWidth(250)
        self.stats.setStyleSheet('background-color: black; color: #fff; font-size: 11pt; border: none;')
        right_panel.addWidget(self.desc)
        right_panel.addWidget(self.stats)

    # Controls for mass, spin, magnetic field
    controls = QtWidgets.QGroupBox('Jet Parameters')
    controls_layout = QtWidgets.QFormLayout()

    self.mass_edit = QtWidgets.QLineEdit(str(self.jet.mass))
    self.mass_edit.setPlaceholderText('Mass (M_sun)')
    controls_layout.addRow('Mass:', self.mass_edit)

    self.spin_edit = QtWidgets.QLineEdit(str(self.jet.spin))
    self.spin_edit.setPlaceholderText('Spin (0.01 - 0.99)')
    controls_layout.addRow('Spin:', self.spin_edit)

    self.B_edit = QtWidgets.QLineEdit(str(self.jet.B))
    self.B_edit.setPlaceholderText('Magnetic Field (G)')
    controls_layout.addRow('Magnetic Field:', self.B_edit)

    controls.setLayout(controls_layout)
    right_panel.addWidget(controls)

    # Connect controls to update handler (on text change)
    self.mass_edit.editingFinished.connect(self.update_parameters)
    self.spin_edit.editingFinished.connect(self.update_parameters)
    self.B_edit.editingFinished.connect(self.update_parameters)

    layout.addLayout(right_panel)
    self.setLayout(layout)
    # Set the main widget background to black
    self.setStyleSheet('background-color: black;')
    self.init_scene()
    self.set_description()

    def update_parameters(self):
        # Update jet parameters from text fields and re-init scene
        try:
            mass = float(self.mass_edit.text())
            spin = float(self.spin_edit.text())
            B = float(self.B_edit.text())
            # Validate ranges
            if not (1 <= mass <= 100):
                raise ValueError('Mass out of range')
            if not (0.01 <= spin <= 0.99):
                raise ValueError('Spin out of range')
            if not (1e12 <= B <= 1e16):
                raise ValueError('Magnetic field out of range')
            self.jet.mass = mass
            self.jet.spin = spin
            self.jet.B = B
            self.jet.update_jet_power()
            self.init_scene()
        except Exception:
            # Optionally show error, but just ignore invalid input for now
            pass

    def set_description(self):
        self.desc.setText(
            "Astrophysical Jet Simulation\n\n"
            "This program visualizes a relativistic jet powered by the Blandford–Znajek process, where a rotating black hole extracts energy from its spin via magnetic fields, launching powerful jets from its poles.\n\n"
            "The Blandford–Znajek process describes how magnetic fields threading a spinning black hole can tap its rotational energy, producing highly energetic outflows observed in quasars and active galactic nuclei.\n\n"
            "Interact with the 3D view: rotate, zoom, and click glowing points for local jet and disk properties."
        )

    def create_flat_torus(self, R, r, n_ring, n_sides):
        # Parametric flat torus mesh with temperature
        theta = np.linspace(0, 2*np.pi, n_ring)
        phi = np.linspace(0, 2*np.pi, n_sides)
        theta, phi = np.meshgrid(theta, phi)
        x = (R + r * np.cos(phi)) * np.cos(theta)
        y = (R + r * np.cos(phi)) * np.sin(theta)
        z = 0.05 * np.sin(phi)  # keep disk flat
        pts = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
        # Temperature by radius (hotter closer to BH)
        radii = np.sqrt(x.ravel()**2 + y.ravel()**2)
        temps = 2e7 * (1 - (radii - R) / (R + r))
        # Faces
        faces = []
        for i in range(n_sides - 1):
            for j in range(n_ring - 1):
                p0 = i * n_ring + j
                p1 = p0 + 1
                p2 = p0 + n_ring + 1
                p3 = p0 + n_ring
                faces.extend([4, p0, p1, p2, p3])
        faces = np.array(faces)
        torus = pv.PolyData(pts, faces)
        return torus, temps
    # Jet
        # Glowing red dots (important info)
        self.add_glowing_dots()
        # Interactive points
        self.add_interactive_points()
        self.plotter.reset_camera()

    def add_glowing_dots(self):
        # Key points: jet base, disk edge, jet tip
        points = np.array([
            [0, 0, 1],  # jet base
            [self.disk_radius, 0, 0],  # disk edge
            [0, 0, self.jet_length]  # jet tip
        ])
        self.plotter.add_points(points, color='red', point_size=22, name='glow_dots', render_points_as_spheres=True, emissive=True)

    def create_jet_points(self):
        # Create a conical/collimated jet mesh
        n_z = 50
        n_theta = 20
        z = np.linspace(1, self.jet_length, n_z)
        theta = np.linspace(0, 2*np.pi, n_theta)
        points = np.zeros((n_z, n_theta, 3))
        for i, zi in enumerate(z):
            r = self.jet_radius * (1 - 0.7 * zi / self.jet_length)  # collimation
            for j, th in enumerate(theta):
                x = r * np.cos(th)
                y = r * np.sin(th)
                points[i, j] = [x, y, zi]
        return points

    def compute_jet_colors(self):
        # Color gradient: blue (base) to white (tip)
        n_z = 120  # match jet mesh
        n_theta = 24  # match jet mesh
        colors = np.linspace(1, 0.3, n_z)
        colors = np.repeat(colors, n_theta)
        return colors

    def add_interactive_points(self):
        # Add clickable/hoverable points along the jet axis and disk
        n_points = 8
        z = np.linspace(2, self.jet_length, n_points)
        jet_points = np.array([[0, 0, zi] for zi in z])
        # Disk points (sampled around ring)
        theta = np.linspace(0, 2*np.pi, 8, endpoint=False)
        disk_points = np.array([
            [self.disk_radius * np.cos(th), self.disk_radius * np.sin(th), 0] for th in theta
        ])
        all_points = np.vstack([jet_points, disk_points])
        self.plotter.add_points(all_points, color='yellow', point_size=15, name='jet_points', pickable=True)
        self.plotter.enable_point_picking(callback=self.on_pick, use_mesh=True, show_message=False)

    def on_pick(self, picked):
        if picked is not None:
            x, y, z = picked
            # Disk or jet?
            if abs(z) < 1.5:
                # Disk point
                r = np.sqrt(x**2 + y**2)
                v_phi = 0.3 * C * (self.disk_radius / max(r, 1))  # simple Keplerian
                temp = 2e7 * (1 - abs(r - self.disk_radius)/self.disk_radius)
                msg = f"Accretion Disk at r={r:.2f}:\nOrbital Velocity: {v_phi:.2e} cm/s\nTemperature: {temp:.2e} K"
            else:
                # Jet point
                velocity = 0.99 * C * (1 - z/self.jet_length)
                luminosity = self.jet.power * (1 - z/self.jet_length)
                temperature = 1e9 * (1 - z/self.jet_length)
                msg = f"Jet Properties at z={z:.2f}:\nVelocity: {velocity:.2e} cm/s\nLuminosity: {luminosity:.2e} erg/s\nTemperature: {temperature:.2e} K"
            QtWidgets.QMessageBox.information(self, "Properties", msg)

    def update_simulation(self):
        self.t += 0.1
        self.jet.fluctuate(self.t)
    # Animate accretion disk rotation (spin, no flashing)
        angle = (self.t * 30) % 360
        # Rotate the disk mesh and update the plotter (no flashing)
        self.plotter.remove_actor('disk')
        disk_rot = self.disk.copy()
        disk_rot.rotate_z(angle, point=(0,0,0))
        self.plotter.add_mesh(disk_rot, scalars=self.disk_colors, rgb=True, opacity=0.85, name='disk')
        # Update stats
        self.stats.setText(
            f"Black Hole Mass: {self.jet.mass:.2f} M_sun\nSpin: {self.jet.spin:.2f}\nMagnetic Field: {self.jet.B:.2e} G\n"
            f"\nJet Power: {self.jet.power:.2e} erg/s\nEnergy Density: {self.jet.energy_density:.2e} erg/cm^3\nTime: {self.t:.2f} s"
        )
        # Update jet color for animation
        if hasattr(self, 'jet_mesh'):
            self.jet_colors = self.compute_jet_colors() * (1 + 0.2 * np.sin(self.t))
            self.plotter.update_scalars(self.jet_colors, mesh=self.jet_mesh)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # Default parameters
    mass = 10      # solar masses
    spin = 0.8     # dimensionless
    B = 1e15       # Gauss
    jet = BlandfordZnajekJet(mass, spin, B)
    win = JetVisualizer(jet)
    win.setWindowTitle("Blandford–Znajek Jet Simulation")
    win.resize(1200, 700)
    win.show()
    sys.exit(app.exec_())
