import ast
import numpy as np
import os

# Define constants for file formats
FORMAT_NPZ = 'npz'
FORMAT_CSV = 'csv' # Placeholder for future implementation

def compute_residuals(baseline_results, perturbed_results, particle_indices=None):
    """
    Computes the residuals (differences) between baseline and perturbed simulations.

    Args:
        baseline_results (tuple): (times, positions, velocities) from the baseline run.
                                  Positions (n_steps, n_particles_base, 3) AU
                                  Velocities (n_steps, n_particles_base, 3) AU/day
                                  Times (n_steps,) years
        perturbed_results (tuple): (times, positions, velocities) from the perturbed run.
                                   Positions (n_steps_pert, n_particles_pert, 3) AU
                                   Velocities (n_steps_pert, n_particles_pert, 3) AU/day
                                   Times (n_steps_pert,) years
        particle_indices (list or None): Optional list of integer indices of the particles
                                         in the baseline simulation to compute residuals for.
                                         If None, computes residuals for all particles present
                                         in *both* simulations (up to min number of particles).

    Returns:
        tuple: (residual_times, position_residuals, velocity_residuals)
               Residuals are calculated as perturbed - baseline.
               Returns (None, None, None) if inputs are invalid or incompatible.
               position_residuals shape: (n_steps_interp, n_particles_common, 3)
               velocity_residuals shape: (n_steps_interp, n_particles_common, 3)
               residual_times shape: (n_steps_interp,)
    """
    if not baseline_results or not perturbed_results:
        print("Error: Baseline or perturbed results are missing.")
        return None, None, None

    base_times, base_pos, base_vel = baseline_results
    pert_times, pert_pos, pert_vel = perturbed_results

    if base_times is None or pert_times is None:
        print("Error: Simulation times are missing from results.")
        return None, None, None
    if base_pos is None or pert_pos is None or base_vel is None or pert_vel is None:
        print("Error: Simulation state data (positions/velocities) is missing.")
        return None, None, None

    # --- Determine common particles ---
    n_particles_base = base_pos.shape[1]
    n_particles_pert = pert_pos.shape[1]

    if particle_indices is None:
        # Default: Use all particles common to both simulations
        n_common = min(n_particles_base, n_particles_pert)
        if n_common == 0:
             print("Error: No particles found in simulation results.")
             return None, None, None
        common_indices_base = list(range(n_common))
        common_indices_pert = list(range(n_common))
        print(f"Computing residuals for the first {n_common} common particles.")
        if n_particles_pert > n_particles_base:
             print(f"Warning: Perturbed simulation has {n_particles_pert - n_particles_base} extra particle(s) (e.g., PBH) which are ignored in residuals.")
    else:
        # Use specified indices
        common_indices_base = [idx for idx in particle_indices if idx < n_particles_base]
        common_indices_pert = [idx for idx in particle_indices if idx < n_particles_pert]
        # Ensure we only compare particles present in both using the provided indices
        valid_indices = sorted(list(set(common_indices_base) & set(common_indices_pert)))
        if not valid_indices:
             print(f"Error: Specified particle indices {particle_indices} not found in both simulations or result in no common particles.")
             return None, None, None
        common_indices_base = valid_indices
        common_indices_pert = valid_indices
        n_common = len(valid_indices)
        print(f"Computing residuals for specified particle indices: {valid_indices}")


    # --- Time Interpolation ---
    # Interpolate the perturbed data onto the baseline time steps for direct comparison
    # (Could also interpolate baseline onto perturbed, or both onto a common grid)
    residual_times = base_times
    n_steps_interp = len(residual_times)
    print(f"Interpolating perturbed data ({len(pert_times)} steps) onto baseline time grid ({n_steps_interp} steps)...")

    # Check if time arrays are identical (avoids unnecessary interpolation)
    if len(base_times) == len(pert_times) and np.allclose(base_times, pert_times):
        print("Time arrays are identical. No interpolation needed.")
        pert_pos_interp = pert_pos[:, common_indices_pert, :]
        pert_vel_interp = pert_vel[:, common_indices_pert, :]
    else:
        # Interpolate positions and velocities for common particles
        pert_pos_interp = np.zeros((n_steps_interp, n_common, 3))
        pert_vel_interp = np.zeros((n_steps_interp, n_common, 3))

        for i, particle_idx in enumerate(common_indices_pert):
            for dim in range(3):
                # Use np.interp: requires 1D arrays
                pert_pos_interp[:, i, dim] = np.interp(residual_times, pert_times, pert_pos[:, particle_idx, dim])
                pert_vel_interp[:, i, dim] = np.interp(residual_times, pert_times, pert_vel[:, particle_idx, dim])

    # --- Calculate Residuals ---
    # Select corresponding particles from baseline
    base_pos_common = base_pos[:, common_indices_base, :]
    base_vel_common = base_vel[:, common_indices_base, :]

    # Residual = Perturbed - Baseline
    position_residuals = pert_pos_interp - base_pos_common
    velocity_residuals = pert_vel_interp - base_vel_common

    print("Residual computation complete.")
    return residual_times, position_residuals, velocity_residuals


