__author__ = 'Steven LI'

from setuptools import setup

setup(name='nose-autochecklog',
    version='0.1.0',
    description='nose plugin - auto check condition and log all checks',
    author='Steven LI',
    author_email='steven004@gmail.com',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Logging",
        "Topic :: Software Development :: Testing",
    ],
    url='https://github.com/steven004/nose-autochecklog',
    keywords='nosetest logging assert',
    entry_points={
        'nose.plugins.0.1.0': [
            'autochecklog = auto_checklog:autochecklog'
        ]
    },
    install_requires=['nose', 'test_steps>=0.5.1']
)
