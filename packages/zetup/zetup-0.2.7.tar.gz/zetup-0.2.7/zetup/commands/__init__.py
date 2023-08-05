# zetup.py
#
# Zimmermann's Python package setup.
#
# Copyright (C) 2014-2015 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# zetup.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# zetup.py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with zetup.py. If not, see <http://www.gnu.org/licenses/>.

__all__ = ['init', 'ZetupCommandError', 'ZetupMakeError']

import os

import zetup

__requires__ = zetup.__extras__['commands'].checked

from path import path as Path


class ZetupCommandError(RuntimeError):
    pass


def init(name, path=None):
    path = Path(path or os.getcwd())
    Path(__path__[0] / 'zetup.py').copy(path / '__init__.py')
    with open(path / 'zetuprc', 'w') as f:
        f.write("[%s]\n\n%s\n" % (name, "\n".join("%s =" % key for key in [
          'description',
          'author',
          'url',
          'license',
          'python',
          'classifiers',
          'keywords',
          ])))


from . import make, run, pytest, tox, conda
from .make import ZetupMakeError
