# Copyright (C) 2014 Adam Schubert <adam.schubert@sg1-game.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import setuptools

version = "1.1.3"


if __name__ == "__main__":
    setuptools.setup(
        name="DwaPython",
        version=version,
        description="Python library to communicate with Divine Warfare game API",
        author="Adam Schubert",
        author_email="adam.schubert@sg1-game.net",
        url="https://github.com/Salamek/DwaPython",
        long_description=open('README.md').read(),
        packages=[
            "dwa",
            "tests"
        ],
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.5",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.2",
            "Programming Language :: Python :: 3.3",
            "Topic :: Software Development",
        ],
        test_suite="tests.AllTests"
    )
