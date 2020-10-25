# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import json
import re

# expressSchemaPath = "../"
# schemaName = "IFC4x2"
# expressSchema = open(os.path.join(expressSchemaPath, schemaName + ".exp"), "r")
# expressSchemaResult = open(os.path.join(expressSchemaPath, schemaName + ".exp"), "w")

# schemaName = schemaName + "_2"

expressSchema = open("./IFC4x2.exp", "r")
expressSchemaResult = open("./IFC4x2-status.exp", "w")
print(expressSchema)

schemaName = "IFC4x2"
schemaNameType = schemaName + "-types"
schemaNameEntities = schemaName + "-entities"

jsonSchemaFile = open(schemaName + ".json", "w")
jsonSchemaFileTypes = open(schemaNameType + ".json", "w")
jsonSchemaFileEntities = open(schemaNameEntities + ".json", "w")

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
    "required": [
        "file_schema", "data"
    ]
}
jsonSchemaTypes = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ifcJSON4 Schema",
    "description": "This is the subschema for IFC.JSON4 containing all IFC TYPES",
    "definitions": {
    }
}
jsonSchemaEntities = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ifcJSON4 Schema",
    "description": "This is the subschema for IFC.JSON4 containing all IFC ENTITIES",
    "definitions": {
    }
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
            {'$ref': 'entities#/definitions/' + objectName}]

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
                        print(line)
                        propertyChild["type"] = "array"
                        layer = layer.replace('LIST ', '')
                        layer = layer.replace('SET ', '')
                        item = layer.replace(
                            '[', '').replace(']', '').split(':')
                        if item[0] != '?':
                            propertyChild['minItems'] = int(item[0])
                        if item[1] != '?':
                            propertyChild['maxItems'] = int(item[1])
                    else:

                        # property names must be camelcase
                        layer = layer[0].lower() + layer[1:]
                        # if layer.startswith('Ifc'):
                        #     propertyChild['items'] = { '$ref': 'types#/definitions/' + layer }
                        # else:
                        #     print(layer)
                        if layer in types:
                            propertyChild['items'] = {
                                '$ref': 'types#/definitions/' + layer}
                        else:
                            propertyChild['items'] = {
                                '$ref': '#/definitions/' + layer}
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
                        '$ref': 'types#/definitions/' + propertyValue}
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
        # jsonSchemaEntities['definitions'][objectName] = ifcObject
        jsonSchemaEntities['definitions'][objectName] = protoType
        # jsonSchema['properties']['data']['items']['anyOf'].append({"$ref": "entities#/definitions/" + objectName})

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
        jsonSchemaTypes['definitions'][objectName] = ifcObject

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
json.dump(jsonSchema, jsonSchemaFile, indent=2)
json.dump(jsonSchemaTypes, jsonSchemaFileTypes, indent=indent)
json.dump(jsonSchemaEntities, jsonSchemaFileEntities, indent=indent)
jsonSchemaFile.close()
jsonSchemaFileEntities.close()
expressSchemaResult.close()
expressSchema.close()
