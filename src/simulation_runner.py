import numpy as np
import multiprocessing
# Keep relative imports for package use
from . import n_body_simulation
from . import analytic_impulse

def run_single_simulation(args):
    """
    Wrapper function to run a single N-body simulation using the NBodySimulation class.
    Handles unpacking arguments for multiprocessing.

    Args:
        args (tuple): A tuple containing simulation parameters:
            initial_positions (np.ndarray): Initial positions (N, 3) in AU.
                                           Assumes the first particle is the central body (e.g., Sun).
            initial_velocities_au_day (np.ndarray): Initial velocities (N, 3) in AU/day.
                                             These will be converted to REBOUND units.
            masses (np.ndarray): Masses of the bodies (N,) in Solar masses.
            t_start_years (float): Simulation start time in years.
            t_end_years (float): Simulation end time in years.
            dt_years (float): Time step in years (used for integrator if needed).
            integrator (str): Integrator type ('leapfrog', 'ias15', etc.).
            pbh_params (dict or None): Dictionary of PBH parameters
                                       (mass, velocity_au_day, impact_param, t_encounter_years)
                                       or None for baseline simulation.
                                       'velocity_au_day' is in AU/day.
                                       't_encounter_years' is the absolute time of encounter in years.

    Returns:
        tuple: (times, positions, velocities) from the simulation.
               Times are in years. Positions in AU. Velocities in AU/day.
               Returns (None, None, None) if simulation fails.
    """
    initial_positions, initial_velocities_au_day, masses, t_start_years, t_end_years, dt_years, integrator, pbh_params = args

    # Convert units for REBOUND
    # Time step: years -> years / (2*pi)
    dt_rebound = dt_years * 2 * np.pi if dt_years else None
    # Velocities: AU/day -> AU / (years / 2*pi)
    initial_velocities_rebound = initial_velocities_au_day * n_body_simulation.VELOCITY_DAY_TO_REBOUND

    try:
        sim_instance = n_body_simulation.NBodySimulation(integrator=integrator, time_step=dt_rebound)

        # Add particles (assuming first particle is central body, others are planets/objects)
        # REBOUND adds the Sun by default if using add_solar_system, but here we add manually
        # based on input arrays. We need labels.
        labels = [f"body_{i}" for i in range(len(masses))]
        if len(masses) > 0:
            labels[0] = "Sun" # Assume first is Sun
        # TODO: Improve labeling mechanism if needed

        for i in range(len(masses)):
            sim_instance.add_pbh( # Using add_pbh as a generic particle adder
                mass=masses[i],
                position=initial_positions[i],
                velocity=initial_velocities_rebound[i],
                label=labels[i]
            )

        # Set initial simulation time
        sim_instance.sim.t = t_start_years * 2 * np.pi

        # --- Data Storage Setup ---
        n_steps = int(np.ceil((t_end_years - t_start_years) / dt_years)) if dt_years else 100 # Estimate steps
        times_out = np.zeros(n_steps + 1)
        positions_out = np.zeros((n_steps + 1, len(masses), 3))
        velocities_out = np.zeros((n_steps + 1, len(masses), 3)) # Store in AU/day

        times_out[0] = sim_instance.get_simulation_time()
        initial_state = sim_instance.get_particle_data()
        for i, p_data in enumerate(initial_state):
             positions_out[0, i, :] = p_data['position']
             # Convert velocity back to AU/day for output consistency
             velocities_out[0, i, :] = p_data['velocity'] / n_body_simulation.VELOCITY_DAY_TO_REBOUND
        # --- End Data Storage Setup ---

        kick_applied_successfully = False
        time_of_kick_application_years = -1.0

        if pbh_params:
            print(f"Running perturbed simulation (PBH params: {pbh_params})...")
            # Add the PBH particle itself
            pbh_mass = pbh_params['mass_msun']
            # PBH velocity needs conversion AU/day -> AU/(yr/2pi)
            pbh_velocity_rebound = pbh_params['velocity_au_day'] * n_body_simulation.VELOCITY_DAY_TO_REBOUND
            # PBH position needs to be calculated based on encounter params (impact param, t_encounter)
            # This requires a more complex setup - assuming position is given directly for now
            # Placeholder: Use a dummy position far away initially
            # TODO: Calculate initial PBH position based on encounter parameters relative to target
            pbh_initial_position_au = np.array([-1000.0, pbh_params.get('impact_param_au', 100.0), 0.0]) # Needs proper calculation!
            pbh_label = "PBH_Perturber"

            sim_instance.add_pbh(
                mass=pbh_mass,
                position=pbh_initial_position_au, # Placeholder position
                velocity=pbh_velocity_rebound,
                label=pbh_label
            )
            print(f"Added PBH '{pbh_label}' to simulation.")

            # Identify target body (e.g., Earth) - How is this specified? Assume 'Earth' for now.
            # TODO: Pass target body label as an argument
            target_body_label = "body_3" # Assuming Earth is body 3 after Sun, Merc, Venus

            # Calculate and apply the kick
            # The analytic kick function needs the state *before* the encounter
            # We assume the provided initial conditions are suitable for this calculation.
            # The kick function itself integrates to t_ca and applies the kick.
            print(f"Attempting to apply analytic kick from {pbh_label} to {target_body_label}...")
            kick_applied_successfully = sim_instance.apply_analytic_kick(
                pbh_label=pbh_label,
                target_body_label=target_body_label
                # Note: apply_analytic_kick uses the *current* state in sim_instance
                # and integrates to t_ca internally before applying.
            )
            if kick_applied_successfully:
                 time_of_kick_application_years = sim_instance.get_simulation_time()
                 print(f"Kick applied at t = {time_of_kick_application_years:.4f} years.")
            else:
                 print("Analytic kick application failed or was zero.")
                 # Decide how to proceed - continue simulation without kick?

            # Need to re-capture state arrays as PBH was added
            num_particles_total = len(masses) + 1
            positions_out = np.zeros((n_steps + 1, num_particles_total, 3))
            velocities_out = np.zeros((n_steps + 1, num_particles_total, 3)) # Store in AU/day

            current_state = sim_instance.get_particle_data()
            times_out[0] = sim_instance.get_simulation_time() # Time might have advanced to t_ca
            for i, p_data in enumerate(current_state):
                 positions_out[0, i, :] = p_data['position']
                 velocities_out[0, i, :] = p_data['velocity'] / n_body_simulation.VELOCITY_DAY_TO_REBOUND

        else:
            print("Running baseline simulation...")
            num_particles_total = len(masses)

        # --- Main Integration Loop ---
        current_step = 0
        target_rebound_time = t_end_years * 2 * np.pi

        while sim_instance.sim.t < target_rebound_time and current_step < n_steps:
            next_time_rebound = min(sim_instance.sim.t + dt_rebound, target_rebound_time)
            sim_instance.integrate_to_time(next_time_rebound / (2 * np.pi)) # Integrate using years
            current_step += 1

            times_out[current_step] = sim_instance.get_simulation_time()
            current_state = sim_instance.get_particle_data()
            # Ensure state arrays match particle count (important if PBH was added)
            if len(current_state) != positions_out.shape[1]:
                 print(f"Warning: Particle count mismatch ({len(current_state)} vs {positions_out.shape[1]}) at step {current_step}. Resizing arrays.")
                 # Resize arrays - this is inefficient, better to size correctly initially
                 old_pos = positions_out
                 old_vel = velocities_out
                 positions_out = np.zeros((n_steps + 1, len(current_state), 3))
                 velocities_out = np.zeros((n_steps + 1, len(current_state), 3))
                 min_steps = min(old_pos.shape[0], positions_out.shape[0])
                 min_parts = min(old_pos.shape[1], positions_out.shape[1])
                 positions_out[:min_steps, :min_parts, :] = old_pos[:min_steps, :min_parts, :]
                 velocities_out[:min_steps, :min_parts, :] = old_vel[:min_steps, :min_parts, :]


            for i, p_data in enumerate(current_state):
                 if i < positions_out.shape[1]: # Check bounds after potential resize
                     positions_out[current_step, i, :] = p_data['position']
                     velocities_out[current_step, i, :] = p_data['velocity'] / n_body_simulation.VELOCITY_DAY_TO_REBOUND
                 else:
                      print(f"Warning: Index {i} out of bounds for state arrays after potential resize.")


        # Trim arrays to actual steps taken
        times_out = times_out[:current_step + 1]
        positions_out = positions_out[:current_step + 1, :, :]
        velocities_out = velocities_out[:current_step + 1, :, :]

        print(f"Simulation loop finished at t = {sim_instance.get_simulation_time():.4f} years.")
        return times_out, positions_out, velocities_out

    except Exception as e:
        print(f"Error during simulation run: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def run_parallel_simulations(initial_positions, initial_velocities_au_day, masses,
                             t_start_years, t_end_years, dt_years, integrator='leapfrog',
                             pbh_params=None):
    """
    Runs baseline and PBH-perturbed simulations in parallel.

    Args:
        initial_positions (np.ndarray): Initial positions (N, 3) in AU.
        initial_velocities_au_day (np.ndarray): Initial velocities (N, 3) in AU/day.
        masses (np.ndarray): Masses of the bodies (N,) in Solar masses.
        t_start_years (float): Simulation start time in years.
        t_end_years (float): Simulation end time in years.
        dt_years (float): Time step in years.
        integrator (str): Integrator type. Defaults to 'leapfrog'.
        pbh_params (dict or None): Dictionary of PBH parameters for the
                                   perturbed run. If None, only baseline runs.
                                   Expected keys: 'mass', 'velocity_au_day',
                                   'impact_param', 't_encounter_years'.

    Returns:
        tuple: Contains results for baseline and perturbed simulations:
               (baseline_results, perturbed_results)
               Each result is a tuple: (times, positions, velocities)
               Times in years, positions in AU, velocities in AU/day.
               If a simulation fails, its result will be (None, None, None).
               If pbh_params is None, perturbed_results will be (None, None, None).
    """
    if pbh_params is None:
        print("No PBH parameters provided. Running only baseline simulation.")
        baseline_args = (initial_positions, initial_velocities_au_day, masses, t_start_years, t_end_years, dt_years, integrator, None)
        baseline_results = run_single_simulation(baseline_args)
        return baseline_results, (None, None, None) # Return placeholder for perturbed

    # Ensure data is copied for parallel runs
    baseline_args = (initial_positions.copy(), initial_velocities_au_day.copy(), masses.copy(), t_start_years, t_end_years, dt_years, integrator, None)
    perturbed_args = (initial_positions.copy(), initial_velocities_au_day.copy(), masses.copy(), t_start_years, t_end_years, dt_years, integrator, pbh_params.copy())

    pool_args = [baseline_args, perturbed_args]

    print(f"Starting parallel simulations with {multiprocessing.cpu_count()} cores...")
    # Use context manager for the pool
    with multiprocessing.Pool(processes=min(2, multiprocessing.cpu_count())) as pool:
        results = pool.map(run_single_simulation, pool_args)

    baseline_results = results[0] if results and len(results) > 0 else (None, None, None)
    perturbed_results = results[1] if results and len(results) > 1 else (None, None, None)

    print("Parallel simulations completed.")
    return baseline_results, perturbed_results

