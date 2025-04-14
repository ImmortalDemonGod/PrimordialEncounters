import numpy as np
import multiprocessing
import os
import time
import json
from tqdm import tqdm # Optional: for progress bar

# Import project modules (use absolute imports for clarity in this context)
try:
    from . import parameter_sampler
    from . import simulation_runner
    from . import residual_analysis
    from . import n_body_simulation # For VELOCITY_DAY_TO_REBOUND if needed directly
except ImportError:
    # Allow running as script for testing
    import parameter_sampler
    import simulation_runner
    import residual_analysis
    import n_body_simulation

# --- Configuration ---
DEFAULT_OUTPUT_DIR = "results/ensemble_run_{timestamp}"
DEFAULT_CHECKPOINT_INTERVAL = 10 # Save progress every N members

def run_ensemble_member(args):
    """
    Worker function to run one member of the simulation ensemble.

    Args:
        args (tuple): Contains all necessary parameters for a single run:
            member_id (int): Unique identifier for this ensemble member.
            pbh_params (dict): Dictionary of PBH parameters for this run
                               (from parameter_sampler).
            initial_cond (dict): Dictionary containing initial conditions:
                                 'positions_au', 'velocities_au_day', 'masses_msun'.
            sim_settings (dict): Dictionary of simulation settings:
                                 't_start_years', 't_end_years', 'dt_years', 'integrator'.
            analysis_settings (dict): Settings for residual analysis:
                                      'particle_indices' (optional list).
            output_dir (str): Directory to save results for this member.

    Returns:
        dict: A summary dictionary containing results or status for this member.
              Includes 'member_id', 'pbh_params', 'status', 'output_path', 'stats' (optional).
    """
    member_id, pbh_params, initial_cond, sim_settings, analysis_settings, output_dir = args
    member_output_dir = os.path.join(output_dir, f"member_{member_id:06d}")
    os.makedirs(member_output_dir, exist_ok=True)
    output_path = os.path.join(member_output_dir, "residuals.npz")
    summary_path = os.path.join(member_output_dir, "summary.json")

    summary = {
        'member_id': member_id,
        'pbh_params': pbh_params,
        'status': 'failed',
        'output_path': None,
        'stats': None,
        'error_message': None
    }

    try:
        print(f"[Member {member_id}] Starting simulation...")
        # Run baseline and perturbed simulations
        baseline_res, perturbed_res = simulation_runner.run_parallel_simulations(
            initial_positions=initial_cond['positions_au'],
            initial_velocities_au_day=initial_cond['velocities_au_day'],
            masses=initial_cond['masses_msun'],
            t_start_years=sim_settings['t_start_years'],
            t_end_years=sim_settings['t_end_years'],
            dt_years=sim_settings['dt_years'],
            integrator=sim_settings.get('integrator', 'ias15'),
            pbh_params=pbh_params # Pass the sampled PBH params
        )

        if baseline_res is None or perturbed_res is None or baseline_res[0] is None or perturbed_res[0] is None:
            raise RuntimeError("Simulation runner failed to produce valid results.")

        print(f"[Member {member_id}] Computing residuals...")
        # Compute residuals
        res_times, res_pos, res_vel = residual_analysis.compute_residuals(
            baseline_results=baseline_res,
            perturbed_results=perturbed_res,
            particle_indices=analysis_settings.get('particle_indices')
        )

        if res_times is None:
            raise RuntimeError("Residual computation failed.")

        print(f"[Member {member_id}] Calculating statistics...")
        # Calculate basic statistics
        stats = residual_analysis.calculate_residual_stats(res_pos, res_vel)
        summary['stats'] = {k: v.tolist() for k, v in stats.items() if v is not None} # Convert numpy arrays for JSON

        print(f"[Member {member_id}] Saving results...")
        # Save residuals and metadata
        metadata = {
            'member_id': member_id,
            'pbh_params': pbh_params,
            'sim_settings': sim_settings,
            'analysis_settings': analysis_settings,
            'initial_conditions_shape': {
                'pos': initial_cond['positions_au'].shape,
                'vel': initial_cond['velocities_au_day'].shape,
                'mass': initial_cond['masses_msun'].shape
            }
        }
        save_success = residual_analysis.save_residuals(
            filepath=output_path,
            times=res_times,
            pos_residuals=res_pos,
            vel_residuals=res_vel,
            metadata=metadata,
            format=residual_analysis.FORMAT_NPZ
        )

        if not save_success:
            raise RuntimeError("Failed to save residual data.")

        summary['status'] = 'completed'
        summary['output_path'] = output_path
        print(f"[Member {member_id}] Completed successfully.")

    except Exception as e:
        error_msg = f"Error in member {member_id}: {e}"
        print(error_msg)
        summary['error_message'] = error_msg
        # Optionally save error details
        with open(os.path.join(member_output_dir, "error.log"), 'w') as f_err:
            f_err.write(error_msg)
            import traceback
            traceback.print_exc(file=f_err)

    # Save summary for this member
    try:
        with open(summary_path, 'w') as f_sum:
            json.dump(summary, f_sum, indent=4)
    except Exception as json_e:
        print(f"[Member {member_id}] Warning: Failed to save summary JSON: {json_e}")


    return summary


