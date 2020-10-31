"""
Converts IFC EXPRESS schema into JSON-Schema
source file: "../reference_schemas/IFC4x2.exp"
target file: "../../Schema/IFC4x2-from-express.json"
status file(processed lines are prepended with --): "./IFC4x2-status.exp"
"""

import json
import os
import re


class JsonSchemaArray():
    def __init__(self, express_string):
        self.schema = {}
        self.schema["type"] = "array"
        express_string = express_string.replace('LIST ', '')
        express_string = express_string.replace('SET ', '')
        item = express_string.replace('[', '').replace(']', '').split(':')
        if item[0] != '?':
            self.schema['minItems'] = int(item[0])
        if item[1] != '?':
            self.schema['maxItems'] = int(item[1])

    def set_items(self, items):
        self.schema['items'] = items


expressSchema = open("../reference_schemas/IFC4x2.exp", "r")
expressSchemaResult = open("./IFC4x2-status.exp", "w")

schemaName = "IFC4x2"

jsonSchemaFile = open("../../Schema/" + schemaName + "-from-express.json", "w")

jsonSchema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ifcJSON4 Schema",
    "description": "This is the schema for representing IFC4 data in JSON",
    "type": "object",
    "properties": {
        "file_schema": {
            "const": "IFC.JSON4"
        },
        "data": {
            "type": "array",
            "items": {
                "anyOf": []
            },
        }
    },
    "definitions": {
    },
    "required": [
        "file_schema", "data"
    ]
}
ifcObject = {}
protoType = {}
objectName = ""
objectProperties = {}
required = []
types = []
inverse = False
unique = False
where = False
derive = False
ifcTypeSection = False
ifcfunction = False

