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

import os
import argparse
import ifcjson.ifc2json4 as ifc2json4
import ifcjson.ifc2json5a as ifc2json5a

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
        if args.v:
            if args.v == "4":
                ifc2json4.spf2Json(ifcFilePath, jsonFilePath)
            elif args.v == "5a":
                ifc2json5a.spf2Json(ifcFilePath, jsonFilePath)
            else:
                print('Version ' + args.v + ' is not supported')
        else:
            ifc2json4.spf2Json(ifcFilePath, jsonFilePath)
    else:
        print(args.i + ' is not a valid file')