def run_ensemble(
    num_members,
    initial_cond,
    sim_settings,
    analysis_settings=None,
    sampling_config=None,
    output_dir=None,
    num_workers=None,
    checkpoint_interval=DEFAULT_CHECKPOINT_INTERVAL
    ):
    """
    Runs a parallel ensemble of N-body simulations.

    Args:
        num_members (int): Number of ensemble members to run.
        initial_cond (dict): Dictionary containing fixed initial conditions for all runs:
                             'positions_au', 'velocities_au_day', 'masses_msun'.
        sim_settings (dict): Dictionary of fixed simulation settings for all runs:
                             't_start_years', 't_end_years', 'dt_years', 'integrator'.
        analysis_settings (dict, optional): Settings for residual analysis. Defaults to {}.
        sampling_config (dict, optional): Configuration for parameter sampling, passed to
                                          generate_pbh_sample sub-functions. Defaults to {}.
        output_dir (str, optional): Base directory to save results. If None, a timestamped
                                    directory is created.
        num_workers (int, optional): Number of parallel processes. Defaults to cpu_count().
        checkpoint_interval (int): Save aggregated results every N members.

    Returns:
        list: A list of summary dictionaries, one for each completed member.
    """
    analysis_settings = analysis_settings or {}
    sampling_config = sampling_config or {}

    if output_dir is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_dir = DEFAULT_OUTPUT_DIR.format(timestamp=timestamp)
    os.makedirs(output_dir, exist_ok=True)
    print(f"Ensemble output directory: {output_dir}")

    # Save run configuration
    run_config = {
        'num_members': num_members,
        'initial_cond_shapes': {k: v.shape for k, v in initial_cond.items()},
        'sim_settings': sim_settings,
        'analysis_settings': analysis_settings,
        'sampling_config': sampling_config,
        'output_dir': output_dir,
        'num_workers': num_workers or multiprocessing.cpu_count(),
        'checkpoint_interval': checkpoint_interval
    }
    config_path = os.path.join(output_dir, "ensemble_config.json")
    try:
        with open(config_path, 'w') as f_cfg:
            # Convert numpy arrays in initial_cond to lists for JSON serialization if necessary
            # For now, just saving shapes. Full ICs might be too large for config.
            json.dump(run_config, f_cfg, indent=4)
        print(f"Saved ensemble configuration to {config_path}")
    except Exception as cfg_e:
        print(f"Warning: Failed to save ensemble configuration: {cfg_e}")


    print(f"\nGenerating {num_members} PBH parameter samples...")
    pbh_samples = parameter_sampler.generate_pbh_sample(
        n_samples=num_members,
        mass_params=sampling_config.get('mass_params'),
        b_params=sampling_config.get('b_params'),
        vel_params=sampling_config.get('vel_params'),
        time_params=sampling_config.get('time_params')
    )
    print("Parameter generation complete.")

    # Prepare arguments for each worker
    all_args = []
    for i in range(num_members):
        member_args = (
            i, # member_id
            pbh_samples[i],
            initial_cond,
            sim_settings,
            analysis_settings,
            output_dir
        )
        all_args.append(member_args)

    # Determine number of workers
    if num_workers is None:
        num_workers = multiprocessing.cpu_count()
    print(f"\nStarting ensemble run with {num_workers} parallel workers...")

    results = []
    checkpoint_path = os.path.join(output_dir, "ensemble_results_checkpoint.json")

    # Use multiprocessing Pool with tqdm for progress bar
    try:
        with multiprocessing.Pool(processes=num_workers) as pool:
            # Use imap_unordered for potentially better performance and progress updates
            # Wrap with tqdm for progress bar
            for i, result in enumerate(tqdm(pool.imap_unordered(run_ensemble_member, all_args), total=num_members, desc="Ensemble Progress")):
                results.append(result)

                # Checkpointing
                if (i + 1) % checkpoint_interval == 0:
                    print(f"\nCheckpointing results ({len(results)}/{num_members})...")
                    try:
                        with open(checkpoint_path, 'w') as f_chk:
                            json.dump(results, f_chk, indent=4)
                        print(f"Checkpoint saved to {checkpoint_path}")
                    except Exception as chk_e:
                        print(f"Warning: Failed to save checkpoint: {chk_e}")

    except KeyboardInterrupt:
        print("\nEnsemble run interrupted by user.")
    except Exception as pool_e:
        print(f"\nError during parallel execution: {pool_e}")
    finally:
        # Save final results
        final_results_path = os.path.join(output_dir, "ensemble_results_final.json")
        print(f"\nSaving final aggregated results ({len(results)} members completed)...")
        try:
            with open(final_results_path, 'w') as f_final:
                json.dump(results, f_final, indent=4)
            print(f"Final results saved to {final_results_path}")
            # Optionally remove checkpoint file after successful final save
            if os.path.exists(checkpoint_path):
                 try:
                     os.remove(checkpoint_path)
                     print("Removed checkpoint file.")
                 except OSError as rm_e:
                     print(f"Warning: Could not remove checkpoint file: {rm_e}")
        except Exception as final_e:
            print(f"Error saving final results: {final_e}. Checkpoint file (if exists) contains intermediate results.")


    print(f"\nEnsemble run finished. {len(results)} members processed.")