def save_residuals(filepath, times, pos_residuals, vel_residuals, metadata=None, format=FORMAT_NPZ):
    """
    Saves residual data to a file.

    Args:
        filepath (str): The path to save the file to.
        times (np.ndarray): Array of time steps (years).
        pos_residuals (np.ndarray): Position residuals (perturbed - baseline) in AU.
                                    Shape: (n_steps, n_particles, 3)
        vel_residuals (np.ndarray): Velocity residuals (perturbed - baseline) in AU/day.
                                    Shape: (n_steps, n_particles, 3)
        metadata (dict, optional): Additional metadata to save (e.g., simulation params).
                                   Only supported for NPZ format currently.
        format (str): The format to save in ('npz' or 'csv'). Defaults to 'npz'.

    Returns:
        bool: True if saving was successful, False otherwise.
    """
    print(f"Attempting to save residuals to '{filepath}' in format '{format}'...")
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    try:
        if format.lower() == FORMAT_NPZ:
            save_dict = {
                'times_years': times,
                'position_residuals_au': pos_residuals,
                'velocity_residuals_au_day': vel_residuals
            }
            if metadata:
                # Convert metadata values to string to ensure compatibility with npz
                # (np.savez doesn't handle arbitrary objects well)
                meta_str_dict = {k: str(v) for k, v in metadata.items()}
                save_dict['metadata'] = np.array([str(meta_str_dict)]) # Store dict as string in array

            np.savez_compressed(filepath, **save_dict)
            print(f"Residuals successfully saved to {filepath}")
            return True

        elif format.lower() == FORMAT_CSV:
            # CSV saving is more complex for multi-dimensional arrays.
            # Requires flattening or multiple files, or using pandas.
            # Placeholder for future implementation.
            print(f"Warning: CSV saving is not yet implemented. Use '{FORMAT_NPZ}'.")
            # Example using pandas (requires pandas dependency):
            # import pandas as pd
            # n_steps, n_particles, _ = pos_residuals.shape
            # # Create multi-index columns
            # cols_pos = pd.MultiIndex.from_product([range(n_particles), ['pos_x', 'pos_y', 'pos_z']], names=['particle', 'coord'])
            # cols_vel = pd.MultiIndex.from_product([range(n_particles), ['vel_x', 'vel_y', 'vel_z']], names=['particle', 'coord'])
            # # Flatten data
            # pos_flat = pos_residuals.reshape(n_steps, -1)
            # vel_flat = vel_residuals.reshape(n_steps, -1)
            # # Create DataFrames
            # df_pos = pd.DataFrame(pos_flat, index=times, columns=cols_pos)
            # df_vel = pd.DataFrame(vel_flat, index=times, columns=cols_vel)
            # # Combine or save separately
            # df_combined = pd.concat([df_pos, df_vel], axis=1)
            # df_combined.index.name = 'time_years'
            # df_combined.to_csv(filepath)
            # print(f"Residuals (potentially flattened) saved to {filepath}")
            # return True
            return False
        else:
            print(f"Error: Unsupported save format '{format}'. Use '{FORMAT_NPZ}'.")
            return False
    except Exception as e:
        print(f"Error saving residuals to '{filepath}': {e}")
        return False


