#-*- coding: utf-8 -*-
"""Setup script for distributing PyCraft

Typical usage scenarios can either be:
 $> python3 setup.py clean
 $> python3 setup.py sdist --format=bztar
 $> python3 setup.py register
"""

from distutils.core import setup


if __name__ == "__main__":
    setup(
        name = "PyCraft",
        version = "1503040",
        license = "CeCILL-C",
        description = "High quality Minecraft world editor",
        author = "Guillaume Lemaître",
        author_email = "guillaume.lemaitre@gmail.com",
        url = "http://github.com/seventh/PyCraft",
        packages = ["pycraft"],
        package_dir = {"pycraft": "Src"},
        data_files = [
            ("/usr/share/doc/pycraft", [
                    "Doc/AUTHORS",
                    "Doc/CHANGELOG",
                    "Doc/Licence_CeCILL-C_V1-en.txt",
                    "Doc/Licence_CeCILL-C_V1-fr.txt",
                    "README.rst",
                    ]),
            ],
        classifiers = [
            "Development Status :: 2 - Pre-Alpha",
            "Intended Audience :: Developers",
            "License :: OSI Approved",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Games/Entertainment",
            ],
        keywords = ["Minecraft"],

        )