# --- New Functions (Detection Analysis) --- To be added before line 300 ---

def is_detected(member_summary, threshold_au, target_particle_idx=0):
    """
    Determines if an encounter is 'detected' based on a simple threshold criterion.

    Args:
        member_summary (dict): The summary dictionary for a single ensemble member.
                               Must contain 'status' and 'stats' (with 'pos_peak_au').
        threshold_au (float): The detection threshold for the peak position residual (in AU).
        target_particle_idx (int): The index of the target particle within the
                                   *analyzed* particles (as defined by
                                   analysis_settings['particle_indices']). Defaults to 0.

    Returns:
        bool or None: True if detected, False if not detected, None if status is not
                      'completed' or stats are missing/invalid.
    """
    if member_summary.get('status') != 'completed':
        return None

    stats = member_summary.get('stats')
    if not stats or 'pos_peak_au' not in stats:
        return None # Cannot determine detection without peak position stats

    pos_peak_au = np.array(stats['pos_peak_au']) # Convert list back to numpy array

    if pos_peak_au.ndim != 2 or pos_peak_au.shape[1] != 3:
         print(f"Warning: Invalid shape for pos_peak_au in member {member_summary.get('member_id')}. Expected (n_particles, 3), got {pos_peak_au.shape}")
         return None # Invalid stats format

    if target_particle_idx >= pos_peak_au.shape[0]:
        print(f"Warning: target_particle_idx {target_particle_idx} out of bounds for analyzed particles ({pos_peak_au.shape[0]}) in member {member_summary.get('member_id')}.")
        return None

    # Calculate the magnitude of the peak position residual vector for the target particle
    peak_residual_magnitude = np.linalg.norm(pos_peak_au[target_particle_idx, :])

    return peak_residual_magnitude > threshold_au


