"""
Converts IFC EXPRESS schema into JSON-Schema
source file: "../reference_schemas/IFC4x2.exp"
target file: "../../Schema/IFC4x2-from-express.json"
status file(processed lines are prepended with --): "./IFC4x2-status.exp"
"""

import copy
import json
import logging
import os
import re

logging.basicConfig(level=logging.DEBUG,
                    filename='schema_parser.log', filemode='w')

JSONSCHEMA_CORE_TYPES = ["number", "integer", "string", "boolean"]


class IfcBaseObject:

    def definition_reference(self, name):
        """ JSON Schema definition name into reference object

        Parameters:
        name (str): JSON Schema definition name

        Returns:
        dict: JSON Schema reference object

        """

        return {
            "$ref": "#/definitions/" + name
        }

    def get_json_type(self, express_type, ifc_objects):
        """ Convert EXPRESS type name string into JSON Schema type

        Parameters:
        express_type (str): EXPRESS type name string
        ifc_objects (dict): dictionary containing all IFC objects in the schema

        Returns:
        dict: JSON Schema type

        """

        schema = {}
        if self.objectName == "IfcGloballyUniqueId":
            schema['type'] = 'string'
            schema['format'] = 'uuid'
        elif express_type.lower() in JSONSCHEMA_CORE_TYPES:
            schema["type"] = express_type.lower()
        elif express_type == "REAL":
            schema["type"] = 'number'
        elif express_type == "BINARY":
            schema["type"] = 'string'
        elif express_type == 'LOGICAL':
            schema["type"] = 'string'
            schema["enum"] = [True, False, "UNKNOWN"]
        elif express_type == 'STRING(255)':
            schema["type"] = 'string'
            schema['maxLength'] = 255
        elif express_type in ifc_objects:
            schema = self.definition_reference(express_type)
        elif express_type == "IfcPropertySetDefinition":
            schema = self.definition_reference(express_type)
        elif express_type.startswith("SELECT"):
            select_type_names = express_type[6:].strip().strip(
                "()").split("\r\n\t,")
            select_type_names_and_supertypes = select_type_names

            # Add supertypes to the list
            for select_type_name in select_type_names:
                if type(ifc_objects[select_type_name]) == Entity:
                    select_type_names_and_supertypes += ifc_objects[select_type_name].supertypes

            select_types = list(
                map(lambda x: self.definition_reference(x), select_type_names_and_supertypes))
            return {"anyOf": select_types}
        else:
            logging.debug(f"Missing type: {express_type}")

        return schema

    def jsonschema_array(self, express_string):
        """ Convert EXPRESS LIST, SET or ARRAY into JSON Schema Array

        Parameters:
        express_string (str): EXPRESS schema LIST, SET or ARRAY

        Returns:
        dict: JSON Schema Array

        """

        schema = {}
        schema["type"] = "array"
        express_string = express_string.replace('LIST ', '')
        express_string = express_string.replace('SET ', '')
        express_string = express_string.replace('ARRAY ', '')
        item = express_string.replace('[', '').replace(']', '').split(':')
        if item[0] != '?':
            schema['minItems'] = int(item[0])
        if item[1] != '?':
            schema['maxItems'] = int(item[1])
        return schema


class Type(IfcBaseObject):
    def __init__(self, object_lines):
        """ Creates an ifcJSON Type object from EXPRESS schema TYPE definition

        Parameters:
        object_lines (str): EXPRESS schema TYPE definition

        """

        line_parts = object_lines[0].strip().rstrip(";").split(" = ")
        key_parts = line_parts[0].split(" ")
        self.value_parts = line_parts[1].split(" OF")
        self.objectName = key_parts[1]

    def to_json(self, ifc_objects):
        express_type = self.value_parts[-1].strip()
        if len(self.value_parts) == 1:

            # Create option to check a direct value and an inline value object
            schema = {"oneOf": [
                self.get_json_type(express_type, ifc_objects),
                {
                    "type": "object",
                    "properties": {
                        "type": {
                            "const": self.objectName
                        },
                        "value": self.get_json_type(express_type, ifc_objects)
                    },
                    "required": [
                        "type",
                        "value"
                    ]
                }

            ]}
            return schema
        else:
            if self.value_parts[0] == "ENUMERATION":  # ENUMERATION
                return {
                    "type": "string",
                    "enum": self.value_parts[1].strip().strip("()").split("\r\n\t,")
                }
            else:  # LIST, ARRAY and SET
                schema = self.jsonschema_array(self.value_parts[0].strip())
                schema["items"] = self.get_json_type(express_type, ifc_objects)
                return schema


