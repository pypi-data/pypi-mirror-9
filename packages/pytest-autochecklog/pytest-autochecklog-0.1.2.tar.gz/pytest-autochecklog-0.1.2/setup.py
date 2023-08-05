
from setuptools import setup

setup(
    name='pytest-autochecklog',
    description='automatically check condition and log all the checks',
    author='Steven LI',
    author_email='steven004@gmail.com',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Topic :: System :: Logging",
        "Programming Language :: Python :: 3"
    ],
    version='0.1.2',
    py_modules = ['auto_checklog'],
    entry_points = {
        'pytest11': [
            'pytest_autochecklog = auto_checklog',
        ]
    },
    install_requires = ['test_steps>=0.5.1', 'pytest'],
    url = "https://github.com/steven004/python-autochecklog",

)

