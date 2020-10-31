import ifcopenshell
import json
import os

from ifcjson import IFC2JSON4
# from ifcjson import JSON2IFC

# traverse root directory, and list directories as dirs and files as files
for root, dirs, files in os.walk("../Samples/"):
    path = root.split(os.sep)
    for file in files:
        inFilePath = os.path.join(root, file)
        filename, file_extension = os.path.splitext(inFilePath)
        if file_extension.lower() == '.ifc':
            if not filename.endswith('_roundtrip'):

                # # First create normalized ifcopenshell ifc for better comparison
                # model = ifcopenshell.open(inFilePath)
                # model.write(filename + '_ifcopenshell.ifc')

                jsonFilePath = filename + '.json'
                with open(jsonFilePath, 'w') as outfile:
                    json.dump(IFC2JSON4(inFilePath).spf2Json(), outfile, indent=2)
                # with open(filename + '_python_5a.json', 'w') as outfile:
                #     json.dump(ifcjson.IFC2JSON5a(inFilePath).spf2Json(), outfile, indent=2)

                # # Convert back to SPF
                # ifc_json = JSON2IFC(jsonFilePath)
                # ifc_model = ifc_json.ifcModel()
                # ifc_model.write(filename + '_roundtrip.ifc')
