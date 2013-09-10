from setuptools import setup

setup(
    name='whip-neustar',
    version='0.1',
    packages=['whip_neustar'],
    entry_points={
        'console_scripts': [
            'whip-neustar-cli = whip_neustar.cli:main',
        ],
    }
)
