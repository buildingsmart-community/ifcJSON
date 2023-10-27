import json
import os
from jsonschema import validate, ValidationError, SchemaError

schema_file_path = "../Schema/IFC4.json"

with open(schema_file_path, "r") as schema_file:
    schema = json.load(schema_file)

    # traverse root directory, and list directories as dirs and files as files
    for root, dirs, files in os.walk("../Samples/IFC_4.0"):
        path = root.split(os.sep)
        for file in files:
            json_file_path = os.path.join(root, file)
            filename, file_extension = os.path.splitext(json_file_path)
            if file_extension.lower() == '.json':
                with open(json_file_path, "r") as json_file:
                    instance = json.load(json_file)
                    try:
                        validate(instance, schema)
                        print(f"{json_file_path} is valid ifcJSON")
                    except SchemaError as e:
                        print("There is an error with the schema")
                    except ValidationError as e:
                        print(f"{json_file_path} is NOT valid ifcJSON!")
                        print(e)
                        print(e.message)

                    # Function that returns a iterator with all the dicts from each IFC type in the data
                    def get_all_ifc_types(data):
                        if isinstance(data, dict):
                            yield data
                            for key, value in data.items():
                                if isinstance(value, dict):
                                    yield from get_all_ifc_types(value)
                                elif isinstance(value, list):
                                    for element in value:
                                        yield from get_all_ifc_types(element)
                        elif isinstance(data, list):
                            for element in data:
                                yield from get_all_ifc_types(element)

                    # For each IFC type inside each IFC instance of 'instance', the parameters' names are evaluated
                    for ifc_instance in get_all_ifc_types(instance['data']):
                        # Get the IFC 'type'
                        ifc_type = ifc_instance['type']
                        
                        # Get all the keys (or parameters) of a given IFC type in the original schema
                        try:
                            keys = list(schema['definitions'][ifc_type].keys())
                        except:
                            print(f'Error in retrieving the IFC parameters (or json keys) from "{json_file_path}"')

                        # Differentiate between the IfcJSON structures to get the adequate 'properties' keys
                        if keys == ['oneOf']:
                            schema_parameters = schema['definitions'][ifc_type]['oneOf'][1]['properties'].keys()
                        else:
                            schema_parameters = schema['definitions'][ifc_type]['properties'].keys()

                        # Check if the parameter name of the validated file is in the ifc schema parameters
                        for validated_parameter in ifc_instance.keys():
                            if validated_parameter == 'ref':
                                continue
                            elif validated_parameter in schema_parameters:
                                pass
                            else:
                                raise ValueError(f'The parameter "{validated_parameter}" in {ifc_instance}, file "{json_file_path}", does not exists in the original schema! \nCheck if any of the following can be used instead: {list(schema_parameters)}.')
