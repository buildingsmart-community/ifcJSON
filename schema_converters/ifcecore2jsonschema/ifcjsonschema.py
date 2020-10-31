from jsonschema import JsonSchema


class IfcJsonSchemaEcore(JsonSchema):
    """
    Create ifc-json-schema from eCore ePackage
    """

    def __init__(self,
                 epackage,
                 ifcschemaversion='IFC.JSON-4.3',
                 jsonschemaversion='http://json-schema.org/draft-07/schema#'):
        super().__init__(jsonschemaversion)
        self.epackage = epackage
        self.properties = {
            'file_schema': {
                'const': ifcschemaversion
            },
            'data': {
                'type': 'array',
                'items': {
                    'anyOf': []
                }
            }
        }
        self.classes = []
        for eclassifier in epackage.eClassifiers:
            self.add_class(eclassifier)

    def add_class(self, eclassifier):
        self.definitions[eclassifier.name] = {
            'type': 'object'
        }
        self.properties['data']['items']['anyOf'].append({
            'type': 'object',
            'properties': {
                'type': {
                    'const': eclassifier.name
                }
            },
            'allOf': [
                {
                    '$ref': '#/definitions/' + eclassifier.name
                }
            ]
        })
