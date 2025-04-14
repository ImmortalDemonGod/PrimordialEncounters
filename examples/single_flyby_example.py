"""
Example script demonstrating a single PBH flyby simulation.

This example shows how to:
1. Set up a solar system model
2. Add a primordial black hole
3. Run the simulation
4. Analyze the results
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.n_body_simulation import NBodySimulation
from src.analytic_impulse import AnalyticImpulse
from src.residual_analysis import ResidualAnalysis

def run_single_flyby_example():
    """Run a simple example of a PBH flyby."""
    print("Running single PBH flyby example...")
    
    # Example parameters
    pbh_mass = 1e-10  # Solar masses
    impact_parameter = 1.0  # AU
    approach_angle = 0.5  # radians
    pbh_velocity = 250.0  # km/s
    
    print(f"PBH parameters:")
    print(f"  Mass: {pbh_mass} solar masses")
    print(f"  Impact parameter: {impact_parameter} AU")
    print(f"  Approach angle: {approach_angle} radians")
    print(f"  Velocity: {pbh_velocity} km/s")
    
    print("\nThis is a placeholder example. The actual implementation will:")
    print("1. Initialize the solar system model")
    print("2. Add a PBH with the specified parameters")
    print("3. Run the simulation")
    print("4. Analyze the orbital perturbations")
    print("5. Visualize the results")

if __name__ == "__main__":
    run_single_flyby_example()