def load_residuals(filepath):
    """
    Loads residual data from a file (currently only NPZ format).

    Args:
        filepath (str): The path to the file to load.

    Returns:
        tuple: (times, pos_residuals, vel_residuals, metadata)
               Returns (None, None, None, None) if loading fails or file not found.
               Metadata will be None if not present in the file or if format is not NPZ.
    """
    print(f"Attempting to load residuals from '{filepath}'...")
    if not os.path.exists(filepath):
        print(f"Error: File not found at '{filepath}'")
        return None, None, None, None

    try:
        # Assuming NPZ format for now
        if filepath.lower().endswith('.npz'):
            # allow_pickle=False: refuse arbitrary object deserialization. A crafted .npz
            # can embed a pickle payload that executes code on load; the residual arrays and
            # the metadata string below do not need pickle, so disabling it is safe here.
            data = np.load(filepath, allow_pickle=False)
            times = data.get('times_years')
            pos_residuals = data.get('position_residuals_au')
            vel_residuals = data.get('velocity_residuals_au_day')
            metadata = None
            if 'metadata' in data:
                 try:
                     # Attempt to parse the metadata string back into a dict
                     metadata_str = str(data['metadata'].item()) # Extract string from array
                     # ast.literal_eval parses Python literals only (dict/list/str/num/etc.)
                     # and never executes code, unlike eval(). A malicious metadata string
                     # therefore cannot run arbitrary code; non-literal input raises and is
                     # caught below, degrading to the raw string.
                     metadata = ast.literal_eval(metadata_str)
                 except Exception as meta_e:
                     print(f"Warning: Could not parse metadata from file: {meta_e}")
                     metadata = {'raw_metadata': str(data['metadata'])} # Store raw string

            if times is None or pos_residuals is None or vel_residuals is None:
                 raise ValueError("File is missing required data arrays (times, positions, or velocities).")

            print(f"Residuals successfully loaded from {filepath}")
            return times, pos_residuals, vel_residuals, metadata
        else:
            print(f"Error: Unsupported file format. Only '.npz' is currently supported for loading.")
            return None, None, None, None
    except Exception as e:
        print(f"Error loading residuals from '{filepath}': {e}")
        return None, None, None, None


# --- TODO: Implement Observable Calculation & Figure of Merit ---
# def calculate_observables(positions, velocities):
#     """ Calculates sky position, distance, etc. Requires observer position. """
#     pass

# def calculate_q_fom(residuals_observables):
#     """ Calculates the figure-of-merit based on observable residuals. Needs definition. """
#     pass


# --- New Functions to be added before line 250 ---

def calculate_rms(data_residuals):
    """
    Calculates the Root Mean Square (RMS) of residuals over time for each particle and dimension.

    Args:
        data_residuals (np.ndarray): Residual array (e.g., position or velocity).
                                     Shape: (n_steps, n_particles, 3)

    Returns:
        np.ndarray: RMS values for each particle and dimension.
                    Shape: (n_particles, 3)
                    Returns None if input is invalid.
    """
    if data_residuals is None or data_residuals.ndim != 3:
        print("Error: Invalid input for RMS calculation.")
        return None
    if data_residuals.shape[0] == 0: # No time steps
        print("Warning: Residual array has zero time steps. RMS is undefined.")
        # Return zeros of appropriate shape? Or None? Returning None for now.
        return None
        # return np.zeros_like(data_residuals[0, :, :]) # Alternative: return zeros

    # RMS = sqrt(mean(squares))
    rms = np.sqrt(np.mean(np.square(data_residuals), axis=0))
    return rms

