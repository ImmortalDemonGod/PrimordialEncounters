import numpy as np
import scipy.stats as stats

from .constants import KILOMETERS_PER_SECOND_TO_ASTRONOMICAL_UNITS_PER_DAY

# Define constants for parameter ranges or distributions (placeholders)
DEFAULT_MASS_RANGE_MSUN = (1e-12, 1e-6) # Example: Log-uniform mass range in Solar masses
DEFAULT_B_MAX_AU = 1000.0 # Example: Maximum impact parameter in AU
DEFAULT_VELOCITY_DISPERSION_KM_S = 200.0 # Example: Velocity dispersion in km/s for sampling
DEFAULT_TIME_RANGE_YEARS = (0.0, 100.0) # Example: Time range for encounter

# Conversion factors — derived from official sources (scipy.constants: IAU 2012
# exact au, SI day) via src/constants.py, never hand-typed (see F017).
kilometers_per_second_to_astronomical_units_per_day = KILOMETERS_PER_SECOND_TO_ASTRONOMICAL_UNITS_PER_DAY

def sample_pbh_mass(n_samples=1, log_min=np.log10(DEFAULT_MASS_RANGE_MSUN[0]), log_max=np.log10(DEFAULT_MASS_RANGE_MSUN[1])):
    """
    Samples PBH mass from a log-uniform distribution.

    Args:
        n_samples (int): Number of samples to generate.
        log_min (float): Log10 of the minimum mass (M_sun).
        log_max (float): Log10 of the maximum mass (M_sun).

    Returns:
        np.ndarray: Array of sampled masses in Solar masses.
    """
    log_masses = np.random.uniform(log_min, log_max, n_samples)
    return 10**log_masses

def sample_impact_parameter(n_samples=1, b_max=DEFAULT_B_MAX_AU):
    """
    Samples impact parameter 'b' assuming uniform probability in b^2 (area).
    This corresponds to P(b) db proportional to b db.

    Args:
        n_samples (int): Number of samples to generate.
        b_max (float): Maximum impact parameter (AU).

    Returns:
        np.ndarray: Array of sampled impact parameters in AU.
    """
    # Sample b^2 uniformly from 0 to b_max^2
    b_squared = np.random.uniform(0, b_max**2, n_samples)
    return np.sqrt(b_squared)

def sample_velocity(n_samples=1, sigma_v_km_s=DEFAULT_VELOCITY_DISPERSION_KM_S):
    """
    Samples PBH velocity relative to the Solar System Barycenter (SSB).
    Assumes an isotropic Maxwell-Boltzmann distribution for velocity components.

    Args:
        n_samples (int): Number of samples to generate.
        sigma_v_km_s (float): Velocity dispersion (characteristic speed) in km/s.
                              This relates to the Maxwell-Boltzmann distribution.

    Returns:
        np.ndarray: Array of sampled velocity vectors (vx, vy, vz) in AU/day.
                    Shape: (n_samples, 3)
    """
    # Sample 3D velocity components from a normal distribution (characteristic scale sigma_v)
    # Note: Maxwell-Boltzmann describes speed distribution |v|. For components, use Gaussian.
    vx_km_s = np.random.normal(0, sigma_v_km_s, n_samples)
    vy_km_s = np.random.normal(0, sigma_v_km_s, n_samples)
    vz_km_s = np.random.normal(0, sigma_v_km_s, n_samples)

    # Convert to AU/day
    vx_au_day = vx_km_s * kilometers_per_second_to_astronomical_units_per_day
    vy_au_day = vy_km_s * kilometers_per_second_to_astronomical_units_per_day
    vz_au_day = vz_km_s * kilometers_per_second_to_astronomical_units_per_day

    return np.stack([vx_au_day, vy_au_day, vz_au_day], axis=-1)