if __name__ == '__main__':
    # Example Usage - Use absolute imports here to avoid 'no parent module' error
    print("Simulation Runner Module - Example Run")
    try:
        # Need to import directly for this block
        import n_body_simulation as nbs
        import analytic_impulse as ai # Not strictly needed for runner, but good practice
    except ImportError:
        print("Error: Could not import simulation modules directly.")
        print("Please run this script using 'python -m src.simulation_runner' from the project root directory.")
        exit()


    # --- Dummy Example Setup ---
    N_BODIES = 3 # Sun, Body1, Body2
    DIM = 3
    # Simple circular orbits for testing
    masses_example = np.array([1.0, 1e-6, 1e-5]) # M_sun
    positions_example = np.array([[0,0,0], [1,0,0], [0,5,0]]) # AU
    # Calculate velocities for circular orbits v = sqrt(GM/r)
    G_sim = 4 * np.pi**2 # AU^3 / (M_sun * (yr/2pi)^2)
    v1 = np.sqrt(G_sim * masses_example[0] / 1.0) # AU / (yr/2pi)
    v2 = np.sqrt(G_sim * masses_example[0] / 5.0) # AU / (yr/2pi)
    velocities_rebound_example = np.array([[0,0,0], [0, v1, 0], [-v2, 0, 0]]) # AU / (yr/2pi)
    # Convert velocities to AU/day for the runner function input
    velocities_au_day_example = velocities_rebound_example / nbs.VELOCITY_DAY_TO_REBOUND

    T_START_YEARS = 0.0
    T_END_YEARS = 0.1  # Short duration for example
    DT_YEARS = 0.001 # ~ 8 hours

    # Example PBH parameters
    dummy_pbh_params = {
        'mass': 1e-9, # M_sun
        'velocity_au_day': np.array([20, 0, 0]), # AU/day - High velocity encounter
        'impact_param': 0.5, # AU - Closest approach distance if undeflected
        't_encounter_years': 0.05 # Encounter time within the simulation duration
        # Note: Initial PBH position calculation based on these is complex and omitted here.
        # The current code uses a placeholder position and applies kick based on initial state.
    }
    # --- End Dummy Example Setup ---

    print("\nRunning example parallel simulation...")
    try:
        baseline_res, perturbed_res = run_parallel_simulations(
            positions_example, velocities_au_day_example, masses_example,
            T_START_YEARS, T_END_YEARS, DT_YEARS, integrator='ias15', # Use adaptive integrator
            pbh_params=dummy_pbh_params
        )

        # Check results (ensure they are not None before accessing shapes)
        print("\n--- Results ---")
        if baseline_res and baseline_res[0] is not None:
            print(f"Baseline simulation completed. Result shapes:")
            print(f"  Times (yrs): {baseline_res[0].shape}")
            print(f"  Positions (AU): {baseline_res[1].shape}")
            print(f"  Velocities (AU/day): {baseline_res[2].shape}")
            # print(f"  Final Sun Pos: {baseline_res[1][-1, 0, :]}")
            # print(f"  Final Body1 Pos: {baseline_res[1][-1, 1, :]}")
        else:
            print("Baseline simulation failed or returned None.")

        if perturbed_res and perturbed_res[0] is not None:
            print(f"\nPerturbed simulation completed. Result shapes:")
            print(f"  Times (yrs): {perturbed_res[0].shape}")
            print(f"  Positions (AU): {perturbed_res[1].shape}") # Should have N+1 particles
            print(f"  Velocities (AU/day): {perturbed_res[2].shape}")
            # print(f"  Final Sun Pos: {perturbed_res[1][-1, 0, :]}")
            # print(f"  Final Body1 Pos: {perturbed_res[1][-1, 1, :]}")
            # print(f"  Final PBH Pos: {perturbed_res[1][-1, -1, :]}")
        else:
            print("Perturbed simulation failed or returned None.")

    except Exception as e:
        print(f"\nAn unexpected error occurred during the example run: {e}")
        import traceback
        traceback.print_exc()