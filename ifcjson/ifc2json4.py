# IFCJSON_python - ifc2json4.py
# Convert IFC SPF file to IFC.JSON-4
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

import os
import uuid
import functools
import ifcopenshell
import ifcopenshell.guid as guid
import ifcjson.common as common
from datetime import datetime
from ifcopenshell.entity_instance import entity_instance


class IFC2JSON4:
    maxCache = 2048

    def __init__(self, ifcModel, compact=False):
        """IFC SPF file to IFC.JSON-4 writer

        parameters:
        ifcModel: IFC filePath or ifcopenshell model instance
        compact (boolean): if True then pretty print is turned off and references are created without informative "type" property

        """
        if isinstance(ifcModel, ifcopenshell.file):
            self.ifcModel = ifcModel
        else:
            self.ifcModel = ifcopenshell.open(ifcModel)
        self.compact = compact
        self.rootObjects = {}
        self.objectDefinitions = {}
        self.ownerHistories = {}
        self.representationContexts = {}

    def spf2Json(self):
        """
        Create json dictionary structure for all attributes of the objects in the root list
        also including inverse attributes (except for IfcGeometricRepresentationContext and IfcOwnerHistory types)
        # (?) Check every IFC object to see if it is used multiple times

        Returns:
        dict: IFC.JSON-4 model structure

        """

        jsonObjects = []

        for entity in self.ifcModel.by_type('IfcOwnerHistory'):
            self.ownerHistories[entity.id()] = str(uuid.uuid4())

        for entity in self.ifcModel.by_type('IfcGeometricRepresentationContext'):
            self.representationContexts[entity.id()] = str(uuid.uuid4())

        for entity in self.ifcModel.by_type('IfcObjectDefinition'):
            self.objectDefinitions[entity.id()] = guid.split(
                guid.expand(entity.GlobalId))[1:-1]

        self.rootobjects = dict(self.ownerHistories)
        self.rootobjects.update(self.representationContexts)
        self.rootobjects.update(self.objectDefinitions)

        for key in self.rootobjects:
            entity = self.ifcModel.by_id(key)
            entityAttributes = entity.__dict__
            entityType = entityAttributes['type']
            if not entityType in ['IfcGeometricRepresentationContext', 'IfcOwnerHistory']:
                for attr in entity.wrapped_data.get_inverse_attribute_names():
                    inverseAttribute = getattr(entity, attr)
                    entityAttributes[attr] = self.getAttributeValue(
                        inverseAttribute)

            entityAttributes["GlobalId"] = self.rootobjects[entity.id()]
            jsonObjects.append(self.createFullObject(entityAttributes))

        return {
            'fileSchema': 'IFC.JSON4',
            'originatingSystem': 'IFC2JSON_python',
            'timeStamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            'data': jsonObjects
        }

    @functools.lru_cache(maxsize=maxCache)
    def getAttributeValue(self, value):
        """Recursive method that walks through all nested objects of an attribute
        and returns a IFC.JSON-4 model structure

        Parameters:
        value

        Returns:
        attribute data converted to IFC.JSON-4 model structure

        """
        if value == None or value == '':
            jsonValue = None
        elif isinstance(value, ifcopenshell.entity_instance):
            entity = value
            entityAttributes = entity.__dict__

            # All objects with a GlobalId must be referenced, all others nested
            if entity.id() in self.rootobjects:
                entityAttributes["GlobalId"] = self.rootobjects[entity.id()]
                return self.createReferenceObject(entityAttributes, self.compact)
            else:
                if 'GlobalId' in entityAttributes:
                    entityAttributes["GlobalId"] = guid.split(
                        guid.expand(entity.GlobalId))[1:-1]
            return self.createFullObject(entityAttributes)
        elif isinstance(value, tuple):
            jsonValue = None
            subEnts = []
            for subEntity in value:
                subEnts.append(self.getAttributeValue(subEntity))
            jsonValue = subEnts
        else:
            jsonValue = value
        return jsonValue

    @functools.lru_cache(maxsize=maxCache)
    def createReferenceObject(self, entityAttributes, compact=False):
        """Returns object reference

        Parameters:
        entityAttributes (dict): Dictionary of IFC object data
        compact (boolean): verbose or non verbose IFC.JSON-4 output

        Returns:
        dict: object containing reference to another object

        """
        ref = {}
        if not compact:
            ref['type'] = entityAttributes['type']
        ref['ref'] = entityAttributes['GlobalId']
        return ref

    @functools.lru_cache(maxsize=maxCache)
    def createFullObject(self, entityAttributes):
        """Returns complete IFC.JSON-4 object

        Parameters:
        entityAttributes (dict): Dictionary of IFC object data

        Returns:
        dict: containing complete IFC.JSON-4 object

        """
        entityType = entityAttributes['type']
        fullObject = {}

        for attr in entityAttributes:
            attrKey = common.toLowerCamelcase(attr)

            # Line numbers are not part of IFC JSON
            if attr == 'id':
                continue

            jsonValue = self.getAttributeValue(entityAttributes[attr])
            if jsonValue:
                fullObject[attrKey] = jsonValue
        return fullObject