def sample_encounter_time(n_samples=1, t_min=DEFAULT_TIME_RANGE_YEARS[0], t_max=DEFAULT_TIME_RANGE_YEARS[1]):
    """
    Samples the time of closest approach (encounter) uniformly within a range.

    Args:
        n_samples (int): Number of samples to generate.
        t_min (float): Minimum encounter time (years).
        t_max (float): Maximum encounter time (years).

    Returns:
        np.ndarray: Array of sampled encounter times in years.
    """
    return np.random.uniform(t_min, t_max, n_samples)

def generate_pbh_sample(n_samples=1, mass_params=None, b_params=None, vel_params=None, time_params=None):
    """
    Generates a dictionary of PBH parameter samples.

    Args:
        n_samples (int): Number of samples (sets of parameters) to generate.
        mass_params (dict, optional): Parameters for sample_pbh_mass (log_min, log_max).
        b_params (dict, optional): Parameters for sample_impact_parameter (b_max).
        vel_params (dict, optional): Parameters for sample_velocity (sigma_v_km_s).
        time_params (dict, optional): Parameters for sample_encounter_time (t_min, t_max).

    Returns:
        list: A list of dictionaries, where each dictionary represents one sample set
              with keys: 'mass_msun', 'impact_param_au', 'velocity_au_day', 't_encounter_years'.
    """
    mass_params = mass_params or {}
    b_params = b_params or {}
    vel_params = vel_params or {}
    time_params = time_params or {}

    masses = sample_pbh_mass(n_samples, **mass_params)
    impact_params = sample_impact_parameter(n_samples, **b_params)
    velocities = sample_velocity(n_samples, **vel_params)
    encounter_times = sample_encounter_time(n_samples, **time_params)

    samples = []
    for i in range(n_samples):
        sample = {
            'mass_msun': masses[i],
            'impact_param_au': impact_params[i],
            'velocity_au_day': velocities[i], # This is a 3D vector
            't_encounter_years': encounter_times[i]
        }
        samples.append(sample)

    return samples


if __name__ == '__main__':
    print("PBH Parameter Sampler Module - Example Usage")

    num_samples = 5

    print(f"\nGenerating {num_samples} PBH parameter samples with default settings...")
    default_samples = generate_pbh_sample(num_samples)

    for i, sample in enumerate(default_samples):
        print(f"\nSample {i+1}:")
        print(f"  Mass: {sample['mass_msun']:.3e} M_sun")
        print(f"  Impact Parameter: {sample['impact_param_au']:.3f} AU")
        vel_str = np.array2string(sample['velocity_au_day'], precision=3, floatmode='fixed', sign=' ')
        print(f"  Velocity: {vel_str} AU/day")
        print(f"  Encounter Time: {sample['t_encounter_years']:.3f} years")

    # Example with custom parameters
    print(f"\nGenerating 2 samples with custom settings...")
    custom_mass_params = {'log_min': -10, 'log_max': -8} # 1e-10 to 1e-8 M_sun
    custom_b_params = {'b_max': 500.0} # Max b = 500 AU
    custom_vel_params = {'sigma_v_km_s': 150.0} # Lower velocity dispersion
    custom_time_params = {'t_min': 10.0, 't_max': 50.0} # Encounter between 10 and 50 years

    custom_samples = generate_pbh_sample(
        n_samples=2,
        mass_params=custom_mass_params,
        b_params=custom_b_params,
        vel_params=custom_vel_params,
        time_params=custom_time_params
    )

    for i, sample in enumerate(custom_samples):
        print(f"\nCustom Sample {i+1}:")
        print(f"  Mass: {sample['mass_msun']:.3e} M_sun")
        print(f"  Impact Parameter: {sample['impact_param_au']:.3f} AU")
        vel_str = np.array2string(sample['velocity_au_day'], precision=3, floatmode='fixed', sign=' ')
        print(f"  Velocity: {vel_str} AU/day")
        print(f"  Encounter Time: {sample['t_encounter_years']:.3f} years")

    print("\nParameter Sampler Module - Example Finished.")
