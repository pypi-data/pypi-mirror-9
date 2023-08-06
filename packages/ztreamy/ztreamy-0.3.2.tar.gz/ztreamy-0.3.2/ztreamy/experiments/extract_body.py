# ztreamy: a framework for publishing semantic events on the Web
# Copyright (C) 2011-2013 Jesus Arias Fisteus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
from __future__ import print_function
from __future__ import division

import gzip

from ztreamy import Deserializer

def extract_bodys(input_filename, output_filename):
    with gzip.GzipFile(input_filename, mode='rb') as input_f:
        with gzip.GzipFile(output_filename, mode='wb') as output_f:
            deserializer = Deserializer()
            while True:
                data = input_f.read(16384)
                if data == '':
                    break
                events = deserializer.deserialize(data, parse_body=False,
                                                  complete=False)
                for event in events:
                    body = event.serialize_body()
                    output_f.write(str(len(body)))
                    output_f.write('\n')
                    output_f.write(body)
                    output_f.write('\n')

def main():
    import sys
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    extract_bodys(input_filename, output_filename)

if __name__ == "__main__":
    main()
