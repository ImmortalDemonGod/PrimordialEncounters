import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
import os

# Define some default plot settings
DEFAULT_FIGSIZE = (8, 8)
DEFAULT_SAVE_DPI = 300

def plot_trajectories_2d(times, positions, labels=None, title="Trajectories (XY Plane)",
                         xlabel="X (AU)", ylabel="Y (AU)", figsize=DEFAULT_FIGSIZE,
                         legend=True, save_path=None):
    """
    Plots the 2D (X-Y) trajectories of particles from simulation results.

    Args:
        times (np.ndarray): Array of time steps (n_steps,). Not directly used for XY plot
                            but good practice to potentially include for context later.
        positions (np.ndarray): Position data array (n_steps, n_particles, 3) in AU.
        labels (list, optional): List of labels for each particle. If None, default
                                 labels ('Particle 0', 'Particle 1', ...) are used.
                                 Length must match n_particles.
        title (str): Title for the plot.
        xlabel (str): Label for the X-axis.
        ylabel (str): Label for the Y-axis.
        figsize (tuple): Figure size (width, height) in inches.
        legend (bool): Whether to display the legend.
        save_path (str, optional): If provided, saves the plot to this path. The format
                                   is determined by the file extension (e.g., .png, .pdf).

    Returns:
        tuple: (fig, ax) The matplotlib figure and axes objects. Returns (None, None)
               if input is invalid.
    """
    if positions is None or positions.ndim != 3 or positions.shape[0] == 0 or positions.shape[2] != 3:
        print("Error: Invalid positions array shape. Expected (n_steps > 0, n_particles, 3).")
        return None, None

    n_steps, n_particles, _ = positions.shape

    if labels is None:
        labels = [f"Particle {i}" for i in range(n_particles)]
    elif len(labels) != n_particles:
        print(f"Warning: Number of labels ({len(labels)}) does not match number of particles ({n_particles}). Using default labels.")
        labels = [f"Particle {i}" for i in range(n_particles)]

    fig, ax = plt.subplots(figsize=figsize)

    # Plot trajectory for each particle
    for i in range(n_particles):
        ax.plot(positions[:, i, 0], positions[:, i, 1], label=labels[i], marker='.', markersize=1, linestyle='-')
        # Mark start and end points (optional)
        # ax.plot(positions[0, i, 0], positions[0, i, 1], 'o', label=f"{labels[i]} Start")
        # ax.plot(positions[-1, i, 0], positions[-1, i, 1], 'x', label=f"{labels[i]} End")


    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_aspect('equal', adjustable='box') # Ensure equal scaling for trajectory plots

    if legend:
        ax.legend()

    if save_path:
        try:
            dir_name = os.path.dirname(save_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            fig.savefig(save_path, dpi=DEFAULT_SAVE_DPI, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        except Exception as e:
            print(f"Error saving plot to '{save_path}': {e}")

    plt.show() # Display the plot interactively

    return fig, ax


# --- New Function (Residual Plotting) --- To be added before line 97 ---

def plot_residual_timeseries(times, residuals, particle_indices=None, labels=None,
                             residual_type="Position", units="AU",
                             title="Residuals vs. Time", xlabel="Time (years)",
                             figsize=(10, 6), save_path=None):
    """
    Plots the time series of residuals (position or velocity) for specified particles.
    Creates subplots for X, Y, and Z components.

    Args:
        times (np.ndarray): Array of time steps (n_steps,).
        residuals (np.ndarray): Residual data array (n_steps, n_particles, 3).
        particle_indices (list, optional): List of integer indices of the particles
                                           to plot residuals for. If None, plots for all.
        labels (list, optional): List of labels corresponding to the *original* particle
                                 indices before potential selection via particle_indices.
                                 Used to label the plotted lines correctly. If None,
                                 default labels are used based on the indices in the
                                 residuals array.
        residual_type (str): Type of residual being plotted (e.g., "Position", "Velocity").
                             Used for plot titles and labels.
        units (str): Units of the residuals (e.g., "AU", "AU/day"). Used for y-axis label.
        title (str): Base title for the plot (will be appended with component).
        xlabel (str): Label for the X-axis (time).
        figsize (tuple): Figure size (width, height) in inches.
        save_path (str, optional): If provided, saves the plot to this path.

    Returns:
        tuple: (fig, axes) The matplotlib figure and axes array (3 subplots).
               Returns (None, None) if input is invalid.
    """
    if times is None or residuals is None:
        print("Error: Times or residuals data is missing.")
        return None, None
    if residuals.ndim != 3 or residuals.shape[0] != len(times) or residuals.shape[2] != 3:
        print("Error: Invalid residuals array shape or mismatch with times. Expected (n_steps, n_particles, 3).")
        return None, None

    n_steps, n_particles_res, _ = residuals.shape

    if particle_indices is None:
        particle_indices = list(range(n_particles_res))
        plot_labels = [f"Particle {i}" for i in particle_indices]
    else:
        # Filter indices to be within the bounds of the residual array
        valid_indices = [idx for idx in particle_indices if 0 <= idx < n_particles_res]
        if not valid_indices:
            print("Error: None of the specified particle_indices are valid for the provided residuals array.")
            return None, None
        # Select the corresponding residuals
        residuals = residuals[:, valid_indices, :]
        # Create labels for the plot
        if labels:
            try:
                # Try to get original labels corresponding to the valid indices
                plot_labels = [labels[idx] for idx in valid_indices]
            except IndexError:
                print(f"Warning: Mismatch between original labels and selected particle indices. Using default labels.")
                plot_labels = [f"Particle {idx}" for idx in valid_indices]
        else:
             plot_labels = [f"Particle {idx}" for idx in valid_indices]
        # Update n_particles_res to reflect the selection
        n_particles_res = len(valid_indices)


    fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)
    components = ['X', 'Y', 'Z']
    ylabel_base = f"{residual_type} Residual ({units})"

    for dim, ax in enumerate(axes):
        for i in range(n_particles_res):
            ax.plot(times, residuals[:, i, dim], label=plot_labels[i], marker='.', markersize=1, linestyle='-')
        ax.set_ylabel(f"{components[dim]}-{ylabel_base}")
        ax.grid(True, linestyle='--', alpha=0.6)
        if dim == 0:
            ax.set_title(title)
        if dim == 2: # Bottom subplot
            ax.set_xlabel(xlabel)
        if n_particles_res > 1: # Add legend if multiple particles plotted
             ax.legend()

    fig.tight_layout() # Adjust layout to prevent overlap

    if save_path:
        try:
            dir_name = os.path.dirname(save_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            fig.savefig(save_path, dpi=DEFAULT_SAVE_DPI, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        except Exception as e:
            print(f"Error saving plot to '{save_path}': {e}")

    plt.show()

    return fig, axes

# --- New Functions (Ensemble Visualization) --- To be added before line 179 ---

def plot_detection_scatter(ensemble_results, x_param='mass_msun', y_param='impact_param_au',
                           color_metric='peak_pos_residual', target_particle_idx=0,
                           detection_threshold=None,
                           title="Detection Metric vs. PBH Parameters",
                           xlabel=None, ylabel=None, clabel=None,
                           x_log=True, y_log=True, c_log=True,
                           figsize=(10, 8), save_path=None):
    """
    Creates a scatter plot of ensemble results, coloring points by a detection metric.

    Args:
        ensemble_results (list): List of summary dictionaries from run_ensemble.
        x_param (str): Key in pbh_params dict for the x-axis (e.g., 'mass_msun').
        y_param (str): Key in pbh_params dict for the y-axis (e.g., 'impact_param_au').
        color_metric (str): Metric to use for coloring points. Can be a key in pbh_params
                            (e.g., 't_encounter_years') or a calculated metric like
                            'peak_pos_residual' or 'peak_vel_residual'.
        target_particle_idx (int): Index of the target particle within the *analyzed*
                                   particles, used if color_metric is residual-based.
        detection_threshold (float, optional): If provided, plots a contour line or marker
                                               indicating the detection threshold based on
                                               the color_metric (assumes color_metric is
                                               the value being thresholded).
        title (str): Plot title.
        xlabel (str, optional): X-axis label. Defaults to x_param.
        ylabel (str, optional): Y-axis label. Defaults to y_param.
        clabel (str, optional): Color bar label. Defaults to color_metric.
        x_log (bool): Use log scale for x-axis.
        y_log (bool): Use log scale for y-axis.
        c_log (bool): Use log scale for color bar.
        figsize (tuple): Figure size.
        save_path (str, optional): Path to save the plot.

    Returns:
        tuple: (fig, ax) The matplotlib figure and axes objects. Returns (None, None)
               if input is invalid or no data to plot.
    """
    if not ensemble_results:
        print("Error: ensemble_results list is empty.")
        return None, None

    x_values = []
    y_values = []
    color_values = []
    valid_members = 0

    # Define how to extract/calculate color metric
    def get_color_value(summary, metric_key, particle_idx):
        if metric_key in summary.get('pbh_params', {}):
            return summary['pbh_params'][metric_key]
        elif metric_key == 'peak_pos_residual':
            stats = summary.get('stats')
            if stats and 'pos_peak_au' in stats:
                pos_peak = np.array(stats['pos_peak_au'])
                if particle_idx < pos_peak.shape[0]:
                    return np.linalg.norm(pos_peak[particle_idx, :])
        elif metric_key == 'peak_vel_residual':
             stats = summary.get('stats')
             if stats and 'vel_peak_au_day' in stats:
                 vel_peak = np.array(stats['vel_peak_au_day'])
                 if particle_idx < vel_peak.shape[0]:
                     return np.linalg.norm(vel_peak[particle_idx, :])
        # Add more calculated metrics here if needed
        return None

    # Extract data from results
    for summary in ensemble_results:
        if summary.get('status') != 'completed':
            continue

        pbh_params = summary.get('pbh_params')
        if not pbh_params or x_param not in pbh_params or y_param not in pbh_params:
            continue

        c_val = get_color_value(summary, color_metric, target_particle_idx)
        if c_val is None:
            continue

        x_values.append(pbh_params[x_param])
        y_values.append(pbh_params[y_param])
        color_values.append(c_val)
        valid_members += 1

    if valid_members == 0:
        print("Error: No valid completed members found with the required parameters and metrics.")
        return None, None

    x_values = np.array(x_values)
    y_values = np.array(y_values)
    color_values = np.array(color_values)

    # Handle log scaling for color, avoiding log(0) or log(negative)
    if c_log:
        # Ensure vmin is positive for LogNorm
        min_positive_c = np.min(color_values[color_values > 0]) if np.any(color_values > 0) else 1e-9 # Add small epsilon if no positive values
        norm = LogNorm(vmin=min_positive_c, vmax=np.max(color_values))
    else:
        norm = Normalize(vmin=np.min(color_values), vmax=np.max(color_values))

    fig, ax = plt.subplots(figsize=figsize)
    scatter = ax.scatter(x_values, y_values, c=color_values, cmap='viridis', norm=norm, alpha=0.7)

    # Add detection threshold contour/marker if specified
    # This is complex to do accurately without a grid; simple indication for now
    if detection_threshold is not None and color_metric in ['peak_pos_residual', 'peak_vel_residual']:
         # Highlight points above threshold?
         detected_mask = color_values > detection_threshold
         ax.scatter(x_values[detected_mask], y_values[detected_mask],
                    facecolors='none', edgecolors='red', s=80, label=f'> {detection_threshold:.1e}')
         if np.any(detected_mask): # Only add label if points are detected
             ax.legend()


    ax.set_xlabel(xlabel or x_param)
    ax.set_ylabel(ylabel or y_param)
    ax.set_title(title)
    if x_log: ax.set_xscale('log')
    if y_log: ax.set_yscale('log')
    ax.grid(True, linestyle='--', alpha=0.6)

    cbar = fig.colorbar(scatter)
    cbar.set_label(clabel or color_metric)

    if save_path:
        try:
            dir_name = os.path.dirname(save_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            fig.savefig(save_path, dpi=DEFAULT_SAVE_DPI, bbox_inches='tight')
            print(f"Scatter plot saved to {save_path}")
        except Exception as e:
            print(f"Error saving scatter plot to '{save_path}': {e}")

    plt.show()
    return fig, ax


def plot_binned_detection_rate(detection_stats, title="Detection Rate vs. PBH Mass",
                               xlabel="PBH Mass (M_sun)", ylabel="Detection Rate",
                               figsize=(8, 5), save_path=None):
    """
    Plots the binned detection rate calculated by calculate_detection_rates.

    Args:
        detection_stats (dict): The dictionary returned by calculate_detection_rates.
                                Must contain the 'binned_rates' sub-dictionary.
        title (str): Plot title.
        xlabel (str): X-axis label.
        ylabel (str): Y-axis label.
        figsize (tuple): Figure size.
        save_path (str, optional): Path to save the plot.

    Returns:
        tuple: (fig, ax) The matplotlib figure and axes objects. Returns (None, None)
               if input is invalid.
    """
    if not detection_stats or 'binned_rates' not in detection_stats:
        print("Error: Invalid detection_stats input or missing 'binned_rates'.")
        return None, None

    binned = detection_stats['binned_rates']
    bin_centers = binned.get('bin_centers')
    rates = binned.get('rates')
    counts_total = binned.get('counts_total')

    if bin_centers is None or rates is None or counts_total is None:
        print("Error: Missing required data (bin_centers, rates, counts_total) in binned_rates.")
        return None, None

    if len(bin_centers) != len(rates) or len(bin_centers) != len(counts_total):
        print("Error: Mismatch in lengths of binned data arrays.")
        return None, None

    fig, ax = plt.subplots(figsize=figsize)

    # Calculate error bars (e.g., binomial proportion confidence interval - using simple approximation sqrt(p(1-p)/n))
    errors = [np.sqrt(r * (1 - r) / n) if n > 0 else 0 for r, n in zip(rates, counts_total)]

    ax.errorbar(bin_centers, rates, yerr=errors, fmt='o-', capsize=5, label="Detection Rate")

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xscale('log') # Usually makes sense for mass bins
    ax.set_ylim(0, 1.05) # Rate is between 0 and 1
    ax.grid(True, linestyle='--', alpha=0.6)
    # ax.legend() # Only one line, legend might be redundant

    # Optional: Add text showing total counts per bin
    # for i, count in enumerate(counts_total):
    #     ax.text(bin_centers[i], rates[i] + 0.05, f"n={count}", ha='center', va='bottom', fontsize=8)


    if save_path:
        try:
            dir_name = os.path.dirname(save_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            fig.savefig(save_path, dpi=DEFAULT_SAVE_DPI, bbox_inches='tight')
            print(f"Binned rate plot saved to {save_path}")
        except Exception as e:
            print(f"Error saving binned rate plot to '{save_path}': {e}")

    plt.show()
    return fig, ax

if __name__ == '__main__':
    print("Visualization Module - Example Usage")

    # --- Create Dummy Simulation Results ---
    n_steps_eg = 200
    n_particles_eg = 3
    times_eg = np.linspace(0, 2 * np.pi, n_steps_eg) # Simulate one orbit

    # Particle 0: Stationary at origin
    pos0 = np.zeros((n_steps_eg, 1, 3))

    # Particle 1: Circular orbit in XY plane
    radius1 = 1.0
    pos1 = np.zeros((n_steps_eg, 1, 3))
    pos1[:, 0, 0] = radius1 * np.cos(times_eg)
    pos1[:, 0, 1] = radius1 * np.sin(times_eg)

    # Particle 2: Elliptical orbit in XY plane
    radius2_a = 5.0 # Semi-major axis
    radius2_b = 3.0 # Semi-minor axis
    pos2 = np.zeros((n_steps_eg, 1, 3))
    pos2[:, 0, 0] = radius2_a * np.cos(times_eg)
    pos2[:, 0, 1] = radius2_b * np.sin(times_eg)

    # Combine positions
    positions_eg = np.concatenate([pos0, pos1, pos2], axis=1)
    labels_eg = ["Sun", "Earth", "PlanetX"]
    # --- End Dummy Data ---

    print("\nPlotting 2D trajectories...")
    fig, ax = plot_trajectories_2d(
        times_eg,
        positions_eg,
        labels=labels_eg,
        title="Example Trajectories",
        save_path="plots/example_trajectories.png" # Example save path
    )

    if fig:
        print("Plot generated.")
    else:
        print("Plot generation failed.")

    # --- Generate Dummy Residual Data ---
    # Assume residuals were calculated for particles 1 and 2 (Earth, PlanetX)
    n_particles_res_eg = 2
    # Create some oscillating residuals for effect
    res_p_eg = np.zeros((n_steps_eg, n_particles_res_eg, 3))
    res_p_eg[:, 0, 0] = 1e-5 * np.sin(times_eg * 5) # Residuals for Earth X
    res_p_eg[:, 0, 1] = 5e-6 * np.cos(times_eg * 5) # Residuals for Earth Y
    res_p_eg[:, 1, 2] = 2e-5 * np.sin(times_eg * 2 + 0.5) # Residuals for PlanetX Z
    # --- End Dummy Residual Data ---

    print("\nPlotting residual time series...")
    # Note: We pass the original labels_eg, the function selects based on particle_indices
    # Here, the dummy res_p_eg corresponds to original particles 1 and 2.
    # So we want to plot indices 0 and 1 of res_p_eg, which correspond to original 1 and 2.
    fig_res, ax_res = plot_residual_timeseries(
        times_eg,
        res_p_eg,
        particle_indices=[0, 1], # Indices *within the residual array*
        labels=labels_eg, # Original labels ["Sun", "Earth", "PlanetX"]
        residual_type="Position",
        units="AU",
        title="Example Position Residuals",
        save_path="plots/example_residuals.png"
    )

    if fig_res:
        print("Residual plot generated.")
    else:
        print("Residual plot generation failed.")

    # --- Generate Dummy Ensemble Results ---
    # Create results similar to what ensemble_runner would produce
    dummy_ensemble_results = []
    num_dummy_members = 50
    dummy_masses = 10**np.random.uniform(-11, -9, num_dummy_members)
    dummy_impacts = 10**np.random.uniform(0, 2, num_dummy_members) # 1 to 100 AU
    # Simulate some detection metric (peak residual) - make it depend on mass/impact
    dummy_peak_res = np.zeros((num_dummy_members, 2, 3)) # For 2 analyzed particles
    for i in range(num_dummy_members):
         # Example: Higher residual for lower mass and lower impact parameter
         peak_mag = (1e-4 / (dummy_masses[i] / 1e-11)) * (1 / (dummy_impacts[i] / 10))**2
         dummy_peak_res[i, 0, 0] = peak_mag * np.random.uniform(0.5, 1.0) # Assign to X of particle 0

         dummy_ensemble_results.append({
             'member_id': i,
             'status': 'completed',
             'pbh_params': {
                 'mass_msun': dummy_masses[i],
                 'impact_param_au': dummy_impacts[i],
                 # Add other params if needed for plotting
             },
             'stats': {
                 # Only include peak pos for this example
                 'pos_peak_au': dummy_peak_res[i].tolist()
             }
         })
    # --- End Dummy Ensemble Results ---

    print("\nPlotting detection scatter plot...")
    fig_scatter, ax_scatter = plot_detection_scatter(
        dummy_ensemble_results,
        x_param='mass_msun',
        y_param='impact_param_au',
        color_metric='peak_pos_residual', # Use calculated peak residual magnitude
        target_particle_idx=0, # Color based on residual of first analyzed particle
        detection_threshold=1e-5, # Example threshold
        x_log=True, y_log=True, c_log=True,
        clabel="Peak Pos Residual Mag (AU)",
        save_path="plots/example_detection_scatter.png"
    )
    if fig_scatter:
        print("Scatter plot generated.")
    else:
        print("Scatter plot generation failed.")


    print("\nPlotting binned detection rate...")
    # Need detection stats first (use dummy results and threshold)
    try:
        # Need to import calculate_detection_rates if running as script
        from ensemble_runner import calculate_detection_rates
        dummy_detection_threshold = 1e-5
        dummy_mass_bins = np.logspace(-11, -9, 6) # 5 bins
        dummy_detection_stats = calculate_detection_rates(
            dummy_ensemble_results,
            detection_threshold_au=dummy_detection_threshold,
            target_particle_idx=0,
            mass_bins=dummy_mass_bins
        )

        fig_binned, ax_binned = plot_binned_detection_rate(
            dummy_detection_stats,
            save_path="plots/example_binned_rate.png"
        )
        if fig_binned:
            print("Binned rate plot generated.")
        else:
            print("Binned rate plot generation failed.")
    except ImportError:
         print("Skipping binned rate plot example (requires ensemble_runner module).")
    except Exception as e:
        print(f"Error during binned rate plot example: {e}")

    print("\nVisualization Module - Example Finished.")