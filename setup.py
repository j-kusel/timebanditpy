from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='timebandit',
    version='2.1',
    description='polytempo composition suite for python and extensions',
    long_description=readme(),
    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: C',
        'Topic :: Artistic Software',
        'Topic :: Sound/Audio :: MIDI',
        'Topic :: System :: Networking :: Time Synchronization',
    ],
    url='http://github.com/ultraturtle0/timebandit',
    author='Jordan Kusel',
    author_email='jordankusel@my.unt.edu',
    license='GNU GPLv3+',
    packages=['timebandit.apps', 'timebandit.lib'],
    install_requires=[
        'numpy',
        'scipy',
        'Pillow',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points = {
        'console_scripts': ['timebandit=timebandit:main'],
    },
    zip_safe=False)
