# IFCJSON_python - ifc2json.py
# Convert IFC SPF file to IFC.JSON
# https://github.com/IFCJSON-Team

# MIT License

# Copyright (c) 2020 Jan Brouwer <jan@brewsky.nl>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from time import perf_counter
import os
import argparse
import json
import ifcjson
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
            jsonData = ifcjson.IFC2JSON4(ifcFilePath).spf2Json()
            with open(jsonFilePath, 'w') as outfile:
                json.dump(jsonData, outfile, indent=4)
        elif args.v == "5a":
            jsonData = ifcjson.IFC2JSON5a(ifcFilePath).spf2Json()
            with open(jsonFilePath, 'w') as outfile:
                json.dump(jsonData, outfile, indent=4)
        else:
            print('Version ' + args.v + ' is not supported')
    else:
        print(args.i + ' is not a valid file')
t1_stop = perf_counter()
print("Conversion took ", t1_stop-t1_start, " seconds") 