def calculate_detection_rates(ensemble_results, detection_threshold_au, target_particle_idx=0, mass_bins=None):
    """
    Calculates overall and binned detection rates from ensemble results.

    Args:
        ensemble_results (list): List of summary dictionaries from run_ensemble.
        detection_threshold_au (float): Detection threshold (peak position residual in AU).
        target_particle_idx (int): Index of the target particle within the analyzed set.
        mass_bins (np.ndarray, optional): Array defining the edges for binning by PBH mass (M_sun).
                                          If None, only the overall rate is calculated.

    Returns:
        dict: A dictionary containing detection rates:
              {
                  'overall_rate': float,
                  'total_completed': int,
                  'total_detected': int,
                  'binned_rates': { # Optional, if mass_bins provided
                      'bin_edges': list,
                      'bin_centers': list,
                      'counts_total': list,
                      'counts_detected': list,
                      'rates': list
                  }
              }
    """
    total_completed = 0
    total_detected = 0
    detections_by_bin = []
    totals_by_bin = []
    num_bins = 0 # Initialize num_bins to ensure it's always bound

    if mass_bins is not None:
        # Check if mass_bins defines at least one bin
        if len(mass_bins) >= 2:
            num_bins = len(mass_bins) - 1
            detections_by_bin = [0] * num_bins
            totals_by_bin = [0] * num_bins
        else:
            print("Warning: mass_bins must define at least one bin (require >= 2 edges). Disabling binning.")
            mass_bins = None # Effectively disable binning if edges are invalid

    for member_summary in ensemble_results:
        if member_summary.get('status') != 'completed':
            continue

        total_completed += 1
        detected = is_detected(member_summary, detection_threshold_au, target_particle_idx)

        if detected is None:
            print(f"Warning: Could not determine detection status for member {member_summary.get('member_id')}. Skipping.")
            continue # Skip if detection status is unclear

        if detected:
            total_detected += 1

        # Binning by mass
        # Binning by mass - only if mass_bins is valid (checked above)
        if mass_bins is not None and num_bins > 0:
            pbh_mass = member_summary.get('pbh_params', {}).get('mass_msun')
            if pbh_mass is not None:
                # Find which bin this mass falls into
                bin_index = np.digitize(pbh_mass, mass_bins) - 1
                # Check bin_index against the now guaranteed > 0 num_bins
                if 0 <= bin_index < num_bins:
                    totals_by_bin[bin_index] += 1
                    if detected:
                        detections_by_bin[bin_index] += 1
            else:
                 print(f"Warning: Missing PBH mass for member {member_summary.get('member_id')}. Cannot bin.")


    results = {
        'overall_rate': (total_detected / total_completed) if total_completed > 0 else 0.0,
        'total_completed': total_completed,
        'total_detected': total_detected,
    }

    # Calculate binned results only if mass_bins was valid
    if mass_bins is not None and num_bins > 0:
        bin_centers = (mass_bins[:-1] + mass_bins[1:]) / 2.0
        binned_rates = [ (detections_by_bin[i] / totals_by_bin[i]) if totals_by_bin[i] > 0 else 0.0
                         for i in range(num_bins) ] # num_bins is correctly defined here
        results['binned_rates'] = {
            'bin_edges': mass_bins.tolist(),
            'bin_centers': bin_centers.tolist(),
            'counts_total': totals_by_bin,
            'counts_detected': detections_by_bin,
            'rates': binned_rates
        }

    return results # Only one return statement needed