class Entity(IfcBaseObject):
    def __init__(self, object_lines):
        self.object_lines = object_lines
        header_line = object_lines[0]
        self.subtype = None
        self.required = []
        self.supertypes = []

        # Remove ABSTRACT
        header_line = header_line.replace("\r\n ABSTRACT", "")

        supertypes_string = re.search(
            'SUPERTYPE OF \(ONEOF\r\n    \((.+?)\)\)', header_line, flags=re.DOTALL)
        if supertypes_string:
            self.supertypes = list(
                map(lambda x: x.strip(), supertypes_string.group(1).split(",")))

        # Remove SUPERTYPE
        header_line = re.sub('SUPERTYPE OF \(ONEOF\r\n.*?\)\)',
                             '', header_line, flags=re.DOTALL)

        line_parts = header_line.split(" ")
        if "SUBTYPE" in line_parts:
            self.subtype = line_parts[-1].rstrip(";").strip("()")
        self.objectName = line_parts[1].strip().rstrip(";")

        self.properties = {'type': {"const": self.objectName}}

    def add_property(self, property_line, ifc_objects, inverse):
        property_parts = property_line.split(" : ")
        name = property_parts[0].strip()
        name = name[0].lower() + name[1:]
        property_type = property_parts[1].strip()
        if property_type.startswith("OPTIONAL"):
            property_type = property_type.replace("OPTIONAL ", "")
        else:
            if not inverse:
                self.required.append(name)

        type_parts = property_type.split(" OF")
        express_type = type_parts[-1].strip().rstrip(";")

        # Remove FOR
        express_type_parts = express_type.split(" FOR ")
        if len(express_type_parts) > 1:
            express_type = express_type_parts[0]

        if len(type_parts) == 1:
            self.properties[name] = self.get_json_type(
                express_type, ifc_objects)
        else:
            schema = self.jsonschema_array(type_parts[0].strip())
            schema["items"] = self.get_json_type(express_type, ifc_objects)
            self.properties[name] = schema

    def set_properties(self, ifc_objects):

        i = 1
        inverse = False
        while i < len(self.object_lines):
            object_line = self.object_lines[i]
            if object_line.startswith("INVERSE"):
                # break
                object_line = object_line.replace("INVERSE\r\n\t", "")
                inverse = True

            # Skip WHERE rules
            if object_line.startswith("UNIQUE"):
                break

            # Skip WHERE rules
            if object_line.startswith("WHERE"):
                break

            # Skip Derived attributes
            if object_line.startswith("DERIVE"):
                break
            self.add_property(object_line, ifc_objects, inverse)
            i += 1

    def get_required(self, ifc_objects):
        if self.subtype:
            return self.required + ifc_objects[self.subtype].get_required(ifc_objects)
        else:
            return self.required

    def get_properties(self, ifc_objects):
        if self.subtype:
            subtype_properties = ifc_objects[self.subtype].get_properties(
                ifc_objects)
            if subtype_properties:
                subtype_properties.update(self.properties)
                return copy.deepcopy(subtype_properties)
            else:
                return copy.deepcopy(self.properties)
        else:
            return copy.deepcopy(self.properties)

    def entity_inheritance_reference(self, name):
        return {
            "$ref": "#/entityInheritance/" + name
        }

    def properties_definition(self, ifc_objects):
        return self.definition_reference(self.objectName)

    def definition(self, ifc_objects):
        definition = {
            'type': 'object',
            'properties': self.get_properties(ifc_objects)
        }

        # Set required attributes
        # definition['required'] = ['type'] + self.get_required(ifc_objects)

        # Prevent use of custom properties
        # definition['additionalProperties'] = False

        # Include supertypes
        if self.supertypes:
            definitionlist = list(
                map(lambda x: self.definition_reference(x), self.supertypes))
            definitionlist.append({
                'type': 'object',
                'properties': self.get_properties(ifc_objects)
            })
            definition = {"anyOf": definitionlist}

        return definition

    def entity_definition(self, ifc_objects):
        definition = {
            'type': 'object'
        }
        # if self.properties:
        #     definition['properties'] = self.properties
        if self.subtype:
            definition['allOf'] = [
                self.entity_inheritance_reference(self.subtype)]
        required = self.get_required(ifc_objects)
        if required:
            definition['required'] = self.get_required(ifc_objects)

        # # Prevent use of custom properties
        # definition['additionalProperties'] = False
        return definition


