import numpy as np
import os

# Import residual analysis module to potentially load data
try:
    from . import residual_analysis
except ImportError:
    # Allow running as script for testing
    import residual_analysis


def add_gaussian_noise(data, noise_std_dev):
    """
    Adds Gaussian noise to the input data.

    Args:
        data (np.ndarray): The input data array (e.g., residuals).
        noise_std_dev (float or np.ndarray): The standard deviation of the Gaussian noise.
                                             If float, the same noise level is applied to all points.
                                             If array, must be broadcastable to data.shape.

    Returns:
        np.ndarray: Data with added Gaussian noise. Returns None if inputs are invalid.
    """
    if data is None:
        print("Error: Input data is None.")
        return None
    if noise_std_dev is None or np.any(np.array(noise_std_dev) < 0):
         print("Error: noise_std_dev must be non-negative.")
         return None

    try:
        noise = np.random.normal(loc=0.0, scale=noise_std_dev, size=data.shape)
        return data + noise
    except Exception as e:
        print(f"Error adding Gaussian noise: {e}")
        return None


def generate_synthetic_residuals(ideal_residuals_path, noise_std_dev_pos, noise_std_dev_vel,
                                 output_path=None):
    """
    Loads ideal residuals, adds Gaussian noise, and saves the synthetic data.

    Args:
        ideal_residuals_path (str): Path to the .npz file containing ideal residuals
                                    (output from residual_analysis.save_residuals).
        noise_std_dev_pos (float): Standard deviation of noise to add to position residuals (AU).
        noise_std_dev_vel (float): Standard deviation of noise to add to velocity residuals (AU/day).
        output_path (str, optional): Path to save the synthetic residuals .npz file.
                                     If None, defaults to a path based on the input file name.

    Returns:
        tuple: (synthetic_times, synthetic_pos_res, synthetic_vel_res, metadata)
               Returns (None, None, None, None) if generation fails.
    """
    print(f"Generating synthetic residuals from: {ideal_residuals_path}")
    # Load ideal residuals
    times, pos_res, vel_res, metadata = residual_analysis.load_residuals(ideal_residuals_path)

    if times is None:
        print("Error: Failed to load ideal residuals.")
        return None, None, None, None

    print("Adding noise to position residuals...")
    synthetic_pos_res = add_gaussian_noise(pos_res, noise_std_dev_pos)
    if synthetic_pos_res is None:
        print("Error: Failed to add noise to position residuals.")
        return None, None, None, None

    print("Adding noise to velocity residuals...")
    synthetic_vel_res = add_gaussian_noise(vel_res, noise_std_dev_vel)
    if synthetic_vel_res is None:
        print("Error: Failed to add noise to velocity residuals.")
        return None, None, None, None

    print("Synthetic data generated.")

    # Update metadata
    if metadata is None:
        metadata = {}

    # Ensure metadata is a dictionary before adding keys
    if isinstance(metadata, dict):
        noise_added_dict = { # Create the dictionary first
            'pos_std_dev_au': noise_std_dev_pos,
            'vel_std_dev_au_day': noise_std_dev_vel,
            'noise_type': 'Gaussian'
        }
        # Store the dictionary as a string value, similar to how residual_analysis saves metadata
        metadata['noise_added'] = str(noise_added_dict)
        metadata['source_ideal_residuals'] = ideal_residuals_path # This is already a string
    else:
        print("Warning: Loaded metadata is not a dictionary. Cannot add noise info.")
        # Consider how to handle non-dict metadata if it occurs

    # Save synthetic data
    if output_path is None:
        base, ext = os.path.splitext(ideal_residuals_path)
        output_path = f"{base}_synthetic{ext}"

    save_success = residual_analysis.save_residuals(
        filepath=output_path,
        times=times,
        pos_residuals=synthetic_pos_res,
        vel_residuals=synthetic_vel_res,
        metadata=metadata,
        format=residual_analysis.FORMAT_NPZ
    )

    if not save_success:
        print(f"Warning: Failed to save synthetic residuals to {output_path}")
        # Still return the data even if saving failed
        return times, synthetic_pos_res, synthetic_vel_res, metadata

    print(f"Synthetic residuals saved to: {output_path}")
    return times, synthetic_pos_res, synthetic_vel_res, metadata


if __name__ == '__main__':
    print("Synthetic Data Generator Module - Example Usage")

    # --- Setup: Ensure dummy ideal residuals exist ---
    # (This part relies on residual_analysis.py example having run successfully)
    ideal_res_file = "examples/residuals_example.npz"
    if not os.path.exists(ideal_res_file):
        print(f"Error: Ideal residual file not found at '{ideal_res_file}'.")
        print("Please run residual_analysis.py first to generate the example file.")
    else:
        # --- Generate Synthetic Data ---
        pos_noise = 1e-6 # AU (e.g., ~150 km uncertainty)
        vel_noise = 1e-8 # AU/day (e.g., ~1.5 m/s uncertainty)
        print(f"\nGenerating synthetic data with Pos Noise={pos_noise:.1e} AU, Vel Noise={vel_noise:.1e} AU/day")

        synth_t, synth_p, synth_v, synth_meta = generate_synthetic_residuals(
            ideal_residuals_path=ideal_res_file,
            noise_std_dev_pos=pos_noise,
            noise_std_dev_vel=vel_noise,
            output_path="examples/residuals_synthetic_example.npz"
        )

        if synth_t is not None and synth_p is not None and synth_v is not None and synth_meta is not None: # Check all returned values
            print("\nSynthetic data generation successful.")
            # Safely access metadata items
            output_file_base = synth_meta.get('source_ideal_residuals', ideal_res_file)
            output_file_synth = output_file_base.replace('.npz', '_synthetic.npz') if isinstance(output_file_base, str) else "unknown_synthetic.npz"
            print(f"  Output file: {output_file_synth}")
            print(f"  Synthetic times shape: {synth_t.shape}")
            print(f"  Synthetic pos_res shape: {synth_p.shape}") # Safe due to check above
            print(f"  Synthetic vel_res shape: {synth_v.shape}") # Safe due to check above
            noise_info = synth_meta.get('noise_added', 'N/A') # Safe due to check above
            print(f"  Updated metadata includes: {noise_info}")

            # Optional: Plot comparison (requires visualization module)
            try:
                import visualization
                # Reload ideal data for comparison
                ideal_t, ideal_p, ideal_v, _ = residual_analysis.load_residuals(ideal_res_file)
                # Check if ideal data loaded correctly
                if ideal_t is not None and ideal_p is not None:
                     # Plot residuals for the first particle (index 0 in residual array)
                     visualization.plot_residual_timeseries(
                         ideal_t, ideal_p, particle_indices=[0], labels=["Ideal Particle 0"],
                         title="Ideal Pos Residuals (Particle 0)", save_path=None # Don't save this one
                     )
                     # Create a separate plot for synthetic
                     visualization.plot_residual_timeseries(
                         synth_t, synth_p, particle_indices=[0], labels=["Synthetic Particle 0"],
                         title="Synthetic Pos Residuals (Particle 0)", save_path="plots/synthetic_residuals_example.png"
                     )
                else:
                    print("\nSkipping comparison plot: Failed to reload ideal data.")

            except ImportError:
                print("\nSkipping comparison plot (requires visualization module).")
            except Exception as plot_e:
                print(f"\nError during plotting example: {plot_e}")

        else:
            print("\nSynthetic data generation failed.")

    print("\nSynthetic Data Generator Module - Example Finished.")