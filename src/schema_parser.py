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

import json
import re

expressSchema = open("IFC4x2.exp", "r")
expressSchemaResult = open("IFC4x2-status.exp", "w")
jsonSchemaFile = open("IFC4x2.json", "w")

jsonSchema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ifcJSON4 Schema",
    "description": "This is the schema for representing IFC4 data in JSON",
    "protoTypes": {
        "description": {"_comment": "This section includes IFC prototype objects without Class attribute to mimic object inheritance."}
    },
    "entities": {
        "description": {"_comment": "This section includes IFC datatypes."}
    },
    "type": "object",
    "properties": {
        "description": {"_comment": "This section includes IFC entities"},
        "data":{
            "type": "array",
            "items": {
                "anyOf": []
            },
        }
    }
}
ifcObject = {}
protoType = {}
objectName = ""
objectProperties = {}
required = []
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
        if objectName == "=":
            print(line)
        ifcObject['$id'] = '#' + objectName
        ifcObject['type'] = 'object'
        ifcObject['properties'] = {}
        ifcObject['allOf'] = [{ '$ref': '#/protoTypes/' + objectName }]

        # add prototype without class
        protoType = {
            "$id": "#" + objectName,
            "type": "object",
            "properties": {}
        }
    
    # start of TYPE section
    elif line.startswith('TYPE '):
        expressSchemaResult.write('--' + line)
        lineParts = line.split(" ")
        objectName = lineParts[1]
        if objectName == "=":
            print(line)
        ifcObject['$id'] = '#' + objectName
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
                if len(lineParts)>4:
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
                if len(lineParts)>4:
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
        protoType['allOf'] = [{ '$ref': '#/protoTypes/' + parentObjectName }]
    elif line == ' INVERSE\n':
        expressSchemaResult.write(line)
        inverse = True
    elif line == ' UNIQUE\n':
        expressSchemaResult.write(line)
        unique = True
    elif line == ' WHERE\n':
        expressSchemaResult.write(line)
        where = True

    # extract properties if in ENTITY section
    elif line.startswith('\t'):
        if inverse == False and ifcTypeSection == False and ifcfunction == False and where == False and unique == False:
            expressSchemaResult.write('--' + line)
            objectProperty = re.split(r'\t| : |;', line)
            propertyKey = objectProperty[1]
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
                        item = layer.replace('[', '').replace(']', '').split(':')
                        if item[0] != '?':
                            propertyChild['minItems'] = int(item[0])
                        if item[1] != '?':
                            propertyChild['maxItems'] = int(item[1])
                    else:
                        if layer.startswith('Ifc'):
                            propertyChild['items'] = { '$ref': '#/entities/' + layer }
                        else:
                            print(layer)
                objectProperties[propertyKey] = propertyChild
            else:
                objectProperties[propertyKey] = {'$ref': '#/entities/' + propertyValue}
        else:
            expressSchemaResult.write(line)
    elif line == 'END_ENTITY;\n':
        expressSchemaResult.write('--' + line)

        if objectProperties:
            protoType['properties'] = objectProperties
            objectProperties
        ifcObject['properties']['Class'] = {"const": objectName}

        # Add required attributes rule
        if required:
            ifcObject['required'] = required
        
        jsonSchema['entities'][objectName] = ifcObject
        jsonSchema['protoTypes'][objectName] = protoType
        jsonSchema['properties']['data']['items']['anyOf'].append({"$ref": "#/entities/" + objectName})

        # Reset object properties
        inverse = False
        unique = False
        where = False
        derive = False
        ifcTypeSection = False
        ifcfunction = False
        required = []
        objectProperties = {}
        ifcObject = {}
        protoType = {}
    elif line == 'END_TYPE;\n':
        expressSchemaResult.write('--' + line)
        jsonSchema['entities'][objectName] = ifcObject

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

json.dump(jsonSchema, jsonSchemaFile, indent=4)

jsonSchemaFile.close()
expressSchemaResult.close()
expressSchema.close()