if __name__ == '__main__':
    print("Ensemble Runner Module - Example Usage")

    # --- Dummy Initial Conditions (Fixed for all runs) ---
    # Using the simple circular orbits from simulation_runner example
    masses_example = np.array([1.0, 1e-6, 1e-5]) # M_sun (Sun, Body1, Body2)
    positions_example = np.array([[0,0,0], [1,0,0], [0,5,0]]) # AU
    G_sim = 4 * np.pi**2
    v1 = np.sqrt(G_sim * masses_example[0] / 1.0)
    v2 = np.sqrt(G_sim * masses_example[0] / 5.0)
    velocities_rebound_example = np.array([[0,0,0], [0, v1, 0], [-v2, 0, 0]]) # AU / (yr/2pi)
    velocities_au_day_example = velocities_rebound_example / n_body_simulation.VELOCITY_DAY_TO_REBOUND

    initial_conditions = {
        'positions_au': positions_example,
        'velocities_au_day': velocities_au_day_example,
        'masses_msun': masses_example
    }

    # --- Simulation Settings (Fixed for all runs) ---
    simulation_settings = {
        't_start_years': 0.0,
        't_end_years': 0.5, # Shorter duration for ensemble example
        'dt_years': 0.005,
        'integrator': 'ias15'
    }

    # --- Analysis Settings ---
    analysis_settings = {
        'particle_indices': [1, 2] # Analyze only Body1 and Body2
    }

    # --- Sampling Configuration ---
    sampling_config = {
        'mass_params': {'log_min': -11, 'log_max': -9},
        'b_params': {'b_max': 200.0},
        'vel_params': {'sigma_v_km_s': 250.0},
        'time_params': {'t_min': 0.1, 't_max': 0.4} # Ensure encounter within sim time
    }

    # --- Run Ensemble ---
    num_ensemble_members = 10 # Small number for example
    num_parallel_workers = min(4, multiprocessing.cpu_count()) # Limit workers for example

    print(f"\nRunning ensemble with {num_ensemble_members} members...")
    ensemble_results = run_ensemble(
        num_members=num_ensemble_members,
        initial_cond=initial_conditions,
        sim_settings=simulation_settings,
        analysis_settings=analysis_settings,
        sampling_config=sampling_config,
        num_workers=num_parallel_workers,
        checkpoint_interval=5 # Checkpoint more frequently for example
    )

    # --- Process Results ---
    print("\n--- Ensemble Summary ---")
    completed_count = sum(1 for r in ensemble_results if r.get('status') == 'completed')
    failed_count = num_ensemble_members - completed_count
    print(f"Total members attempted: {num_ensemble_members}")
    print(f"Successfully completed: {completed_count}")
    print(f"Failed: {failed_count}")

    # Example: Print stats for the first completed run
    first_completed = next((r for r in ensemble_results if r.get('status') == 'completed'), None)
    if first_completed:
        print("\nExample stats from first completed run (Member {}):".format(first_completed['member_id']))
        stats = first_completed.get('stats')
        if stats:
            for key, value_list in stats.items():
                # Value is list of lists (particles, dimensions)
                print(f"  {key}:")
                for particle_idx, p_stats in enumerate(value_list):
                     stat_str = np.array2string(np.array(p_stats), precision=3, floatmode='fixed', sign=' ')
                     # Map particle_idx back to original index if needed (using analysis_settings['particle_indices'])
                     original_idx = analysis_settings.get('particle_indices', list(range(len(p_stats))))[particle_idx]
                     print(f"    Particle {original_idx}: {stat_str}")
        else:
            print("  No stats found in summary.")

    # --- Detection Rate Analysis ---
    detection_threshold = 1e-5 # Example threshold: 1e-5 AU peak position residual
    # Target particle index within the *analyzed* set.
    # analysis_settings['particle_indices'] was [1, 2].
    # If we want to check detection for original particle 1 (Body1), its index in the analyzed set is 0.
    # If we want to check detection for original particle 2 (Body2), its index is 1.
    target_idx_in_analyzed = 0 # Corresponds to original particle 1 (Body1)

    print(f"\n--- Detection Rate Analysis (Threshold: {detection_threshold:.2e} AU for particle index {target_idx_in_analyzed} in analyzed set) ---")

    # Define mass bins (logarithmic)
    log_mass_min = sampling_config.get('mass_params', {}).get('log_min', -12)
    log_mass_max = sampling_config.get('mass_params', {}).get('log_max', -6)
    num_mass_bins = 5
    mass_bin_edges = np.logspace(log_mass_min, log_mass_max, num_mass_bins + 1)

    detection_stats = calculate_detection_rates(
        ensemble_results,
        detection_threshold_au=detection_threshold,
        target_particle_idx=target_idx_in_analyzed,
        mass_bins=mass_bin_edges
    )

    print(f"Total Completed Runs Analyzed: {detection_stats['total_completed']}")
    print(f"Total Detections: {detection_stats['total_detected']}")
    print(f"Overall Detection Rate: {detection_stats['overall_rate']:.4f}")

    if 'binned_rates' in detection_stats:
        print("\nDetection Rates by PBH Mass Bin:")
        binned = detection_stats['binned_rates']
        print("  Bin Edges (M_sun) | Bin Center (M_sun) | Total | Detected | Rate")
        print("--------------------|--------------------|-------|----------|------")
        for i in range(len(binned['rates'])):
            print(f"  {binned['bin_edges'][i]:<9.2e}-{binned['bin_edges'][i+1]:<9.2e}| {binned['bin_centers'][i]:<18.2e} | {binned['counts_total'][i]:<5} | {binned['counts_detected'][i]:<8} | {binned['rates'][i]:.4f}")

    print("\nEnsemble Runner Module - Example Finished.")