def calculate_peak(data_residuals):
    """
    Calculates the peak absolute residual value over time for each particle and dimension.

    Args:
        data_residuals (np.ndarray): Residual array (e.g., position or velocity).
                                     Shape: (n_steps, n_particles, 3)

    Returns:
        np.ndarray: Peak absolute values for each particle and dimension.
                    Shape: (n_particles, 3)
                    Returns None if input is invalid.
    """
    if data_residuals is None or data_residuals.ndim != 3:
        print("Error: Invalid input for peak calculation.")
        return None
    if data_residuals.shape[0] == 0: # No time steps
         print("Warning: Residual array has zero time steps. Peak is undefined.")
         return None
         # return np.zeros_like(data_residuals[0, :, :]) # Alternative: return zeros

    # Peak = max(abs(value))
    peak = np.max(np.abs(data_residuals), axis=0)
    return peak

def calculate_residual_stats(pos_residuals, vel_residuals):
    """
    Calculates basic statistics (RMS, Peak) for position and velocity residuals.

    Args:
        pos_residuals (np.ndarray): Position residuals (perturbed - baseline) in AU.
                                    Shape: (n_steps, n_particles, 3)
        vel_residuals (np.ndarray): Velocity residuals (perturbed - baseline) in AU/day.
                                    Shape: (n_steps, n_particles, 3)

    Returns:
        dict: A dictionary containing the statistics, e.g.,
              {
                  'pos_rms_au': np.ndarray,
                  'pos_peak_au': np.ndarray,
                  'vel_rms_au_day': np.ndarray,
                  'vel_peak_au_day': np.ndarray
              }
              Returns an empty dict if inputs are invalid.
    """
    stats = {}
    if pos_residuals is not None:
        stats['pos_rms_au'] = calculate_rms(pos_residuals)
        stats['pos_peak_au'] = calculate_peak(pos_residuals)
    else:
        print("Warning: Position residuals are None. Cannot calculate position stats.")

    if vel_residuals is not None:
        stats['vel_rms_au_day'] = calculate_rms(vel_residuals)
        stats['vel_peak_au_day'] = calculate_peak(vel_residuals)
    else:
        print("Warning: Velocity residuals are None. Cannot calculate velocity stats.")

    # Filter out None values if calculations failed
    stats = {k: v for k, v in stats.items() if v is not None}
    return stats


