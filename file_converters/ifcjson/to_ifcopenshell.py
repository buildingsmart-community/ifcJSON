import json
import pandas as pd
import uuid

import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.template

from ifcjson.reader import IFCJSON

# Specific JSON types that need mapping
INCLUDE_ATTRIBUTES = ['value']

# IfcOpenShell does not seem to support dimensions: https://standards.buildingsmart.org/IFC/DEV/IFC4_2/FINAL/HTML/schema/ifcmeasureresource/lexical/ifcdimensionsforsiunit.htm
EXCLUDE_ATTRIBUTES = ['id', 'type', 'dimensions']


class JSON2IFC(IFCJSON):

    def __init__(self, inFilePath):

        self.fileSchema = None
        self.schemaIdentifier = None
        self.timeString = None
        self.organization = None
        self.creator = None
        self.applicationVersion = None
        self.timeStamp = None
        self.application = None

        with open(inFilePath) as ifcJsonFile:
            ifcJson = json.load(ifcJsonFile)

            # When ifcJson data is a complete filestructure including header
            if type(ifcJson) is dict:
                self.parseHeader(ifcJson)
                if 'type' in ifcJson:
                    if ifcJson['type'] == 'ifcJSON':
                        
                        self.timestamp = None
                        
                        if 'data' in ifcJson:
                            self.collect_objects(ifcJson['data'])
                        else:
                            print('Not a valid ifcJson file')
                    else:
                        print('Not a valid ifcJson file')

                else:
                    print('Not a valid ifcJson file')

            # When ifcJson data is just a list of objects
            elif type(ifcJson) is dict:
                self.collect_objects(ifcJson['data'])

    def toLowerCamelcase(self, string):
        """Convert string from upper to lower camelCase"""

        return string[0].lower() + string[1:]

    def toUpperCamelcase(self, string):
        """Convert string from lower to upper camelCase"""

        return string[0].upper() + string[1:]

    def isNaN(self, num):
        return num != num

    def uuidToGlobalId(self, uuidString):
        if not self.isNaN(uuidString):
            return ifcopenshell.guid.compress(uuid.UUID(uuidString).hex)
        else:
            return uuid

    def readData(self, data):
        self.data = pd.DataFrame()
        self.data["data"] = data
        self.data['type'] = self.data['data'].apply(pd.Series)['type']
        self.data['uuid'] = self.data['data'].apply(pd.Series)['globalId']
        return(self.data)

    def createNestedEntity(self, attributes):
        entityType = attributes['type']
        entity = self.model.create_entity(entityType)
        self.fillEntity(attributes, entity)
        return entity

    def fillEntityFromDf(self, row):
        data = row.data
        entity = self.model.by_id(row.id)
        self.fillEntity(data, entity)

    def createEntity(self, row):
        entityType = row.type
        entity = self.model.create_entity(entityType)
        return entity.id()

    def getAttributeObject(self, attributeValue):
        if type(attributeValue) is dict:
            if 'ref' in attributeValue:
                row = self.data.loc[self.data['uuid'] ==
                                    attributeValue['ref']]['id'].values
                return self.model.by_id(int(row[0]))
            else:
                return self.createNestedEntity(attributeValue)
        elif type(attributeValue) is list:
            returnList = []
            for listItem in attributeValue:
                returnList.append(self.getAttributeObject(listItem))
            if returnList:
                return returnList
        else:
            return attributeValue

    def fillEntity(self, data, entity):
        attributes = entity.get_info().keys()
        for attribute in data:
            attributeName = self.toUpperCamelcase(attribute)
            if attributeName not in attributes and attribute not in INCLUDE_ATTRIBUTES:
                continue
            if attribute in EXCLUDE_ATTRIBUTES:
                continue
            if attribute == 'globalId':
                data['globalId'] = self.uuidToGlobalId(data['globalId'])

            attributeValue = data[attribute]
            attributeObject = self.getAttributeObject(attributeValue)
            if attributeObject == None:
                continue
            if attributeName == 'Value':
                attributeName = 'wrappedValue'
            try:
                setattr(entity, attributeName, attributeObject)
            except Exception:
                if attributeName != 'GlobalId':
                    print('Unable to set attribute %s for entity %s' %
                          (attributeName, entity.is_a()))

    def collect_objects(self, data):
        self.data = self.readData(data)
        project = self.data[self.data.type == 'IfcProject'].iloc[0].data
        self.project_globalid = ifcopenshell.guid.compress(
            uuid.UUID(project['globalId']).hex)
        self.project_name = project['name']
        self.model = ifcopenshell.file(None, self.schemaIdentifier)
        self.data['id'] = self.data.apply(self.createEntity, axis=1)
        self.data.apply(self.fillEntityFromDf, axis=1)

    def ifcModel(self):
        return self.model
