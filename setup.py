"""
Setup script for the PrimordialEncounters package.
"""
from setuptools import setup, find_packages

setup(
    name="primordial_encounters",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "scipy",
        "rebound",
        "pytest",
        "pytest-cov",
    ],
    author="ImmortalDemonGod",
    author_email="58341488+ImmortalDemonGod@users.noreply.github.com",
    description="A package for simulating and analyzing primordial black hole encounters with the solar system",
    keywords="astronomy, astrophysics, simulation, n-body, primordial black holes",
    python_requires=">=3.8",
)