for line in expressSchema:

    # start of ENTITY section
    if line.startswith('ENTITY'):
        expressSchemaResult.write('--' + line)
        objectName = line.split(" ")[1].rstrip().replace(';', '')

        # object names must be camelcase
        objectName = objectName[0].lower() + objectName[1:]

        if objectName == "=":
            print(line)
        # ifcObject['$id'] = '#' + objectName
        ifcObject['type'] = 'object'
        ifcObject['properties'] = {}
        ifcObject['allOf'] = [
            {'$ref': '#/definitions/' + objectName}]

        # Prevent use of custom properties
        # ifcObject['additionalProperties'] = False

        # add prototype without type
        protoType = {
            # "$id": "#" + objectName,
            "type": "object",
            "properties": {}
        }

    # start of TYPE section
    elif line.startswith('TYPE '):
        expressSchemaResult.write('--' + line)
        lineParts = line.split(" ")
        objectName = lineParts[1]

        # object names must be camelcase
        objectName = objectName[0].lower() + objectName[1:]

        if objectName == "ifcGloballyUniqueId":
            ifcObject['type'] = 'string'
            ifcObject['format'] = 'uuid'

        else:

            if objectName == "=":
                print(line)
            # ifcObject['$id'] = '#' + objectName
            if len(lineParts) > 3:
                superType = lineParts[3].rstrip().replace(';', '')
                # print(superType)
                if superType == "REAL":
                    ifcObject['type'] = 'number'
                elif superType == "INTEGER":
                    ifcObject['type'] = 'integer'
                elif superType == "BINARY":
                    ifcObject['type'] = 'string'
                elif superType == "BOOLEAN":
                    ifcObject['type'] = 'boolean'

                # LIST, LIST [(]1:?])
                elif superType == "LIST":
                    ifcObject['type'] = 'array'
                    if len(lineParts) > 4:
                        if lineParts[4].startswith("[") and lineParts[4].endswith("]"):
                            domain = re.split(r'\[|\]|\:', lineParts[4])
                            if domain[1] != "?":
                                ifcObject['minLength'] = int(domain[1])
                            if domain[2] != "?":
                                ifcObject['maxLength'] = int(domain[2])

                # SET, SET [(]1:?])
                elif superType == "SET":
                    ifcObject['type'] = 'array'
                    ifcObject['uniqueItems'] = True
                    if len(lineParts) > 4:
                        if lineParts[4].startswith("[") and lineParts[4].endswith("]"):
                            domain = re.split(r'\[|\]|\:', lineParts[4])
                            if domain[1] != "?":
                                ifcObject['minLength'] = int(domain[1])
                            if domain[2] != "?":
                                ifcObject['maxLength'] = int(domain[2])
                elif superType == "STRING":
                    ifcObject['type'] = 'string'

                # STRING, STRING(255), STRING(22) FIXED
                elif superType.startswith("STRING"):
                    ifcObject['type'] = 'string'
                    # re.sub('(<)[^>]+)', '', s)
                    stringLength = re.split(r'\(|\)', superType)[1]
                    if stringLength:
                        ifcObject['maxLength'] = int(stringLength)
                        if line.endswith("FIXED;\n"):
                            ifcObject['minLength'] = int(stringLength)
                # elif superType == "LOGICAL":
                # elif superType == "ENUMERATION":
                # elif superType == "SELECT":
            else:
                ifcObject['type'] = 'string'
        ifcTypeSection = True

    # start of FUNCTION section
    elif line.startswith('FUNCTION'):
        expressSchemaResult.write(line)
        ifcfunction = True

    # add subtypes using 'allOf'
    elif line.startswith(' SUBTYPE OF '):
        expressSchemaResult.write('--' + line)
        # https://github.com/json-schema-org/json-schema-spec/issues/348
        parentObjectName = re.split(r'\(|\)', line)[1]

        # object names must be camelcase
        parentObjectName = parentObjectName[0].lower() + parentObjectName[1:]

        protoType['allOf'] = [{'$ref': '#/definitions/' + parentObjectName}]
    elif line == ' INVERSE\n':
        expressSchemaResult.write(line)
        inverse = True
    elif line == ' UNIQUE\n':
        expressSchemaResult.write(line)
        unique = True
    elif line == ' WHERE\n':
        expressSchemaResult.write(line)
        where = True
    elif line == ' DERIVE\n':
        expressSchemaResult.write(line)
        derive = True

    # extract properties if in ENTITY section
    elif line.startswith('\t'):
        if inverse == False and ifcTypeSection == False and ifcfunction == False and where == False and unique == False and derive == False:
            expressSchemaResult.write('--' + line)
            objectProperty = re.split(r'\t| : |;', line)
            propertyKey = objectProperty[1]

            # property names must be camelcase
            propertyKey = propertyKey[0].lower() + propertyKey[1:]

            propertyValue = objectProperty[2]
            if propertyValue.startswith('OPTIONAL'):
                propertyValue = propertyValue.replace('OPTIONAL ', '')
            else:
                required.append(propertyKey)

            # extract property levels
            if ' OF ' in propertyValue:
                propertyChild = {}
                layers = propertyValue.split(' OF ')
                for layer in layers:

                    # extract LISTS and SETS
                    if layer.startswith('LIST') or layer.startswith('SET'):
                        schema_array = JsonSchemaArray(layer).schema

                        # (!) TODO This hack overwrites 'items' multiple times
                        # property names must be camelcase
                        layer_name = layers[-1][0].lower() + layers[-1][1:]
                        schema_array['items'] = {
                            '$ref': '#/definitions/' + layer_name}

                        if propertyChild:
                            propertyChild['items'] = schema_array
                        else:
                            propertyChild = schema_array

                objectProperties[propertyKey] = propertyChild
            else:

                # property names must be camelcase
                propertyValue = propertyValue[0].lower() + propertyValue[1:]

                if propertyValue == 'iNTEGER':
                    objectProperties[propertyKey] = {"type": "integer"}
                elif propertyValue == 'lOGICAL':
                    objectProperties[propertyKey] = {
                        "enum": [True, False, "UNKNOWN"]}
                elif propertyValue in types:
                    objectProperties[propertyKey] = {
                        '$ref': '#/definitions/' + propertyValue}
                else:
                    objectProperties[propertyKey] = {
                        '$ref': '#/definitions/' + propertyValue}
        else:
            expressSchemaResult.write(line)
    elif line == 'END_ENTITY;\n':
        expressSchemaResult.write('--' + line)

        if objectProperties:
            protoType['properties'] = objectProperties
            objectProperties
        ifcObject['properties']['type'] = {"const": objectName}

        # Add required attributes rule
        if required:
            protoType['required'] = required
            ifcObject['required'] = ["type"]

        jsonSchema['properties']['data']['items']['anyOf'].append(ifcObject)
        jsonSchema['definitions'][objectName] = protoType

        # Reset object properties
        inverse = False
        unique = False
        where = False
        derive = False
        ifcfunction = False
        required = []
        objectProperties = {}
        ifcObject = {}
        protoType = {}
    elif line == 'END_TYPE;\n':
        expressSchemaResult.write('--' + line)
        jsonSchema['definitions'][objectName] = ifcObject

        # collect all types for checking later on
        types.append(objectName)

        # Reset object properties
        inverse = False
        unique = False
        where = False
        derive = False
        ifcTypeSection = False
        ifcfunction = False
        objectProperties = {}
        ifcObject = {}
        protoType = {}
    else:
        expressSchemaResult.write(line)

indent = 2
json.dump(jsonSchema, jsonSchemaFile, indent=indent)
jsonSchemaFile.close()
expressSchemaResult.close()
expressSchema.close()
