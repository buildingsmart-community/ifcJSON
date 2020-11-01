"""
IFCJSON_python - ifc2json.py
Convert ifcJSON to SPF
https://github.com/IFCJSON-Team
"""

from time import perf_counter
import os
import argparse
import json
import ifcjson

start_time = perf_counter()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert ifcJSON to SPF')
    parser.add_argument('-i', type=str, help='input json file path')
    parser.add_argument('-o', type=str, help='output ifc file path')
    args = parser.parse_args()
    if args.i:
        jsonFilePath = args.i
    if os.path.isfile(jsonFilePath):
        if args.o:
            ifcFilePath = args.o
        else:
            ifcFilePath = os.path.splitext(jsonFilePath)[0] + '.ifc'
        ifc_json = ifcjson.JSON2IFC(jsonFilePath)
        ifc_model = ifc_json.ifcModel()
        ifc_model.write(ifcFilePath)

        print("Conversion took ", perf_counter()-start_time, " seconds")
    else:
        print(str(args.i) + ' is not a valid file')
