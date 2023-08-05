from setuptools import setup
import simple_server

setup(
    name='simple-server',
    version='v0.1.1',
    description='A Python version-independent HTTP server.',
    long_description=simple_server.__doc__,
    url='https://github.com/brianhou/fuzzy-octo-ironman',
    author='Brian Hou',
    packages=['simple_server'],
    entry_points={
        'console_scripts': [
            'pyserve=simple_server.__init__:main',
        ],
    },
)
