from setuptools import setup

setup(
    name="airfoil_converter",
    version="0.1",
    description="Using xfoil, interpolate and convert airfoils",
    author="Caleb Crome",
    author_email="caleb@crome.org",
    packages=["airfoil_converter"],
    package_data={
        'airfoil_converter': ['airfoils/airfoils-interpolated/*.dat'],
    },
    install_requires=[
        "numpy",
        "svgwrite",
        "dxfwrite",
        "matplotlib",
        "dash",
        "flask",
        "pandas",
    ],
    entry_points={
        "console_scripts": [
            "airfoil=airfoil_converter.airfoil:main",
            "airfoil-server=airfoil_converter.app:main",
        ]
    }
)
