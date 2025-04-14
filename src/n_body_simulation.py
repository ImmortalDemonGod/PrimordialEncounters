import rebound
import numpy as np
# Import the analytic impulse calculation function
from analytic_impulse import calculate_velocity_kick, G as analytic_G # Use G from analytic_impulse for consistency check

# Define conversion factor for velocity: (AU/day) to (AU / (yr/2pi))
# 1 yr = 365.25 days => 1 day = 1/365.25 yr
# 1 day = (2*pi / 365.25) * (yr/2pi)
# AU/day = AU / ( (2*pi / 365.25) * (yr/2pi) ) = (365.25 / (2*pi)) * AU/(yr/2pi)
VELOCITY_DAY_TO_REBOUND = 365.25 / (2.0 * np.pi)

class NBodySimulation:
    """
    Handles the setup and execution of N-body simulations using REBOUND,
    specifically for simulating the Solar System with an additional PBH.
    Includes functionality to apply analytic impulse kicks.
    """
    def __init__(self, integrator='whfast', time_step=None):
        """
        Initializes the REBOUND simulation.

        Args:
            integrator (str): The integrator to use ('whfast', 'ias15', etc.).
                              Defaults to 'whfast'.
            time_step (float, optional): The timestep for the integrator, if required
                                         (e.g., for WHFast). Units are yr/(2pi).
                                         Defaults to None (REBOUND might choose one).
        """
        self.sim = rebound.Simulation()
        self.sim.integrator = integrator

        # Store for potential reset
        self._integrator = integrator
        self._time_step = time_step

        # Set simulation units (AU, Solar Masses, yr/2pi)
        self.sim.G = 4 * np.pi**2 # Gravitational constant in AU^3 / (M_sun * (yr/2pi)^2)
        # Verify consistency with analytic module G
        assert np.isclose(self.sim.G, analytic_G), "G mismatch between simulation and analytic modules!"

        if time_step is not None:
             # Check if integrator requires dt (like whfast)
             if integrator.lower() in ['whfast', 'mercurius']:
                 self.sim.dt = time_step
                 print(f"Set timestep to {time_step} yr/(2pi).")
             else:
                 print(f"Warning: Timestep provided but integrator '{integrator}' might not use a fixed dt.")
        elif integrator.lower() in ['whfast', 'mercurius']:
             # Default timestep for WHFast if none provided (adjust as needed)
             default_dt = 0.001 # yr/(2pi) - corresponds to ~0.06 years
             self.sim.dt = default_dt
             print(f"Using default timestep {default_dt} yr/(2pi) for {integrator}.")

        print(f"Initialized REBOUND simulation with {integrator} integrator (G={self.sim.G:.4f}).")

    def get_simulation_time(self):
        """
        Gets the current simulation time.

        Returns:
            float: The current simulation time in years.
        """
        return self.sim.t / (2 * np.pi)

    def add_solar_system(self, date=None):
        """
        Adds the major Solar System bodies (Sun + 8 planets) to the simulation.
        Uses REBOUND's built-in function which sources data from JPL Horizons.

        Args:
            date (str, optional): The date for which to fetch the initial conditions
                                  in 'YYYY-MM-DD HH:MM' format. Defaults to REBOUND's
                                  default (often J2000.0).
        """
        print(f"Adding Solar System bodies for date: {date or 'default'}...")
        try:
            # Ensure simulation time is 0 before adding bodies at a specific date
            # This is crucial as add_solar_system sets t=0 internally based on the date
            if not np.isclose(self.sim.t, 0.0):
                 print(f"Warning: Simulation time is {self.get_simulation_time():.4f} years. "
                       "REBOUND's add_solar_system will reset time based on the provided date. "
                       "Ensure this is intended.")
                 # If adding bodies *after* some evolution, manual addition is needed.

            self.sim.add_solar_system(date=date)
            # Assign labels for easier access if not already done by rebound
            # (rebound usually assigns names like 'Sun', 'Jupiter', etc.)
            for p in self.sim.particles:
                 if not hasattr(p, 'label') or not p.label:
                     # Attempt to get name from hash (rebound stores names as hashes)
                     try:
                         p.label = p.name # type: ignore # Known dynamic attribute issue
                     except:
                         # Fallback label
                         p.label = f"particle_{p.index}"
            print(f"Successfully added {self.sim.N} particles (Sun and planets). Current time: {self.get_simulation_time():.4f} years.")
        except Exception as e:
            print(f"Error adding Solar System bodies: {e}")
            # Consider fallback or raising the error

    def add_pbh(self, mass, position, velocity, label="PBH"):
        """
        Adds a Primordial Black Hole (PBH) or any custom particle to the simulation.

        Args:
            mass (float): Mass of the PBH (in Solar masses).
            position (list or np.ndarray): Initial position [x, y, z] (in AU).
            velocity (list or np.ndarray): Initial velocity [vx, vy, vz] (in AU / (year / 2pi)).
                                          Note the velocity units required by REBOUND.
            label (str): A label for the particle. Defaults to "PBH".
        """
        if len(position) != 3 or len(velocity) != 3:
            raise ValueError("Position and velocity must be 3D vectors.")

        print(f"Adding particle '{label}' with mass {mass:.2e} M_sun...")
        # Ensure label is assigned correctly
        self.sim.add(m=mass, x=position[0], y=position[1], z=position[2],
                     vx=velocity[0], vy=velocity[1], vz=velocity[2], label=label)
        # Verify label assignment (REBOUND might handle labels differently based on version/context)
        # Accessing the last added particle
        new_particle = self.sim.particles[-1]
        # Check and explicitly set label if needed (REBOUND sometimes needs help)
        if getattr(new_particle, 'label', None) != label: # type: ignore # Known dynamic attribute issue
             print(f"Warning: Label '{label}' might not be set correctly on the particle object. Manually setting.")
             new_particle.label = label # type: ignore # Known dynamic attribute issue

        print(f"Particle '{label}' added. Total particles: {self.sim.N}")

    def run_simulation(self, duration):
        """
        Runs the simulation for a specified duration from the current time.

        Args:
            duration (float): The total time to simulate (in years).
        """
        # Convert duration from years to REBOUND's time unit (years / 2pi)
        rebound_time_duration = duration * 2 * np.pi
        current_rebound_time = self.sim.t
        target_rebound_time = current_rebound_time + rebound_time_duration

        current_time_years = current_rebound_time / (2 * np.pi)
        target_time_years = target_rebound_time / (2 * np.pi)

        print(f"Running simulation from t={current_time_years:.4f} years for {duration:.4f} years (until t={target_time_years:.4f} years)...")
        self.sim.integrate(target_rebound_time)
        final_time_years = self.sim.t / (2 * np.pi)
        print(f"Simulation finished at t={final_time_years:.4f} years.")

    def integrate_to_time(self, target_time_years):
        """
        Integrates the simulation precisely to a specified target time.

        Args:
            target_time_years (float): The absolute time to integrate to (in years).
        """
        target_rebound_time = target_time_years * 2 * np.pi
        current_rebound_time = self.sim.t
        current_time_years = current_rebound_time / (2 * np.pi)

        if target_rebound_time < current_rebound_time:
             print(f"Warning: Target time {target_time_years:.4f} years is before current time {current_time_years:.4f} years. No integration performed.")
             return

        if np.isclose(target_rebound_time, current_rebound_time):
             print(f"Simulation already at target time {target_time_years:.4f} years.")
             return

        print(f"Integrating simulation from t={current_time_years:.4f} years to t={target_time_years:.4f} years...")
        self.sim.integrate(target_rebound_time, exact_finish_time=1) # Use exact_finish_time=1 for precision
        final_time_years = self.sim.t / (2 * np.pi)
        # Check if integration reached the target time accurately
        if not np.isclose(self.sim.t, target_rebound_time):
             print(f"Warning: Integration finished at t={final_time_years:.4f} years, slightly different from target {target_time_years:.4f} years.")
        else:
             print(f"Integration finished precisely at t={final_time_years:.4f} years.")

    def get_particle_state(self, label):
         """
         Gets the state vector (position, velocity) for a particle by its label.

         Args:
             label (str): The label of the particle to find.

         Returns:
             tuple: A tuple containing (position, velocity) as numpy arrays (AU, AU/(yr/2pi)),
                    or (None, None) if the particle is not found.
         """
         for p in self.sim.particles:
             # Check if particle has a label attribute and if it matches
             particle_label = getattr(p, 'label', None) # type: ignore # Known dynamic attribute issue
             if particle_label == label:
                 pos = np.array([p.x, p.y, p.z])
                 vel = np.array([p.vx, p.vy, p.vz])
                 return pos, vel
         print(f"Warning: Particle with label '{label}' not found.")
         return None, None

    def apply_analytic_kick(self, pbh_label, target_body_label):
        """
        Calculates and applies an analytic impulse kick to a target body due to a PBH encounter.

        Assumes the simulation is at the initial time (t=0) where initial positions/velocities
        are used for the kick calculation. Integrates to the time of closest approach (t_ca),
        applies the kick, and leaves the simulation at t_ca.

        Args:
            pbh_label (str): The label of the PBH particle in the simulation.
            target_body_label (str): The label of the Solar System body to apply the kick to.

        Returns:
            bool: True if the kick was successfully applied, False otherwise.
        """
        print(f"\nApplying analytic kick from '{pbh_label}' to '{target_body_label}'...")
        initial_time_years = self.get_simulation_time()
        # We calculate the kick based on the state at the *current* simulation time.
        # The analytic formula assumes this state is the 'initial' state for the encounter.
        print(f"Calculating kick based on state at t = {initial_time_years:.4f} years.")

        # Get initial states at current time
        pbh_pos, pbh_vel = self.get_particle_state(pbh_label)
        body_pos, body_vel = self.get_particle_state(target_body_label)
        pbh_mass = None
        for p in self.sim.particles:
             if getattr(p, 'label', None) == pbh_label: # type: ignore # Known dynamic attribute issue
                 pbh_mass = p.m
                 break

        if pbh_pos is None or body_pos is None or pbh_mass is None:
            print("Error: Could not find PBH or target body, or PBH mass. Kick not applied.")
            return False

        # Calculate kick and time of closest approach using the analytic module
        print("Calculating delta_v and t_ca using analytic_impulse module...")
        delta_v, t_ca_rebound_relative = calculate_velocity_kick(
            pbh_mass=pbh_mass,
            pbh_position=pbh_pos,
            pbh_velocity=pbh_vel,
            body_position=body_pos,
            body_velocity=body_vel
        )
        # t_ca is relative to the current simulation time
        t_ca_years_relative = t_ca_rebound_relative / (2 * np.pi)
        t_ca_absolute_rebound = self.sim.t + t_ca_rebound_relative
        t_ca_absolute_years = t_ca_absolute_rebound / (2 * np.pi)


        print(f"  Calculated delta_v: {delta_v} AU/(yr/2pi)")
        print(f"  Calculated t_ca (relative): {t_ca_rebound_relative:.4f} rebound units = {t_ca_years_relative:.4f} years")
        print(f"  Absolute time of closest approach: {t_ca_absolute_years:.4f} years")


        if np.allclose(delta_v, 0):
             print("Calculated delta_v is zero. No kick applied.")
             # Optionally integrate to t_ca anyway if needed for consistency?
             # self.integrate_to_time(t_ca_absolute_years)
             return True # Technically successful, just no change.

        if t_ca_rebound_relative <= 0:
             # This means closest approach already happened relative to the current time.
             # The impulse approximation assumes instantaneous kick at t_ca.
             # Applying it now might be inaccurate.
             print(f"Warning: Calculated relative t_ca ({t_ca_years_relative:.4f} years) is non-positive. "
                   "Closest approach is in the past relative to current time. Applying kick at current time.")
             t_apply_rebound = self.sim.t
             t_apply_years = self.get_simulation_time()
        else:
             t_apply_rebound = t_ca_absolute_rebound
             t_apply_years = t_ca_absolute_years


        # Integrate simulation precisely to the time of kick application
        self.integrate_to_time(t_apply_years)

        # Find the target particle object again (its state might have changed slightly)
        target_particle = None
        for p in self.sim.particles:
            if getattr(p, 'label', None) == target_body_label: # type: ignore # Known dynamic attribute issue
                target_particle = p
                break

        if target_particle is None:
             # Should not happen if found initially, but check anyway
             print(f"Error: Could not find target body '{target_body_label}' at t_apply={t_apply_years:.4f} years. Kick not applied.")
             # Potentially rewind simulation? For now, just report error.
             return False

        # Apply the kick by modifying the particle's velocity
        print(f"Applying delta_v to '{target_body_label}' at t = {self.get_simulation_time():.4f} years...")
        vel_before = np.array([target_particle.vx, target_particle.vy, target_particle.vz])
        print(f"  Velocity before kick: [{vel_before[0]:.4e}, {vel_before[1]:.4e}, {vel_before[2]:.4e}]")
        target_particle.vx += delta_v[0]
        target_particle.vy += delta_v[1]
        target_particle.vz += delta_v[2]
        vel_after = np.array([target_particle.vx, target_particle.vy, target_particle.vz])
        print(f"  Velocity after kick:  [{vel_after[0]:.4e}, {vel_after[1]:.4e}, {vel_after[2]:.4e}]")

        print(f"Analytic kick successfully applied. Simulation time is now at t_apply = {self.get_simulation_time():.4f} years.")
        return True

    def get_particle_data(self):
        """
        Retrieves the current state (positions, velocities, masses, labels) of all particles.

        Returns:
            list: A list of dictionaries, where each dictionary contains the
                  data for one particle ('label', 'mass', 'position', 'velocity').
                  Positions are in AU, velocities in AU/(year / 2pi).
        """
        particles_data = []
        for i, p in enumerate(self.sim.particles):
            # Ensure label exists
            label = getattr(p, 'label', f'particle_{i}') # type: ignore # Known dynamic attribute issue
            if not label: # Handle empty string labels if they occur
                 label = f'particle_{i}'
            data = {
                'index': i,
                'label': label,
                'mass': p.m,
                'position': np.array([p.x, p.y, p.z]), # Return as numpy arrays
                'velocity': np.array([p.vx, p.vy, p.vz]) # Return as numpy arrays
            }
            particles_data.append(data)
        return particles_data


