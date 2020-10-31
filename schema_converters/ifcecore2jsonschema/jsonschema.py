import json


class JsonSchema:
    """
    Library that helps building json-schema structures
    """

    def __init__(self, version='http://json-schema.org/draft-07/schema#'):
        self.schema = {
            "type": "object"
        }
        self.properties = {}
        self.definitions = {}
        self.set_version(version)

    def set_title(self, title):
        self.schema['title'] = title

    def set_version(self, version):
        self.schema['$schema'] = version

    def to_json(self):
        """
        Serialize JsonSchema
        """
        self.schema['properties'] = self.properties
        self.schema['definitions'] = self.definitions
        return json.dumps(self.schema, indent=2)

    def save(self, savepath):
        """
        Write JsonSchema to file
        """
        with open(savepath, 'w') as outfile:
            outfile.write(self.to_json())
