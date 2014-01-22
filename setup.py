# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup

install_requires = [
    "requests"
]

setup(name="py-zest",
    version="0.0",
    description="An experimental Python implementation of Zest",
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            ['walker-console=walker.bin.console:main']
    }
)
