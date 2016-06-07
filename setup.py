from setuptools import setup

scripts = [
    "coherentDds_controller=artiqDrivers.frontend.coherentDds_controller:main",
    "dosDac_controller=artiqDrivers.frontend.dosDac_controller:main",
    "arduinoDds_controller=artiqDrivers.frontend.arduinoDds_controller:main",
    "trapDac_controller=artiqDrivers.frontend.trapDac_controller:main",
    "thorlabs_mdt69xb_controller=artiqDrivers.frontend.thorlabs_mdt69xb_controller:main",
    "rohdeSynth_controller=artiqDrivers.frontend.rohdeSynth_controller:main",
    "tti_ql355_controller=artiqDrivers.frontend.tti_ql355_controller:main"
]

setup(name='artiqDrivers',
    version='0.1',
    packages=['artiqDrivers',
              'artiqDrivers.frontend',
              'artiqDrivers.devices',
              'artiqDrivers.devices.arduinoDds',
              'artiqDrivers.devices.coherentDds',
              'artiqDrivers.devices.dosDac',
              'artiqDrivers.devices.rohdeSynth',
              'artiqDrivers.devices.thorlabs_mdt69xb',
              'artiqDrivers.devices.trapDac',
              'artiqDrivers.devices.tti_ql355',
              'artiqDrivers.profileSwitcher',
              'artiqDrivers.profileSwitcher.profileSwitcher'
             ],
    entry_points={
        "console_scripts": scripts,
    },
    install_requires = [
        'pyserial>=3'
    ]
)
