import json
import re

expressSchema = open("IFC4x2.exp", "r")
expressSchemaResult = open("IFC4x2-status.exp", "w")
jsonSchemaFile = open("IFC4x2.json", "w")

jsonSchema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "ifcJSON4 Schema",
    "description": "This is the schema for representing IFC4 data in JSON",
    "definitions": {
        "description": {"_comment": "This section includes IFC datatypes."},
        "ifcUnit": {
            "type": "object",
            "oneOf":[
                { "$ref": "#/properties/ifcDerivedUnit" },
                { "$ref": "#/properties/ifcNamedUnit" },
                { "$ref": "#/properties/ifcMonetaryUnit" }]
        },
        "ifcAxis2Placement":{
            "type": "object",		
            "oneOf":[
                { "$ref": "#/properties/ifcAxis2Placement2D" },
                { "$ref": "#/properties/ifcAxis2Placement3D" } 
            ]
        }
    },
    "type": "object",
    "properties": {
        "description": {"_comment": "This section includes IFC entities"}
    }
}
entity = {}
entityName = ""
properties = {}
required = []
inverse = False
where = False
derive = False
ifctype = False
ifcfunction = False

for line in expressSchema:

    # start of ENTITY section
    if line.startswith('ENTITY'):
        expressSchemaResult.write('--' + line)
        entityName = line.split(" ")[1].rstrip().replace(';', '')
        entity['$id'] = '#' + entityName
        entity['type'] = 'object'
        # entity['class'] = entityName
    
    # start of TYPE section
    elif line.startswith('TYPE'):
        expressSchemaResult.write(line)
        ifctype = True

    # start of FUNCTION section
    elif line.startswith('FUNCTION'):
        expressSchemaResult.write(line)
        ifcfunction = True

    # add subtypes using 'allOf'
    elif line.startswith(' SUBTYPE OF '):
        expressSchemaResult.write('--' + line)
        # https://github.com/json-schema-org/json-schema-spec/issues/348
        subtypeName = re.split(r'\(|\)', line)[1]
        entity['allOf'] = [{ '$ref': '#/properties/' + subtypeName }]
    elif line == ' INVERSE\n':
        expressSchemaResult.write(line)
        inverse = True
    elif line == ' WHERE\n':
        expressSchemaResult.write(line)
        where = True

    # extract properties if in ENTITY section
    elif line.startswith('\t'):
        if inverse == False and ifctype == False and ifcfunction == False and where == False:
            expressSchemaResult.write('--' + line)
            property = re.split(r'\t| : |;', line)
            propertyKey = property[1]
            propertyValue = property[2]
            if propertyValue.startswith('OPTIONAL'):
                propertyValue = propertyValue.replace('OPTIONAL ', '')
                required.append(propertyKey)
                
            propertyChild = {}

            # extract property levels
            if ' OF ' in propertyValue:
                layers = propertyValue.split(' OF ')
                for layer in layers:

                    # extract LISTS and SETS
                    if layer.startswith('LIST') or layer.startswith('SET'):
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
                            propertyChild['items'] = { '$ref': '#/properties/' + layer }
                        else:
                            print(layer)
            properties[propertyKey] = {"type" : "string"}
        else:
            expressSchemaResult.write(line)
    elif line == 'END_ENTITY;\n':
        expressSchemaResult.write('--' + line)
        if properties:
            entity['properties'] = properties
        if required:
            entity['required'] = required
        jsonSchema['properties'][entityName] = entity
        inverse = False
        where = False
        derive = False
        ifctype = False
        ifcfunction = False
        required = []
        properties = {}
        entity = {}
    elif line == 'END_TYPE;\n':
        expressSchemaResult.write(line)
        inverse = False
        where = False
        derive = False
        ifctype = False
        ifcfunction = False
    else:        
        expressSchemaResult.write(line)

json.dump(jsonSchema, jsonSchemaFile, indent=4)

jsonSchemaFile.close()
expressSchemaResult.close()
expressSchema.close()