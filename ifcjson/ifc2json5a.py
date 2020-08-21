# IFCJSON_python - ifc2json5a.py
# Convert IFC SPF file to IFC.JSON-5a
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
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid as guid
import ifcjson.common as common
from datetime import datetime
from ifcopenshell.entity_instance import entity_instance


class IFC2JSON5a(common.IFC2JSON):

    # Attributes that are not part of IFC.JSON5a
    INVALIDATTRIBUTES = {
        'OwnerHistory',
        'RepresentationContexts',
        'ContextOfItems',
        'ObjectPlacement',
        'RepresentationMaps'
    }

    # Attributes for which the intermediate relationship object is removed
    SIMPLIFICATIONS = {
        # IfcRelAggregates
        'IsDecomposedBy':       ['relatedObjects'],
        'Decomposes':           ['relatingObject'],
        # IfcRelContainedInSpatialStructure
        'ContainsElements':     ['relatedElements'],
        'ContainedInStructure': ['relatingStructure'],
        # IfcRelDefinesByProperties
        'IsDefinedBy':          ['relatingPropertyDefinition', 'relatingType'],
        # IfcRelAssociatesMaterial
        'HasAssociations':      ['relatingMaterial'],
        # IfcRelFillsElement
        'HasFillings':          ['relatedBuildingElement'],
        'FillsVoids':           ['relatingOpeningElement'],
        # IfcRelVoidsElement
        'HasOpenings':          ['relatedOpeningElement'],
        'VoidsElements':        ['relatingBuildingElement'],
        # IfcRelDefinesByType
        'ObjectTypeOf':         ['relatedObjects'],
        'IsTypedBy':            ['relatingType'],
        # IfcRelConnectsPathElements (!) This skips all IfcRelConnectsPathElements properties
        'ConnectedTo':          ['relatedElement'],
        'ConnectedFrom':        ['relatingElement'],
        # IfcRelSpaceBoundary (!) This skips all spaceboundary properties like for example geometry
        'BoundedBy':            ['relatedBuildingElement'],
        'ProvidesBoundaries':   ['relatingSpace']
    }

    settings = ifcopenshell.geom.settings()
    settings.USE_PYTHON_OPENCASCADE = True
    settings.set(settings.USE_WORLD_COORDS, True)
    settings.set(settings.EXCLUDE_SOLIDS_AND_SURFACES, False)

    def __init__(self, ifcModel, compact=False):
        """IFC SPF to IFC.JSON-5a writer

        parameters:
        ifcModel: IFC filePath or ifcopenshell model instance
        compact (boolean): if True then pretty print is turned off and references are created without informative "type" property

        """
        if isinstance(ifcModel, ifcopenshell.file):
            self.ifcModel = ifcModel
        else:
            self.ifcModel = ifcopenshell.open(ifcModel)
        self.compact = compact
        self.objectDefinitions = {}

        # Dictionary referencing all objects with a GlobalId that are already created
        self.rootObjects = {}

        # Representations are kept seperate to be added to the end of the list
        self.representations = {}

    def spf2Json(self):
        """
        Create json dictionary structure for all attributes of the objects in the root list
        (?) also including inverse attributes
        (?) Check every IFC object to see if it is used multiple times

        Returns:
        dict: IFC.JSON-5a model structure

        """

        jsonObjects = []

        for entity in self.ifcModel.by_type('IfcObjectDefinition'):
            self.objectDefinitions[entity.id()] = guid.split(
                guid.expand(entity.GlobalId))[1:-1]

        self.rootobjects = dict(self.objectDefinitions)

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

            # Convert representations to OBJ
            if 'Representation' in entityAttributes:
                obj = self.toObj(entity)

                if obj:
                    id = guid.split(guid.expand(guid.new()))[1:-1]
                    ref = {}
                    if not self.compact:
                        ref['type'] = "shapeRepresentation"
                    ref['ref'] = id
                    entityAttributes['representations'] = [ref]
                    self.representations[id] = {
                        "type": "shapeRepresentation",
                        "globalId": id,
                        "representationIdentifier": "Body",
                        "representationType": "OBJ",
                        "items": [
                            obj
                        ]
                    }

                # (!) delete original representation, even if OBJ generation fails
                del entityAttributes['Representation']

            jsonObjects.append(self.createFullObject(entityAttributes))

        jsonObjects = jsonObjects + list(self.representations.values())

        return {
            'fileSchema': 'IFC.JSON-5a',
            'originatingSystem': 'IFC2JSON_python',
            'timeStamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            'data': jsonObjects
        }

    def createFullObject(self, entityAttributes):
        """Returns complete IFC.JSON-5a object

        Parameters:
        entityAttributes (dict): Dictionary of IFC object data

        Returns:
        dict: containing complete IFC.JSON-5a object

        """
        fullObject = {}

        for attr in entityAttributes:

            # Line numbers are not part of IFC JSON
            if attr == 'id':
                continue

            # Skip all IFC entities that are not part of IFC.JSON5a
            if attr in self.INVALIDATTRIBUTES:
                continue

            # Flatten object hierarchy through removing intermediate relationship objects
            if attr in self.SIMPLIFICATIONS:
                for relObject in entityAttributes[attr]:
                    for attrName in self.SIMPLIFICATIONS[attr]:

                        # In case of propertysets, further simplification through removing intermediate PropertySets
                        if attr == 'IsDefinedBy':
                            if relObject['type'] == 'RelDefinesByProperties':
                                if relObject['relatingPropertyDefinition']:
                                    relatingPropertyDefinition = relObject['relatingPropertyDefinition']
                                    if 'hasProperties' in relatingPropertyDefinition:
                                        for property in relatingPropertyDefinition['hasProperties']:
                                            try:
                                                fullObject[property['name']
                                                        ] = property['nominalValue']['value']
                                            except Exception as e:
                                                print(str(e))
                                continue
                            else:
                                print(relObject['type'])
                        if attrName in relObject:
                            entityAttributes[attr] = relObject[attrName]

            attrKey = self.toLowerCamelcase(attr)

            # Replace wrappedvalue key names to value
            if attrKey == 'wrappedValue':
                attrKey = 'value'

            jsonValue = self.getAttributeValue(entityAttributes[attr])
            if jsonValue:

                # Entity names must be stripped of Ifc prefix
                if attr == 'type':
                    jsonValue = jsonValue[3:]

                fullObject[attrKey] = jsonValue
        return fullObject

    def createReferenceObject(self, entityAttributes, compact=False):
        """Returns object reference

        Parameters:
        entityAttributes (dict): Dictionary of IFC object data
        compact (boolean): verbose or non verbose IFC.JSON-5a output

        Returns:
        dict: object containing reference to another object

        """
        ref = {}
        if not compact:

            # Entity names must be stripped of Ifc prefix
            ref['type'] = entityAttributes['type'][3:]
        ref['ref'] = entityAttributes['GlobalId']
        return ref

    def toObj(self, product):
        """Convert IfcProduct to OBJ mesh

        parameters:
        product: ifcopenshell ifcProduct instance

        Returns:
        string: OBJ string
        """

        if product.Representation:
            try:
                shape = ifcopenshell.geom.create_shape(self.settings, product)

                verts = shape.geometry.verts
                vertsList = [' '.join(map(str, verts[x:x+3]))
                             for x in range(0, len(verts), 3)]
                vertString = 'v ' + '\nv '.join(vertsList) + '\n'

                faces = shape.geometry.faces
                facesList = [' '.join(map(str, faces[x:x+3]))
                             for x in range(0, len(faces), 3)]
                faceString = 'f ' + '\nf '.join(map(str, facesList)) + '\n'

                return vertString + faceString
            except Exception as e:
                print(str(e) + ': Unable to generate OBJ data for ' +
                      str(product))
                return None
