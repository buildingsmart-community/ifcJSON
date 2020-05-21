# IFCJSON_python - ifc2json4.py
# Copyright (C) 2020 Jan Brouwer <jan@brewsky.nl>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Convert IFC SPF file to IFC.JSON-4
# https://github.com/IFCJSON-Team

import os
import uuid
import ifcopenshell
import ifcopenshell.guid as guid
import ifcjson.common as common

class IFC2JSON4:
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
        jsonObjects= []
        entityIter = iter(self.ifcModel)
        for entity in entityIter:
            self.entityToDict(entity)
        for key in self.id_objects:
            jsonObjects.append(self.id_objects[key])
        return jsonObjects

    def entityToDict(self, entity):
        attr_dict = entity.__dict__
        
        ref = {
            "type": entity.is_a()
        }

        # Add missing GlobalId to OwnerHistory
        if entity.is_a() == 'IfcOwnerHistory':
            if not entity.id() in self.ownerHistories:
                self.ownerHistories[entity.id()] = guid.new()
            attr_dict["GlobalId"] = self.ownerHistories[entity.id()]

        # Add missing GlobalId to IfcGeometricRepresentationContext
        if entity.is_a() == 'IfcGeometricRepresentationContext':
            if not entity.id() in self.representationContexts:
                self.representationContexts[entity.id()] = guid.new()
            attr_dict["GlobalId"] = self.representationContexts[entity.id()]

        # check for globalid
        if "GlobalId" in attr_dict:
            uuid = guid.split(guid.expand(attr_dict["GlobalId"]))[1:-1]
            ref["ref"] = uuid
            if not attr_dict["GlobalId"] in self.id_objects:
                d = {
                    "type": entity.is_a()
                }

                # Add missing GlobalId to OwnerHistory
                if entity.is_a() == 'IfcOwnerHistory':
                    d["GlobalId"] = guid.split(guid.expand(self.ownerHistories[entity.id()]))[1:-1]

                # Add missing GlobalId to IfcGeometricRepresentationContext
                if entity.is_a() == 'IfcGeometricRepresentationContext':
                    d["GlobalId"] = guid.split(guid.expand(self.representationContexts[entity.id()]))[1:-1]

                for i in range(0,len(entity)):
                    attr = entity.attribute_name(i)
                    attrKey = common.toLowerCamelcase(attr)
                    if attr == "GlobalId":
                        d[attrKey] = uuid
                    else:
                        if attr in attr_dict:
                            jsonValue = self.getEntityValue(attr_dict[attr])
                            if jsonValue:
                                if ((entity.is_a() == 'IfcOwnerHistory') and (attr == "GlobalId")):
                                    pass
                                else:
                                    d[attrKey] = jsonValue
                            if attr_dict[attr] == None:
                                continue
                            elif isinstance(attr_dict[attr], ifcopenshell.entity_instance):
                                d[attrKey] = self.entityToDict(attr_dict[attr])
                            elif isinstance(attr_dict[attr], tuple):
                                subEnts = []
                                for subEntity in attr_dict[attr]:
                                    if isinstance(subEntity, ifcopenshell.entity_instance):
                                        subEntJson = self.entityToDict(subEntity)
                                        if subEntJson:
                                            subEnts.append(subEntJson)
                                    else:
                                        subEnts.append(subEntity)
                                if len(subEnts) > 0:
                                    d[attrKey] = subEnts
                            else:
                                d[attrKey] = attr_dict[attr]
                    self.id_objects[attr_dict["GlobalId"]] = d
            return ref
        else:
            d = {
                "type": entity.is_a()
            }

            for i in range(0,len(entity)):
                attr = entity.attribute_name(i)
                attrKey = common.toLowerCamelcase(attr)
                if attr in attr_dict:
                    if not attr == "OwnerHistory":
                        jsonValue = self.getEntityValue(attr_dict[attr])
                        if jsonValue:
                            d[attrKey] = jsonValue
                        if attr_dict[attr] == None:
                            continue
                        elif isinstance(attr_dict[attr], ifcopenshell.entity_instance):
                            d[attrKey] = self.entityToDict(attr_dict[attr])
                        elif isinstance(attr_dict[attr], tuple):
                            subEnts = []
                            for subEntity in attr_dict[attr]:
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
                            d[attrKey] = attr_dict[attr]
            return d

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