class JsonSchema:
    def __init__(self, express_path):
        self.schema_version = "None"
        self.properties = []
        self.types = {}
        self.entities = {}
        self.ifc_objects = self.parse_file(express_path)

        # Set properties can only be done after all entities are present in the list
        self.set_properties()

    def to_file(self, json_file_path):
        with open(json_file_path, 'w') as json_file:
            json_schema = {
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "ifcJSON " + self.schema_version + " Schema",
                "description": "This is the schema for representing " + self.schema_version + " data in JSON",
                "type": "object",
                "properties": {
                    "type": {
                        "const": "ifcJSON"
                    },
                    "version": {
                        "type": "string"
                    },
                    "schemaIdentifier": {
                        "type": "string"
                    },
                    "originatingSystem": {
                        "type": "string"
                    },
                    "preprocessorVersion": {
                        "type": "string"
                    },
                    "timeStamp": {
                        "type": "string",
                        "format": "date-time"
                    },
                    "data": {
                        "type": "array",
                        "items": {
                            "anyOf": self.get_properties()
                        },
                    }
                },
                "definitions": self.get_definitions(),
                "required": [
                    "type", "data"
                ]
            }
            json.dump(json_schema, json_file, indent=2)

    def set_properties(self):
        objects = []
        for key in self.ifc_objects:
            ifc_object = self.ifc_objects[key]
            if type(ifc_object) is Entity:
                ifc_object.set_properties(self.ifc_objects)

    def get_properties(self):
        objects = []
        for key in self.ifc_objects:
            ifc_object = self.ifc_objects[key]
            if type(ifc_object) is Entity:
                objects.append(
                    ifc_object.properties_definition(self.ifc_objects))
        return objects

    def get_definitions(self):
        definitions = {}
        for key in self.ifc_objects:
            ifc_object = self.ifc_objects[key]
            if type(ifc_object) is Entity:
                definitions[ifc_object.objectName] = ifc_object.definition(
                    self.ifc_objects)
            elif type(ifc_object) is Type:
                definitions[ifc_object.objectName] = ifc_object.to_json(
                    self.ifc_objects)
        return definitions

    def parse_file(self, express_path):
        ifc_objects = {}
        object_lines = []
        ifc_object = None
        f = open(express_path, "rb")
        byte = f.read(1)
        i = 0

        # Mark end of header section
        while byte:
            byte = f.read(1)
            i += 1
            if byte == b')':

                # Assume there is an empty line between header and SCHEMA
                byte = f.read(4)
                i += 4
                break

        blocks = [i]
        j = i

        while byte:
            byte = f.read(1)
            j += 1
            if byte == b';':
                blocks.append(j+2)  # Add end of line

        # Reset read pointer
        f.seek(i+1)

        i = 0
        while i < len(blocks)-1:
            line = f.read(blocks[i+1] - blocks[i]).decode().strip()
            if line.startswith('SCHEMA'):
                self.schema_version = line.split(" ")[1].strip().rstrip(";")

            # Group all lines that belong to a single TYPE or ENTITY
            elif line.startswith('TYPE'):
                object_lines = [line]
            elif line.startswith('END_TYPE'):
                object = Type(object_lines)
                ifc_objects[object.objectName] = object
            elif line.startswith('ENTITY'):
                object_lines = [line]
            elif line.startswith('END_ENTITY'):
                object = Entity(object_lines)
                ifc_objects[object.objectName] = object

            # No support for FUNCTION and RULE for now
            elif line.startswith('FUNCTION'):
                break
            elif line.startswith('END_FUNCTION'):
                break
            elif line.startswith('RULE'):
                break
            elif line.startswith('END_RULE'):
                break
            else:
                object_lines.append(line)
            i += 1
        f.close()
        return ifc_objects


def main():
    express_file_path = "./reference_schemas/IFC4.exp"
    json_schema = JsonSchema(express_file_path)
    json_file_path = f"./../Schema/{json_schema.schema_version}.json"
    json_schema.to_file(json_file_path)


if __name__ == "__main__":
    main()