# Example Usage (modified to use apply_analytic_kick)
if __name__ == '__main__':
    print("Running NBodySimulation example with Analytic Kick...")

    # Initialize simulation
    simulation = NBodySimulation(integrator='ias15') # IAS15 is good for varying timescales

    # Add Solar System bodies at t=0
    simulation.add_solar_system(date="2025-04-10 00:00") # Use current date for example

    # Define PBH parameters (using analytic_impulse example values for consistency)
    pbh_mass = 1e-10  # M_sun
    pbh_position = [-10.0, 0.1, 0.0] # AU
    # Velocity needs conversion from analytic example (AU/day) if different, but analytic_impulse now uses rebound units
    # analytic_impulse example: 5510 AU/(yr/2pi)
    pbh_velocity = [5510.0, 0, 0] # AU/(yr/2pi)
    pbh_label = "PBH_Encounter"

    # Add the PBH
    simulation.add_pbh(mass=pbh_mass, position=pbh_position, velocity=pbh_velocity, label=pbh_label)

    # Target body for the kick
    target = "Earth"

    # Get initial state for reference
    print("\nInitial States (t=0):")
    initial_data = simulation.get_particle_data()
    for p in initial_data:
         # Use numpy array formatting for cleaner output
         pos_str = np.array2string(p['position'], precision=3, floatmode='fixed', sign=' ')
         vel_str = np.array2string(p['velocity'], precision=3, floatmode='fixed', sign=' ')
         print(f"  {p['label']:<10}: Pos={pos_str}, Vel={vel_str}")

    # Apply the analytic kick
    kick_applied = simulation.apply_analytic_kick(pbh_label=pbh_label, target_body_label=target)

    if kick_applied:
        # Simulation time is now at t_ca (or current time if t_ca was past)
        time_after_kick = simulation.get_simulation_time()
        print(f"\nSimulation state at t = {time_after_kick:.4f} years (after kick attempt):")
        state_at_kick_time = simulation.get_particle_data()
        for p in state_at_kick_time:
             # Highlight the kicked body
             marker = " <<< KICKED" if p['label'] == target else ""
             pos_str = np.array2string(p['position'], precision=3, floatmode='fixed', sign=' ')
             vel_str = np.array2string(p['velocity'], precision=3, floatmode='fixed', sign=' ')
             print(f"  {p['label']:<10}: Pos={pos_str}, Vel={vel_str}{marker}")

        # Optionally, continue simulation after the kick
        duration_after_kick = 10.0 # Simulate for 10 more years
        print(f"\nContinuing simulation for {duration_after_kick:.2f} years after the kick...")
        simulation.run_simulation(duration=duration_after_kick)

        # Get final particle data
        final_data = simulation.get_particle_data()
        print("\nFinal particle data (t = {:.4f} years):".format(simulation.get_simulation_time()))
        for particle in final_data:
            pos_str = np.array2string(particle['position'], precision=3, floatmode='fixed', sign=' ')
            vel_str = np.array2string(particle['velocity'], precision=3, floatmode='fixed', sign=' ')
            print(f"  {particle['label']:<10}: Mass={particle['mass']:.2e}, Pos={pos_str}, Vel={vel_str}")
    else:
        print("\nAnalytic kick was not applied.")

    print(f"\nFinal simulation time: {simulation.get_simulation_time():.4f} years")
    print("\nNBodySimulation example finished.")