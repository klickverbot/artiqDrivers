from setuptools import setup

scripts = [
    "coherentDds_controller=artiqDrivers.frontend.coherentDds_controller:main",
    "dosDac_controller=artiqDrivers.frontend.dosDac_controller:main",
    "arduinoDds_controller=artiqDrivers.frontend.arduinoDds_controller:main",
    "trapDac_controller=artiqDrivers.frontend.trapDac_controller:main",
    "thorlabs_mdt69xb_controller=artiqDrivers.frontend.thorlabs_mdt69xb_controller:main"
]

setup(name='artiqDrivers',
    version='0.1',
    packages=['artiqDrivers'],
    entry_points={
        "console_scripts": scripts,
    }
)