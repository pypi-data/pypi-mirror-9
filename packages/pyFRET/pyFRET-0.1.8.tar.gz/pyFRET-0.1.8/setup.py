from distutils.core import setup

# need to fix url and install requirements.
# also good to get it working for python 3
setup(
    name='pyFRET',
    version='0.1.8',
    author='Rebecca R. Murphy',
    author_email='rebeccaroisin@gmail.com',
    packages=['pyfret'],
    scripts=['bin/FRET_example.py','bin/ALEX_example.py', 'bin/FRET_bursts_example.py', 
        'bin/ALEX_config.cfg', 'bin/FRET_config.cfg', 'bin/4bp_FRET_config.cfg',
        'bin/6bp_FRET_config.cfg', 'bin/8bp_FRET_config.cfg', 
        'bin/10bp_FRET_config.cfg', 'bin/12bp_FRET_config.cfg',
        'bin/4bp_ALEX_config.cfg', 'bin/6bp_ALEX_config.cfg',
        'bin/8bp_ALEX_config.cfg', 'bin/10bp_ALEX_config.cfg',
        'bin/12bp_ALEX_config.cfg', 'bin/FRET_bursts_config.cfg'],
    url='http://pypi.python.org/pypi/pyFRET/',
        license='LICENSE.txt',
    description='Library for analysis of single-molecule fluorescence (smFRET) data',
    long_description=open('README').read(),
    install_requires=[
        "scipy >= 0.9.0",
        "numpy >= 1.6.1",
        "matplotlib >= 1.1.1rc",
        "scikit-learn >= 0.15.2"
    ],
)