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