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


class IFC2JSON4:
    maxCache = 2048

    def __init__(self, ifcFilePath):
        self.ifcFilePath = ifcFilePath
        self.ifcModel = ifcopenshell.open(ifcFilePath)

        # Dictionary referencing all objects with a GlobalId that are already created
        self.id_objects = {}

        # Create dictionary of OwnerHistory objects
        self.ownerHistories = {}

        # Create dictionary of IfcGeometricRepresentationContext objects
        self.representationContexts = {}

    def spf2Json(self):
        jsonObjects = []
        entityIter = iter(self.ifcModel)
        for entity in entityIter:
            self.entityToDict(entity)
        for key in self.id_objects:
            jsonObjects.append(self.id_objects[key])
        return {
            'file_schema': 'IFC.JSON4',
            'originatingSystem': 'IFC2JSON_python',
            'data': jsonObjects
        }

    @functools.lru_cache(maxsize=maxCache)
    def entityToDict(self, entity):

        # Entity names must be in camelCase
        entityType = common.toLowerCamelcase(entity.is_a())

        entityAttributes = entity.__dict__

        ref = {
            "type": entityType
        }

        # Add missing GlobalId to OwnerHistory
        if entityType == 'ifcOwnerHistory':
            if not entity.id() in self.ownerHistories:
                self.ownerHistories[entity.id()] = guid.new()
            entityAttributes["GlobalId"] = self.ownerHistories[entity.id()]

        # Add missing GlobalId to IfcGeometricRepresentationContext
        if entityType == 'ifcGeometricRepresentationContext':
            if not entity.id() in self.representationContexts:
                self.representationContexts[entity.id()] = guid.new()
            entityAttributes["GlobalId"] = self.representationContexts[entity.id()]

        # All objects with a GlobalId must be referenced, all others nested
        if "GlobalId" in entityAttributes:
            uuid = guid.split(guid.expand(entityAttributes["GlobalId"]))[1:-1]
            ref["ref"] = uuid

            # Every object must be added to the root array only once
            if not entityAttributes["GlobalId"] in self.id_objects:
                d = {
                    "type": entityType
                }

                # Add missing GlobalId to OwnerHistory
                if entityType == 'ifcOwnerHistory':
                    d["globalId"] = guid.split(guid.expand(
                        self.ownerHistories[entity.id()]))[1:-1]

                # Add missing GlobalId to IfcGeometricRepresentationContext
                if entityType == 'ifcGeometricRepresentationContext':
                    d["globalId"] = guid.split(guid.expand(
                        self.representationContexts[entity.id()]))[1:-1]

                # Inverse attributes must be added if not OwnerHistory or GeometricRepresentationContext
                if not entityType in ['ifcGeometricRepresentationContext', 'ifcOwnerHistory']:
                    for attr in entity.wrapped_data.get_inverse_attribute_names():
                        inverseAttribute = getattr(entity, attr)
                        
                        # print(attr)
                        # d[attrKey] = {
                        #     "type": attr.Name,
                        #     "ref": "guid"
                        # }
                        # print(inverseAttribute)
                        if isinstance(inverseAttribute, tuple):
                            for attribute in inverseAttribute:
                                attrKey = common.toLowerCamelcase(attribute.is_a())
                                # print(dir(attribute))
                                d[attr] = {
                                    'type': attrKey
                                }
                                if 'GlobalId' in dir(attribute):
                                    d[attr]['ref'] = guid.split(guid.expand(attribute.GlobalId))[1:-1]
                                else:
                                    print(entityType + ' has no GlobalId for referencing!')

                for attr in entityAttributes:
                    attrKey = common.toLowerCamelcase(attr)
                    if attr == "GlobalId":
                        d[attrKey] = uuid
                    else:

                        # Line numbers are not part of IFC JSON
                        if attr == 'id':
                            continue

                        jsonValue = self.getEntityValue(entityAttributes[attr])
                        if jsonValue:
                            if ((entityType == 'ifcOwnerHistory') and (attr == "GlobalId")):
                                pass
                            else:
                                d[attrKey] = jsonValue
                        if entityAttributes[attr] == None:
                            continue
                        elif isinstance(entityAttributes[attr], ifcopenshell.entity_instance):
                            d[attrKey] = self.entityToDict(
                                entityAttributes[attr])
                        elif isinstance(entityAttributes[attr], tuple):
                            subEnts = []
                            for subEntity in entityAttributes[attr]:
                                if isinstance(subEntity, ifcopenshell.entity_instance):
                                    subEntJson = self.entityToDict(subEntity)
                                    if subEntJson:
                                        subEnts.append(subEntJson)
                                else:
                                    subEnts.append(subEntity)
                            if len(subEnts) > 0:
                                d[attrKey] = subEnts
                        else:
                            d[attrKey] = entityAttributes[attr]
                    self.id_objects[entityAttributes["GlobalId"]] = d
            return ref
        else:
            d = {
                "type": entityType
            }

            for i in range(0, len(entity)):
                attr = entity.attribute_name(i)
                attrKey = common.toLowerCamelcase(attr)
                if attr in entityAttributes:
                    if not attr == "OwnerHistory":
                        jsonValue = self.getEntityValue(entityAttributes[attr])
                        if jsonValue:
                            d[attrKey] = jsonValue
                        if entityAttributes[attr] == None:
                            continue
                        elif isinstance(entityAttributes[attr], ifcopenshell.entity_instance):
                            d[attrKey] = self.entityToDict(
                                entityAttributes[attr])
                        elif isinstance(entityAttributes[attr], tuple):
                            subEnts = []
                            for subEntity in entityAttributes[attr]:
                                if isinstance(subEntity, ifcopenshell.entity_instance):
                                    # subEnts.append(None)
                                    subEntJson = self.entityToDict(subEntity)
                                    if subEntJson:
                                        subEnts.append(subEntJson)
                                else:
                                    subEnts.append(subEntity)
                            if len(subEnts) > 0:
                                d[attrKey] = subEnts
                        else:
                            d[attrKey] = entityAttributes[attr]
            return d

    @functools.lru_cache(maxsize=maxCache)
    def getEntityValue(self, value):
        if value == None:
            jsonValue = None
        elif isinstance(value, ifcopenshell.entity_instance):
            jsonValue = self.entityToDict(value)
        elif isinstance(value, tuple):
            jsonValue = None
            subEnts = []
            for subEntity in value:
                subEnts.append(self.getEntityValue(subEntity))
            jsonValue = subEnts
        else:
            jsonValue = value
        return jsonValue
