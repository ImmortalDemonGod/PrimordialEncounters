import numpy as np

# Gravitational constant in simulation units (AU^3 / (M_sun * (yr/2pi)^2))
G = 4 * np.pi**2

def calculate_velocity_kick(pbh_mass, pbh_position, pbh_velocity, body_position, body_velocity):
    """
    Calculates the velocity kick imparted to a body by a passing PBH using the impulse approximation.

    Assumes PBH travels on an undeflected linear trajectory relative to the body.
    Calculates the point of closest approach to determine impact parameter and kick direction.
    Uses simulation units: AU, M_sun, time in yr/(2pi), velocity in AU/(yr/2pi).

    Args:
        pbh_mass (float): Mass of the Primordial Black Hole (PBH) in M_sun.
        pbh_position (np.ndarray): Initial position vector of the PBH (3D) in AU.
        pbh_velocity (np.ndarray): Velocity vector of the PBH (3D) in AU/(yr/2pi) (assumed constant).
        body_position (np.ndarray): Initial position vector of the body (3D) in AU.
        body_velocity (np.ndarray): Velocity vector of the body (3D) in AU/(yr/2pi) (assumed constant during encounter).

    Returns:
        tuple: A tuple containing:
            - delta_v (np.ndarray): The change in velocity vector (3D) for the body in AU/(yr/2pi).
                                    Returns zero vector if relative velocity or impact parameter is zero.
            - t_ca (float): The time of closest approach relative to the initial time, in yr/(2pi).
                            Returns 0.0 if relative velocity is zero.

    Notes:
        - Assumes the encounter is instantaneous relative to the orbital period of the body.
        - Assumes the PBH path is undeflected.
        - Calculates impact parameter 'b' and relative position at closest approach 'r_ca'.
    """
    initial_relative_position = pbh_position - body_position
    relative_velocity = pbh_velocity - body_velocity
    v_rel_mag_sq = np.dot(relative_velocity, relative_velocity)

    if v_rel_mag_sq == 0:
        # Avoid division by zero if velocities are identical (no relative motion)
        print("Warning: Relative velocity is zero. No kick applied.")
        return np.zeros(3, dtype=float), 0.0 # No kick, t_ca is undefined/irrelevant, return 0

    # Calculate time of closest approach (t_ca) relative to the initial time
    # t_ca = - (r_rel(0) . v_rel) / |v_rel|^2
    t_ca = -np.dot(initial_relative_position, relative_velocity) / v_rel_mag_sq

    # Calculate the relative position vector at the time of closest approach
    # r_ca = r_rel(0) + v_rel * t_ca
    r_ca = initial_relative_position + relative_velocity * t_ca

    # The impact parameter 'b' is the magnitude of the relative position vector at closest approach
    b_sq = np.dot(r_ca, r_ca)
    if b_sq == 0:
        # Direct hit or numerical precision issue
        print("Warning: Calculated impact parameter is zero. Impulse approximation is invalid. No kick applied.")
        return np.zeros(3, dtype=float), t_ca # Return zero kick but calculated t_ca

    b = np.sqrt(b_sq)
    v_rel_mag = np.sqrt(v_rel_mag_sq)

    # Magnitude of the velocity kick
    # delta_v_mag = (2 * G * M_pbh) / (b * v_rel)
    delta_v_magnitude = (2 * G * pbh_mass) / (b * v_rel_mag)

    # Direction of the kick is opposite to the relative position vector at closest approach
    # kick_direction = -r_ca / |r_ca| = -r_ca / b
    kick_direction = -r_ca / b

    # Calculate the final delta-v vector
    delta_v = delta_v_magnitude * kick_direction

    return delta_v, t_ca


