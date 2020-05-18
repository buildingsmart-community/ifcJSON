# IFCJSON_python - ifc2json5a.py
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

# Convert IFC SPF file to IFC.JSON-5Alpha
# https://github.com/IFCJSON-Team

import os
import argparse
import json
import uuid
import subprocess
import ifcopenshell
import ifcopenshell.guid as guid
import ifcjson.common as common

# Dictionary referencing all objects with a GlobalId that are already created
id_objects = {}

# Representations are kept seperate to be added to the end of the list
representations = {}

def entityToDict(entity, objData):
    ref = {
        'type': entity.is_a()
    }
    attr_dict = entity.__dict__

    # check for globalid
    if 'GlobalId' in attr_dict:
        uuid = guid.split(guid.expand(attr_dict["GlobalId"]))[1:-1]
        ref['ref'] = uuid
        if not attr_dict['GlobalId'] in id_objects:
            d = {
                'type': entity.is_a()
            }

            for i in range(0,len(entity)):
                attr = entity.attribute_name(i)
                attrKey = common.toLowerCamelcase(attr)
                if attr == "GlobalId":
                    d[attrKey] = uuid
                else:
                    if attr in attr_dict:

                        # Skip all IFC entities that are not part of IFC.JSON5a
                        if type(attr_dict[attr]) == ifcopenshell.entity_instance:

                            # Skip IfcOwnerHistory
                            if attr_dict[attr].is_a() == 'IfcOwnerHistory':
                                continue

                            # Skip IfcGeometricRepresentationContext
                            if attr_dict[attr].is_a() == 'IfcGeometricRepresentationContext':
                                continue

                        # Use representation from OBJ list if present
                        if attr == 'Representation':
                            if objData:
                                if attr_dict['GlobalId'] in objData:
                                    id = guid.split(guid.expand(guid.new()))[1:-1]
                                    d['representations'] = [
                                        {
                                            "class": "ShapeRepresentation",
                                            "ref": id
                                        }
                                    ]
                                    representations[id] = {
                                        "class": "ShapeRepresentation",
                                        "globalId": id,
                                        "representationIdentifier": "Body",
                                        "representationType": "OBJ",
                                        "items": [
                                            objData[attr_dict['GlobalId']]
                                        ]
                                    }
                                    continue
                                else:
                                    continue


                        # Skip ObjectPlacement: all OBJ geometries are in world coordinates
                        if attr == 'ObjectPlacement':
                            continue

                        jsonValue = getEntityValue(attr_dict[attr], objData)
                        if jsonValue:
                            d[attrKey] = jsonValue
                        if attr_dict[attr] == None:
                            continue
                        elif isinstance(attr_dict[attr], ifcopenshell.entity_instance):
                            d[attrKey] = entityToDict(attr_dict[attr], objData)
                        elif isinstance(attr_dict[attr], tuple):
                            subEnts = []
                            for subEntity in attr_dict[attr]:
                                if isinstance(subEntity, ifcopenshell.entity_instance):
                                    subEntJson = entityToDict(subEntity, objData)
                                    if subEntJson:
                                        subEnts.append(subEntJson)
                                else:
                                    subEnts.append(subEntity)
                            if len(subEnts) > 0:
                                d[attrKey] = subEnts
                        else:
                            d[attrKey] = attr_dict[attr]
            id_objects[attr_dict['GlobalId']] = d
        return ref
    else:
        d = {
            'type': entity.is_a()
        }

        for i in range(0,len(entity)):
            attr = entity.attribute_name(i)
            attrKey = common.toLowerCamelcase(attr)
            if attr in attr_dict:
                if not attr == 'OwnerHistory':
                    jsonValue = getEntityValue(attr_dict[attr], objData)
                    if jsonValue:
                        d[attrKey] = jsonValue
                    if attr_dict[attr] == None:
                        continue
                    elif isinstance(attr_dict[attr], ifcopenshell.entity_instance):
                        d[attrKey] = entityToDict(attr_dict[attr], objData)
                    elif isinstance(attr_dict[attr], tuple):
                        subEnts = []
                        for subEntity in attr_dict[attr]:
                            if isinstance(subEntity, ifcopenshell.entity_instance):
                                # subEnts.append(None)
                                subEntJson = entityToDict(subEntity, objData)
                                if subEntJson:
                                    subEnts.append(subEntJson)
                            else:
                                subEnts.append(subEntity)
                        if len(subEnts) > 0:
                            d[attrKey] = subEnts
                    else:
                        d[attrKey] = attr_dict[attr]
        return d

def getEntityValue(value, objData):
    if value == None:
        jsonValue = None
    elif isinstance(value, ifcopenshell.entity_instance):
        jsonValue = entityToDict(value, objData)
    elif isinstance(value, tuple):
        jsonValue = None
        subEnts = []
        for subEntity in value:
            subEnts.append(getEntityValue(subEntity, objData))
        jsonValue = subEnts
    else:
        jsonValue = value
    return jsonValue

# convert IFC SPF file into OBJ using IfcConvert and extract OBJ objects
def getObjData(ifcFilePath):
    objFilePath = os.path.splitext(ifcFilePath)[0] + '.obj'

    # Convert IFC to OBJ using IfcConvert (could also be done for glTF or Collada)
    subprocess.run([
        './ifcopenshell/IfcConvert',
        ifcFilePath,
        objFilePath,
        '--use-element-guids'
    ])
    if os.path.isfile(objFilePath):
        objData = {}
        header = True
        groupId = ''
        groupData = []
        f = open(objFilePath, 'r')
        for line in f:

            # find group
            if line[0] == 'g':
                header = False
                objData[groupId] = '\n'.join(groupData)
                groupId = line.split()[1]
                groupData = []
            else:
                if header:
                    pass
                else:
                    groupData.append(line)
        return objData
    else:
        print('Creating intermediate OBJ failed')
        return None

def spf2Json(ifcFilePath, jsonFilePath):
    ifc_file = ifcopenshell.open(ifcFilePath)
    objData = getObjData(ifcFilePath)

    jsonObjects= []
    entityIter = iter(ifc_file)
    for entity in entityIter:
        entityToDict(entity, objData)
    for key in id_objects:
        jsonObjects.append(id_objects[key])
    for key in representations:
        jsonObjects.append(representations[key])
    with open(jsonFilePath, 'w') as outfile:
        json.dump(jsonObjects, outfile, indent=4)