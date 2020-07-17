# IFCJSON_python - ifc2json5a.py
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
from tempfile import NamedTemporaryFile
import subprocess
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid as guid
import ifcjson.common as common
import copy
from datetime import datetime


explicitInverseAttributes = {
    'IsDecomposedBy',
    'HasAssociations',
    'IsDefinedBy',
    'HasOpenings',
    'ContainsElements'
}


class IFC2JSON5a:
    def __init__(self, ifcFilePath):
        self.ifcFilePath = ifcFilePath
        self.ifcModel = ifcopenshell.open(ifcFilePath)

        # Dictionary referencing all objects with a GlobalId that are already created
        self.id_objects = {}

        # Representations are kept seperate to be added to the end of the list
        self.representations = {}

    def spf2Json(self):
        objData = self.getObjData(self.ifcFilePath)
        jsonObjects = []
        # entityIter = iter(self.ifcModel)
        # for entity in entityIter:
        #     # print(dir(entity))
        #     # print("test")
        #     # print(getitem(entity))
        #     self.entityToDict(entity, objData)
        for entity in self.ifcModel.by_type('IfcProject'):
            self.entityToDict(entity, objData)
        for key in self.id_objects:
            jsonObjects.append(self.id_objects[key])
        for key in self.representations:
            jsonObjects.append(self.representations[key])
        return {
            'fileSchema': 'IFC.JSON5a',
            'originatingSystem': 'IFC2JSON_python',
            'timeStamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            'data': jsonObjects
            }

    def entityToDict(self, entity, objData, parent=None):
        settings = ifcopenshell.geom.settings()
        # print(ifcopenshell.geom.create_shape(settings, entity))
        print(dir(ifcopenshell.geom))
        print(dir(ifcopenshell.geom.serialise(settings, entity)))

        # Entity names must be stripped of Ifc prefix
        entityType = entity.is_a()[3:]

        entityAttributes = entity.__dict__
        # inverseAttributes = explicitInverseAttributes.intersection(entity.wrapped_data.get_inverse_attribute_names())
        
        ref = {
            'type': entityType
        }

        # All objects with a GlobalId must be referenced, all others nested
        reference = False
        if 'GlobalId' in entityAttributes:
            reference = True
        if entity.is_a == 'IfcRelAggregates':
            reference = False

        d = {
            'type': entityType
        }

        # for inverseAttribute in inverseAttributes:
        #     invAtt = {}
        #     attributeObject = getattr(entity, inverseAttribute)
        #     attr = inverseAttribute
        #     attrKey = common.toLowerCamelcase(attr)
        #     print(attributeObject)

        #     if isinstance(attributeObject, ifcopenshell.entity_instance):
        #         print("dsicnkjcnkdjvnskjcnkvjnfjkn")
        #         # if attributeObject.is_a == 'IfcRelAggregates':
        #         # d[inverseAttribute] = attributeObject.RelatedObjects
        #     # jsonValue = self.getEntityValue(attributeObject, objData)
        # #     if jsonValue:
        # #         invAtt[attrKey] = jsonValue
        #     # if attributeObject == None:
        #     #     continue
        #     # elif isinstance(attributeObject, ifcopenshell.entity_instance):
        #     #     invAtt[attrKey] = self.entityToDict(attributeObject, objData)
        #     # elif isinstance(attributeObject, tuple):
        #     #     subEnts = []
        #     #     for subEntity in attributeObject:
        #     #         if isinstance(subEntity, ifcopenshell.entity_instance):
        #     #             subEntJson = self.entityToDict(subEntity, objData)
        #     #             if subEntJson:
        #     #                 subEnts.append(subEntJson)
        #     #         else:
        #     #             subEnts.append(subEntity)
        #     #     if len(subEnts) > 0:
        #     #         invAtt[attrKey] = subEnts
        #     # else:
        #     #     invAtt[attrKey] = attributeObject
        #     if invAtt:
        #         # print(inverseAttribute)
        #         d[inverseAttribute] = invAtt

        # if hasattr(entity, 'IsDefinedBy'):
        #     decomposedBy = entity.IsDefinedBy
        #     invAtt = []
        #     for rel in decomposedBy:
        #         print(rel)
        #         relatedObjects = rel.RelatingPropertyDefinition.HasProperties
        #         print(relatedObjects)
        #         for relatedObject in  relatedObjects:
        #             relatedEntity = self.entityToDict(relatedObject, objData, parent=entity)
        #             if parent != relatedEntity:
        #                 invAtt.append(relatedEntity)
        #             # print(relatedObject)
        #         # invAtt = invAtt + list(self.entityToDict(subEntity, objData))
        #     print(invAtt)
        #     if invAtt:
        #         d['IsDefinedBy'] = invAtt

        if hasattr(entity, 'IsDefinedBy'):
            relations = entity.IsDefinedBy
            # p = {}
            for rel in relations:
                if rel.is_a() == 'IfcRelDefinesByProperties':
                    definition = rel.RelatingPropertyDefinition
                    if definition.is_a() == 'IfcPropertySet':
                        relatedObjects = definition.HasProperties
                        for relatedObject in relatedObjects:
                            value = relatedObject.NominalValue.wrappedValue
                            if value and value != '':
                                d[common.toLowerCamelcase(
                                    relatedObject.Name)] = value
                    elif definition.is_a() == 'IfcElementQuantity':
                        relatedObjects = definition.Quantities
                        for relatedObject in relatedObjects:
                            value = relatedObject.AreaValue
                            if value and value != '':
                                d[common.toLowerCamelcase(
                                    relatedObject.Name)] = value
                    else:
                        print('Skipped: ' + str(definition))
                else:
                    print('Skipped: ' + str(rel))
            # if p:
            #     d['properties'] = p

        if hasattr(entity, 'IsDecomposedBy'):
            decomposedBy = entity.IsDecomposedBy
            invAtt = []
            for rel in decomposedBy:
                relatedObjects = rel.RelatedObjects
                for relatedObject in relatedObjects:
                    relatedEntity = self.entityToDict(
                        relatedObject, objData, parent=entity)
                    if parent != relatedEntity:
                        invAtt.append(relatedEntity)
            if invAtt:
                d['IsDecomposedBy'] = invAtt

        if hasattr(entity, 'ContainsElements'):
            decomposedBy = entity.ContainsElements
            invAtt = []
            for rel in decomposedBy:
                relatedObjects = rel.RelatedElements
                for relatedObject in relatedObjects:
                    relatedEntity = self.entityToDict(
                        relatedObject, objData, parent=entity)
                    if parent != relatedEntity:
                        invAtt.append(relatedEntity)
            if invAtt:
                d['ContainsElements'] = invAtt

        if reference:
            uuid = guid.split(guid.expand(entityAttributes["GlobalId"]))[1:-1]
            ref['ref'] = uuid
            if not entityAttributes['GlobalId'] in self.id_objects:

                for i in range(0, len(entity)):
                    attr = entity.attribute_name(i)
                    attrKey = common.toLowerCamelcase(attr)
                    if attr == "GlobalId":
                        d[attrKey] = uuid
                    else:
                        if attr in entityAttributes:

                            # Skip all IFC entities that are not part of IFC.JSON5a
                            if isinstance(entityAttributes[attr], ifcopenshell.entity_instance):

                                # Skip IfcOwnerHistory
                                if entityAttributes[attr].is_a() == 'IfcOwnerHistory':
                                    continue

                                # Skip IfcGeometricRepresentationContext
                                if entityAttributes[attr].is_a() == 'IfcGeometricRepresentationContext':
                                    continue

                            # Use representation from OBJ list if present
                            if attr == 'Representation':
                                if objData:
                                    if entityAttributes['GlobalId'] in objData:
                                        id = guid.split(
                                            guid.expand(guid.new()))[1:-1]
                                        d['representations'] = [
                                            {
                                                "type": "shapeRepresentation",
                                                "ref": id
                                            }
                                        ]
                                        self.representations[id] = {
                                            "type": "shapeRepresentation",
                                            "globalId": id,
                                            "representationIdentifier": "Body",
                                            "representationType": "OBJ",
                                            "items": [
                                                objData[entityAttributes['GlobalId']]
                                            ]
                                        }
                                        continue
                                    else:
                                        continue

                            # Skip ObjectPlacement: all OBJ geometries are in world coordinates
                            if attr == 'ObjectPlacement':
                                continue

                            jsonValue = self.getEntityValue(
                                entityAttributes[attr], objData)
                            if jsonValue:
                                d[attrKey] = jsonValue
                            if entityAttributes[attr] == None:
                                continue
                            elif isinstance(entityAttributes[attr], ifcopenshell.entity_instance):
                                d[attrKey] = self.entityToDict(
                                    entityAttributes[attr], objData)
                            elif isinstance(entityAttributes[attr], tuple):
                                subEnts = []
                                for subEntity in entityAttributes[attr]:
                                    if isinstance(subEntity, ifcopenshell.entity_instance):
                                        subEntJson = self.entityToDict(
                                            subEntity, objData)
                                        if subEntJson:
                                            subEnts.append(subEntJson)
                                    else:
                                        subEnts.append(subEntity)
                                if len(subEnts) > 0:
                                    d[attrKey] = subEnts
                            else:
                                d[attrKey] = entityAttributes[attr]
                self.id_objects[entityAttributes['GlobalId']] = d
            return ref
        else:

            for i in range(0, len(entity)):
                attr = entity.attribute_name(i)
                attrKey = common.toLowerCamelcase(attr)
                if attr in entityAttributes:
                    if not attr == 'OwnerHistory':
                        jsonValue = self.getEntityValue(
                            entityAttributes[attr], objData)
                        if jsonValue:
                            d[attrKey] = jsonValue
                        if entityAttributes[attr] == None:
                            continue
                        elif isinstance(entityAttributes[attr], ifcopenshell.entity_instance):
                            d[attrKey] = self.entityToDict(
                                entityAttributes[attr], objData)
                        elif isinstance(entityAttributes[attr], tuple):
                            subEnts = []
                            for subEntity in entityAttributes[attr]:
                                if isinstance(subEntity, ifcopenshell.entity_instance):
                                    subEntJson = self.entityToDict(
                                        subEntity, objData)
                                    if subEntJson:
                                        subEnts.append(subEntJson)
                                else:
                                    subEnts.append(subEntity)
                            if len(subEnts) > 0:
                                d[attrKey] = subEnts
                        else:
                            d[attrKey] = entityAttributes[attr]

            return d

    def getEntityValue(self, value, objData):
        if value == None:
            jsonValue = None
        elif isinstance(value, ifcopenshell.entity_instance):
            jsonValue = self.entityToDict(value, objData)
        elif isinstance(value, tuple):
            jsonValue = None
            subEnts = []
            for subEntity in value:
                subEnts.append(self.getEntityValue(subEntity, objData))
            jsonValue = subEnts
        else:
            jsonValue = value
        return jsonValue

    # convert IFC SPF file into OBJ using IfcConvert and extract OBJ objects
    def getObjData(self, ifcFilePath):
        objFilePath = NamedTemporaryFile(suffix='.obj', delete=True).name

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
            vertexIterator = 0
            vertexCount = 0
            f = open(objFilePath, 'r')
            lc = 0
            for line in f:
                lc += 1

                # find group
                if line[0] == 'g':
                    header = False
                    vertexCount = copy.deepcopy(vertexIterator)
                    objData[groupId] = ''.join(groupData)
                    groupId = line.split()[1]
                    groupData = []
                else:
                    if header:
                        pass
                    else:
                        if line[0:2] == 'v ':
                            groupData.append(line)
                            vertexIterator += 1
                        elif line[0] == 'f':
                            fl = []
                            face = line[2:].rstrip().split(' ')
                            for fp in face:
                                p = fp.split('//')
                                ps0 = int(p[0]) - vertexCount
                                ps1 = int(p[1]) - vertexCount
                                ps = str(ps0) + '//' + str(ps1)
                                fl.append(ps)

                            fs = 'f ' + ' '.join(fl) + '\n'
                            groupData.append(fs)
            return objData
        else:
            print('Creating intermediate OBJ failed')
            return None
