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
import argparse
import json
import uuid
import ifcopenshell
import ifcopenshell.guid as guid
import ifcjson.common as common

# ifc_file = ifcopenshell.open('../samples/7m900_tue_hello_wall_with_door.ifc')
# schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(ifc_file.schema)
id_objects = {}

# Create dictionary of OwnerHistory objects
ownerHistories = {}

# Create dictionary of IfcGeometricRepresentationContext objects
representationContexts = {}

def entityToDict(entity):
    attr_dict = entity.__dict__
    
    ref = {
        "type": entity.is_a()
    }

    # Add missing GlobalId to OwnerHistory
    if entity.is_a() == 'IfcOwnerHistory':
        if not entity.id() in ownerHistories:
            ownerHistories[entity.id()] = guid.new()
        attr_dict["GlobalId"] = ownerHistories[entity.id()]

    # Add missing GlobalId to IfcGeometricRepresentationContext
    if entity.is_a() == 'IfcGeometricRepresentationContext':
        if not entity.id() in representationContexts:
            representationContexts[entity.id()] = guid.new()
        attr_dict["GlobalId"] = representationContexts[entity.id()]

    # check for globalid
    if "GlobalId" in attr_dict:
        uuid = guid.split(guid.expand(attr_dict["GlobalId"]))[1:-1]
        ref["ref"] = uuid
        if not attr_dict["GlobalId"] in id_objects:
            d = {
                "type": entity.is_a()
            }

            # Add missing GlobalId to OwnerHistory
            if entity.is_a() == 'IfcOwnerHistory':
                d["GlobalId"] = guid.split(guid.expand(ownerHistories[entity.id()]))[1:-1]

            # Add missing GlobalId to IfcGeometricRepresentationContext
            if entity.is_a() == 'IfcGeometricRepresentationContext':
                d["GlobalId"] = guid.split(guid.expand(representationContexts[entity.id()]))[1:-1]

            for i in range(0,len(entity)):
                attr = entity.attribute_name(i)
                attrKey = common.toLowerCamelcase(attr)
                if attr == "GlobalId":
                    d[attrKey] = uuid
                else:
                    if attr in attr_dict:
                        jsonValue = getEntityValue(attr_dict[attr])
                        if jsonValue:
                            if ((entity.is_a() == 'IfcOwnerHistory') and (attr == "GlobalId")):
                                pass
                            else:
                                d[attrKey] = jsonValue
                        if attr_dict[attr] == None:
                            continue
                        elif isinstance(attr_dict[attr], ifcopenshell.entity_instance):
                            d[attrKey] = entityToDict(attr_dict[attr])
                        elif isinstance(attr_dict[attr], tuple):
                            subEnts = []
                            for subEntity in attr_dict[attr]:
                                if isinstance(subEntity, ifcopenshell.entity_instance):
                                    subEntJson = entityToDict(subEntity)
                                    if subEntJson:
                                        subEnts.append(subEntJson)
                                else:
                                    subEnts.append(subEntity)
                            if len(subEnts) > 0:
                                d[attrKey] = subEnts
                        else:
                            d[attrKey] = attr_dict[attr]
                id_objects[attr_dict["GlobalId"]] = d
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
                    jsonValue = getEntityValue(attr_dict[attr])
                    if jsonValue:
                        d[attrKey] = jsonValue
                    if attr_dict[attr] == None:
                        continue
                    elif isinstance(attr_dict[attr], ifcopenshell.entity_instance):
                        d[attrKey] = entityToDict(attr_dict[attr])
                    elif isinstance(attr_dict[attr], tuple):
                        subEnts = []
                        for subEntity in attr_dict[attr]:
                            if isinstance(subEntity, ifcopenshell.entity_instance):
                                # subEnts.append(None)
                                subEntJson = entityToDict(subEntity)
                                if subEntJson:
                                    subEnts.append(subEntJson)
                            else:
                                subEnts.append(subEntity)
                        if len(subEnts) > 0:
                            d[attrKey] = subEnts
                    else:
                        d[attrKey] = attr_dict[attr]
        return d

def getEntityValue(value):
    if value == None:
        jsonValue = None
    elif isinstance(value, ifcopenshell.entity_instance):
        jsonValue = entityToDict(value)
    elif isinstance(value, tuple):
        jsonValue = None
        subEnts = []
        for subEntity in value:
            subEnts.append(getEntityValue(subEntity))
        jsonValue = subEnts
    else:
        jsonValue = value
    return jsonValue


# jsonObjects= []
# entityIter = iter(ifc_file)
# for entity in entityIter:
#     entityToDict(entity)
# for key in id_objects:
#     jsonObjects.append(id_objects[key])
# with open('../7m900_tue_hello_wall_with_door.json', 'w') as outfile:
#     json.dump(jsonObjects, outfile, indent=4)

def spf2Json(ifcFilePath, jsonFilePath):
    ifc_file = ifcopenshell.open(ifcFilePath)

    jsonObjects= []
    entityIter = iter(ifc_file)
    for entity in entityIter:
        entityToDict(entity)
    for key in id_objects:
        jsonObjects.append(id_objects[key])
    with open(jsonFilePath, 'w') as outfile:
        json.dump(jsonObjects, outfile, indent=4)
