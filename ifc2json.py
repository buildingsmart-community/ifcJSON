# IFCJSON_python - ifc2json.py
# Copyright (C) 2020 Jan Brouwer <jan@brewsky.nl>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Convert IFC SPF file to IFC.JSON-5Alpha
# https://github.com/IFCJSON-Team

from time import perf_counter
import os
import argparse
import json
from ifcjson.ifc2json4 import IFC2JSON4
from ifcjson.ifc2json5a import IFC2JSON5a
t1_start = perf_counter()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert IFC SPF file to IFC.JSON')
    parser.add_argument('-i', type=str, help='input ifc file path')
    parser.add_argument('-o', type=str, help='output json file path')
    parser.add_argument('-v', type=str, help='IFC.JSON version, options: "4"(default), "5a"')
    args = parser.parse_args()
    if args.i:
        ifcFilePath = args.i
    else:
        ifcFilePath = './samples/7m900_tue_hello_wall_with_door.ifc'
    if os.path.isfile(ifcFilePath):
        if args.o:
            jsonFilePath = args.o
        else:
            jsonFilePath = os.path.splitext(ifcFilePath)[0] + '.json'
        if not args.v or args.v == "4":
            jsonData = IFC2JSON4(ifcFilePath).spf2Json()
            with open(jsonFilePath, 'w') as outfile:
                json.dump(jsonData, outfile, indent=4)
        elif args.v == "5a":
            jsonData = IFC2JSON5a(ifcFilePath).spf2Json()
            with open(jsonFilePath, 'w') as outfile:
                json.dump(jsonData, outfile, indent=4)
        else:
            print('Version ' + args.v + ' is not supported')
    else:
        print(args.i + ' is not a valid file')
t1_stop = perf_counter()
print("Conversion took ", t1_stop-t1_start, " seconds") 