from setuptools import setup

setup(
    name="threeflex",
    version="0.1.0",
    description="Python driver for Micromeritics 3Flex surface "
                "characterization analyzers.",
    url="http://github.com/numat/threeflex/",
    author="Patrick Fuller",
    author_email="pat@numat-tech.com",
    packages=["threeflex"],
    install_requires=[],
    entry_points={
        "console_scripts": [("threeflex = threeflex:command_line")]
    },
    license="GPLv2",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)"
    ]
)
