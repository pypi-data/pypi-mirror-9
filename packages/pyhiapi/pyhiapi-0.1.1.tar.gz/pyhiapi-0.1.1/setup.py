"""Set up hiapi
"""

from distutils.core import setup

setup(
    name='pyhiapi',
    version='0.1.1',
    author='Ryan Jung',
    author_email='gradysghost@gmail.com',
    package=['pyhiapi'],
    url='https://github.com/GradysGhost/pyhiapi',
    license='LICENCE',
    description='PyHiAPI - Simple test API',
    long_description=open('README.md').read(),
    install_requires=[
        'flask'
    ],
    entry_points={
        'console_scripts': [
            'hiapi = hiapi.hi:main'
        ]
    }
)
