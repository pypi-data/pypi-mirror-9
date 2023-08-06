from setuptools import setup

setup(
    name='terminalplot',
    version='0.2.1',
    description='Plot points in terminal',
    url='http://github.com/kressi/terminalplot',
    author='Michael Kressibucher',
    author_email='michael.kressibucher@gmail.com',
    license='AGPL',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Topic :: Scientific/Engineering :: Visualization'
    ],
    keywords='plot terminal graph console',
    packages=['terminalplot'],
    zip_safe=True,
    entry_points={
        'console_scripts': ['plot = terminalplot.command:main']
    }
)
