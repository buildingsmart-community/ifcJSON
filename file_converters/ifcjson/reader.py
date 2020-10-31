import ifcjson.mesh as mesh

class IFCJSON:
    def __init__(self, json):
        """ifcJSON data reader

        parameters:
        ifcJSON data

        """
        self.json = json

        # Main object container
        self.index = {}
        
        # Used object types container
        self.entityTypes = {}

        # Geometry container for ifcJSON5a OBJ meshes
        self.geometry = {}

        self.fileSchema = None
        self.schemaIdentifier = None
        self.timeString = None
        self.organization = None
        self.creator = None
        self.applicationVersion = None
        self.timeStamp = None
        self.application = None
        
        # When ifcJson data is a complete filestructure including header
        if type(json) is dict:
            self.parseHeader(json)
            if 'data' in json:
                self.data = json['data']
            else:
                raise ValueError("Not a valid ifcJSON file")

        # When json data is just a list of objects
        elif type(json) is list:
            self.data = json
        else:
            raise ValueError("Not a valid ifcJSON file")

        self.parseData(self.data)

    def parseHeader(self, json):
        
        # If no fileSchema available, assume it's ifcJSON-4
        # if 'fileSchema' in json:
        #     if json['fileSchema'] == 'ifcJSON-4':
        #         self.schemaIdentifier = 'IFC2X3' # IFC4
        #     else:
        #         raise ValueError('FileSchema "{}" not supported.'.format(json['fileSchema']))
        if 'fileSchema' in json:
            self.fileSchema = json['fileSchema']
        if 'timeString' in json:
            self.timeString = json['timeString']
        if 'organization' in json:
            self.organization = json['organization']
        if 'creator' in json:
            self.creator = json['creator']
        if 'applicationVersion' in json:
            self.applicationVersion = json['applicationVersion']
        if 'timeStamp' in json:
            self.timeStamp = json['timeStamp']
        if 'application' in json:
            self.application = json['application']

    def parseData(self, data):
        if not type(data) is list:
            raise ValueError("Not a valid ifcJSON file, data object must contain a list of entities.")
        for entity in data:
            self.parseValue(entity)

    def parseValue(self, entity):
        if type(entity) is dict:
            if 'type' in entity:
                if 'globalId' in entity:
                    self.addToIndex(entity)

            for value in entity:
                self.parseValue(entity[value])
        elif type(entity) is list:
            for listItem in entity:
                self.parseValue(listItem)

    def addType(self, entity):
        entityType = entity['type']
        if not entityType in self.entityTypes:
            self.entityTypes[entityType] = []
        self.entityTypes[entityType].append(entity['globalId'])

    def addToIndex(self, entity):
        """Adds entity to one of the entity indexes (entityTypes and index or geometry)

        Parameters:
        entity (dict)

        """

        # Seperately store mesh geometry (OBJ and Tessellation)
        if('representationType' in entity) and (entity['representationType'] in ('OBJ','Tessellation')):
            entityId = entity['globalId']
            self.geometry[entityId] = entity
        else:
            entityId = entity['globalId']
            self.index[entityId] = entity
            self.addType(entity)

    def types(self):
        """Returns all entity types present in the model

        Parameters:
        typeName (string)

        Returns:
        list

        """
        return list(self.entityTypes.keys())

    def entitiesByType(self, typeName):
        """Returns all entities of given type

        Parameters:
        typeName (string)

        Returns:
        list

        """
        if typeName in self.entityTypes:
            typeEntities = self.entityTypes[typeName]
            # return {x for x in self.data}
            return [self.index[k] for k in typeEntities if k in self.index]

    def entityById(self, globalId):
        """Returns the entitity for the given globalId

        Parameters:
        globalId (string)

        Returns:
        dict

        """
        if globalId in self.index:
            return self.index[globalId]

    def geometryById(self, globalId):
        """Returns the geometry for the given geometry globalId

        Parameters:
        globalId (string)

        Returns:
        dict

        """
        if globalId in self.geometry:
            return self.geometry[globalId]

    def meshesById(self, globalId):
        """Returns the OBJ mesh objects for the given geometry globalId

        Parameters:
        globalId (string)

        Returns:
        list

        """
        if globalId in self.geometry:
            shapeRepresentation = self.geometryById(globalId)
            if 'items' in shapeRepresentation:
                items = shapeRepresentation['items']
                if type(items) is list:
                    return shapeRepresentation['items']

    def entities(self):
        """Returns all ifcJSON entities

        Returns:
        list

        """
        return list(self.index.values())

    def mainEntities(self):
        """Returns the entities from the ifcJSON 'data' attribute

        Returns:
        list

        """
        return self.data
    
    def mainEntitiesDict(self):
        """Returns the entities from the ifcJSON 'data'
        as a dictionary with globalId as key

        Returns:
        dict

        """
        return {x['globalId']:x for x in self.data}


    def geometryAsMeshes(self):
        """Returns the OBJ or Tessellation geometry as lists of globalIds, vertices per mesh and faces per mesh.

        Returns:
        dict: mesh objects by globalId

        """
        meshes = {}
        for globalId in self.geometry:
            value = self.geometry[globalId]
            if 'representationType' in value:
                if 'items' in value:
                    if value['representationType'] == 'OBJ':
                        meshes[globalId] = []
                        for item in value['items']:
                            mesh2 = mesh.ObjMesh(item)
                            print(type(mesh2))
                            meshes[globalId].append(mesh2)
                    elif value['representationType'] == 'Tessellation':
                        meshes[globalId] = []
                        for item in value['items']:
                            if item['type'] == 'IfcTriangulatedFaceSet':
                                if 'coordinates' in item:
                                    if isinstance(item['coordinates'], dict):
                                        coordinates = item['coordinates']
                                        if 'type' in coordinates:
                                            if coordinates['type'] == 'IfcCartesianPointList3D':
                                                if 'coordList' in coordinates:
                                                    if isinstance(coordinates['coordList'], list):
                                                        if 'coordIndex' in item:
                                                            if isinstance(item['coordIndex'], list):
                                                                vertices = coordinates['coordList']
                                                                # print(vertices)
                                                                faces = item['coordIndex']
                                                                mesh1 = mesh.ObjMesh(vertices, faces)
                                                                # print(type(mesh1))
                                                                meshes[globalId].append(mesh1)
        return meshes
            


