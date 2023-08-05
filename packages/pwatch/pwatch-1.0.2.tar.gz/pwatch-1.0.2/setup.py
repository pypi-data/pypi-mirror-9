"""
Setuptools script for pwatch

"""
from setuptools import setup

def readme():
    """
    Extracts readme contents

    """
    with open('README.md') as f:
        return f.read()

def requirements():
    """
    Extacts requirements.txt contents

    """
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name='pwatch',
    version='1.0.2',
    description='Simple tool to watch and report processes with excessive resource usage',
    long_description=readme(),
    license='MIT',
    url='https://github.com/quanta-computing/pwatch',
    author="Matthieu 'Korrigan' Rosinski",
    author_email='mro@quanta-computing.com',
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: System :: Monitoring',
        'Topic :: Utilities',
    ],
    packages=['pwatch'],
    entry_points={
        'console_scripts': [
            'pwatch = pwatch.__main__:main',
        ],
    },
    install_requires=requirements(),
)
