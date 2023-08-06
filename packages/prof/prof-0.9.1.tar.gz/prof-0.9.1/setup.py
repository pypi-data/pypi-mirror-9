from setuptools import setup, find_packages

setup(
    name='prof',
    packages=find_packages(),
    version='0.9.1',
    description='A tool to upload student work to http://prof.fil.univ-lille1.fr',
    author='calve',
    author_email='calvinh34@gmail.com',
    url='http://github.com/calve/prof',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Environment :: Console',
    ],
    install_requires=[
        "requests",
    ],
    entry_points={
        'console_scripts': [
            'prof=prof:main',
        ],
    }
)