def apply_kick(body_state, delta_v):
    """
    Applies a velocity kick to a body's state dictionary.

    Args:
        body_state (dict): Dictionary representing the body's state,
                           must include 'velocity' (np.ndarray or list).
                           Example: {'position': np.array([...]), 'velocity': np.array([...]), 'mass': ...}
        delta_v (np.ndarray): The velocity change vector (3D) to apply.

    Returns:
        dict: The updated body state dictionary.
    """
    if 'velocity' not in body_state:
        raise ValueError("Body state must include a 'velocity' key.")
    # Ensure velocity is a numpy array for addition
    current_velocity = np.asarray(body_state['velocity'])
    if current_velocity.shape != (3,) or delta_v.shape != (3,):
         raise ValueError("Velocity and delta_v must be 3D vectors.")

    updated_state = body_state.copy()
    updated_state['velocity'] = current_velocity + delta_v
    return updated_state

# Example Usage (Placeholder - requires proper inputs)
if __name__ == "__main__":
    # Example PBH parameters
    pbh_mass_example = 1e-10  # M_sun
    # Initial PBH state (example: coming from -x direction towards origin)
    pbh_position_example = np.array([-10.0, 0.1, 0.0]) # AU
    # Velocity approx 200 km/s -> 94.8 AU/day -> 94.8 * 365.25 / (2*pi) AU/(yr/2pi) ~= 5510 AU/(yr/2pi)
    pbh_velocity_example = np.array([5510.0, 0, 0]) # AU/(yr/2pi)

    # Example Body (e.g., Earth at perihelion)
    # Initial Earth state
    earth_position_example = np.array([1.0, 0, 0]) # AU
    # Velocity approx 30 km/s -> 0.0172 AU/day -> 0.0172 * 365.25 / (2*pi) AU/(yr/2pi) ~= 1.0 AU/(yr/2pi)
    earth_velocity_example = np.array([0, 1.0, 0]) # AU/(yr/2pi)

    print("Calculating velocity kick...")
    try:
        delta_v_kick, time_ca = calculate_velocity_kick(
            pbh_mass=pbh_mass_example,
            pbh_position=pbh_position_example,
            pbh_velocity=pbh_velocity_example,
            body_position=earth_position_example,
            body_velocity=earth_velocity_example,
        )
        # Calculate derived parameters for verification
        _rel_vel = pbh_velocity_example - earth_velocity_example
        _v_rel_mag = np.linalg.norm(_rel_vel)
        _init_rel_pos = pbh_position_example - earth_position_example
        _t_ca_calc = -np.dot(_init_rel_pos, _rel_vel) / np.dot(_rel_vel, _rel_vel)
        _r_ca = _init_rel_pos + _rel_vel * _t_ca_calc
        _b = np.linalg.norm(_r_ca)

        print(f"  Initial Relative Position: {_init_rel_pos} AU")
        print(f"  Relative Velocity: {_rel_vel} AU/(yr/2pi) (Magnitude: {_v_rel_mag:.4f} AU/(yr/2pi))")
        print(f"  Calculated Time to Closest Approach: {_t_ca_calc:.4f} yr/(2pi)")
        print(f"  Returned Time to Closest Approach (t_ca): {time_ca:.4f} yr/(2pi)")
        print(f"  Relative Position at Closest Approach (r_ca): {_r_ca} AU")
        print(f"  Impact Parameter (b = |r_ca|): {_b:.4f} AU")
        print(f"Calculated Delta-V Kick (vector): {delta_v_kick} AU/(yr/2pi)")
        print(f"  Magnitude of Kick: {np.linalg.norm(delta_v_kick):.4e} AU/(yr/2pi)")

        # Example state update
        initial_state = {
            'name': 'Earth',
            'position': earth_position_example,
            'velocity': earth_velocity_example,
            'mass': 3e-6 # M_sun
        }
        print(f"\nInitial state: {initial_state}")

        # Note: Applying the kick assumes it happens *instantaneously* at t=0
        # A more accurate simulation would evolve the body to t_ca, apply kick, then evolve further.
        # Or, integrate the kick into the N-body simulation at the correct time.
        final_state = apply_kick(initial_state, delta_v_kick)
        print(f"Final state after kick (applied at t=0): {final_state}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")