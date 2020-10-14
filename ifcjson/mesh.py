class ObjMesh:
    def __init__(self, *argv):
        self.globalId = ""
        self.vertices = []
        self.faces = []
        if len(argv) == 1:
            # Assume import is a OBJ string
            self.splitObjString(argv[0])
        elif len(argv) == 2:
            # Assume import is list of vertices and a list of faces
            self.vertices = argv[0]
            self.faces = argv[1]
    
    def splitObjString(self, objString):
        lines = objString.splitlines()
        for line in lines:
            ent = line.split()
            type = ent.pop(0)
            if type == 'v':
                self.vertices.append(list(map(float, ent)))
            elif type == 'f':
                self.faces.append(list(map(int, ent)))
    
    def toObjString(self):
        vertsList = [' '.join(map(str, self.vertices[x:x+3]))
                        for x in range(0, len(self.vertices), 3)]
        vertString = 'v ' + '\nv '.join(vertsList) + '\n'

        facesList = [' '.join(map(str, self.faces[x:x+3]))
                        for x in range(0, len(self.faces), 3)]
        faceString = 'f ' + '\nf '.join(map(str, facesList)) + '\n'

        return vertString + faceString
    
    def toVertices(self):
        return self.vertices
    
    def toFaces(self):
        return self.faces