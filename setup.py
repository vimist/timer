from setuptools import setup


setup(
    name='timers',
    version='0.0.1',
    author='Vimist',
    description='A simple timer manager',
    packages=['timers'],
    entry_points={
        'console_scripts': [
            'timers=timers.__main__:main'
        ]
    }
)