if __name__ == '__main__':
    print("Residual Analysis Module - Example Usage")

    # --- Create Dummy Simulation Results ---
    n_steps = 100
    n_particles_base = 3 # e.g., Sun, Earth, Jupiter
    n_particles_pert = 4 # e.g., Sun, Earth, Jupiter, PBH
    dt = 0.1 # years

    # Baseline
    base_times_eg = np.arange(n_steps) * dt
    base_pos_eg = np.random.rand(n_steps, n_particles_base, 3) * 10 # AU
    base_vel_eg = np.random.rand(n_steps, n_particles_base, 3) * 1 # AU/day

    # Perturbed (slightly different + extra particle)
    pert_times_eg = np.arange(n_steps + 5) * dt * 0.99 # Slightly different time steps
    pert_pos_eg = np.random.rand(n_steps + 5, n_particles_pert, 3) * 10.1
    pert_vel_eg = np.random.rand(n_steps + 5, n_particles_pert, 3) * 1.01
    # Add a small systematic offset to first few particles for effect
    pert_pos_eg[:, :n_particles_base, :] += 0.01
    pert_vel_eg[:, :n_particles_base, :] -= 0.001

    baseline_results_eg = (base_times_eg, base_pos_eg, base_vel_eg)
    perturbed_results_eg = (pert_times_eg, pert_pos_eg, pert_vel_eg)
    # --- End Dummy Data ---

    print("\n1. Computing Residuals (Default - Common Particles)...")
    res_t, res_p, res_v = compute_residuals(baseline_results_eg, perturbed_results_eg)

    if res_t is not None and res_p is not None and res_v is not None: # Check all results
        print(f"  Residual times shape: {res_t.shape}")
        print(f"  Position residuals shape: {res_p.shape}") # Should be (n_steps_base, n_particles_base, 3)
        print(f"  Velocity residuals shape: {res_v.shape}") # Should be (n_steps_base, n_particles_base, 3)

        # --- Save Residuals ---
        print("\n2. Saving Residuals to NPZ...")
        save_path = "examples/residuals_example.npz"
        dummy_meta = {'baseline_run': 'run_001', 'perturbed_run': 'run_002_pbh', 'pbh_mass': 1e-9}
        # Pass the checked non-None arrays
        success = save_residuals(save_path, res_t, res_p, res_v, metadata=dummy_meta, format=FORMAT_NPZ)

        if success:
            print("\n3. Loading Residuals from NPZ...")
            loaded_t, loaded_p, loaded_v, loaded_meta = load_residuals(save_path)
            # Check loaded arrays before use
            if loaded_t is not None and loaded_p is not None and loaded_v is not None:
                print(f"  Loaded times shape: {loaded_t.shape}")
                print(f"  Loaded pos_res shape: {loaded_p.shape}")
                print(f"  Loaded vel_res shape: {loaded_v.shape}")
                print(f"  Loaded metadata: {loaded_meta}")
                # Verify data integrity (optional) - now safe to use arrays
                assert np.allclose(res_t, loaded_t)
                assert np.allclose(res_p, loaded_p)
                assert np.allclose(res_v, loaded_v)
                print("  Data integrity check passed.")
            else:
                print("  Loading failed (returned None).")
        else:
            print("  Saving failed.")

    else:
        print("  Residual computation failed (returned None).")

        # --- Calculate Stats ---
        print("\nCalculating Residual Statistics...")
        residual_stats = calculate_residual_stats(res_p, res_v)
        if residual_stats:
            print("  Statistics calculated:")
            for key, value in residual_stats.items():
                 # Assuming value is a numpy array (n_particles, 3)
                 print(f"    {key}:")
                 # Print stats per particle
                 for particle_idx in range(value.shape[0]):
                     stat_str = np.array2string(value[particle_idx], precision=3, floatmode='fixed', sign=' ')
                     print(f"      Particle {particle_idx}: {stat_str}")
        else:
            print("  Failed to calculate statistics.")

    print("\n4. Computing Residuals (Specific Indices)...")
    # Example: Compute only for particle 1 (Earth?)
    res_t_spec, res_p_spec, res_v_spec = compute_residuals(
        baseline_results_eg,
        perturbed_results_eg,
        particle_indices=[1] # Compute only for the particle originally at index 1
    )
    # Check results before printing shapes
    if res_t_spec is not None and res_p_spec is not None and res_v_spec is not None:
         print(f"  Residual times shape: {res_t_spec.shape}")
         print(f"  Position residuals shape: {res_p_spec.shape}") # Should be (n_steps_base, 1, 3)
         print(f"  Velocity residuals shape: {res_v_spec.shape}") # Should be (n_steps_base, 1, 3)

         # --- Calculate Stats for specific particle ---
         print("  Calculating Residual Statistics (Specific Index)...")
         residual_stats_spec = calculate_residual_stats(res_p_spec, res_v_spec)
         if residual_stats_spec:
             print("  Statistics calculated:")
             for key, value in residual_stats_spec.items():
                  print(f"    {key}:")
                  for particle_idx in range(value.shape[0]): # Should only be 1 particle here
                      stat_str = np.array2string(value[particle_idx], precision=3, floatmode='fixed', sign=' ')
                      print(f"      Particle (original index 1): {stat_str}")
         else:
             print("  Failed to calculate statistics for specific index.")
    else:
         print("  Residual computation for specific indices failed (returned None).")


    print("\nResidual Analysis Module - Example Finished.")