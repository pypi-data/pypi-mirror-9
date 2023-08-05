# Copyright (C) 2011 Diego Pardilla Mata
#
#    This file is part of SpiderBOY.
#
#     SpiderBOY is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import itertools
import sys
import time

def spin():
    parts = ['|', '/', '-', '\\']

    cnt = 1
    for part in itertools.cycle(parts):
        #if cnt >= max:
        #   break
        sys.stdout.write(part)
        sys.stdout.flush()
        time.sleep(.1)
        sys.stdout.write('\b')
        cnt += 1