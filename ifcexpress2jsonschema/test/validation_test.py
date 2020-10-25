# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
from jsonschema import validate

with open("../IFC4x2.json", "r") as schemaFile:
    schema = json.load(schemaFile)

instance = {
    "data": [
        {
            "Class": "IfcWall",
            "OwnerHistory": {
                "Class": "IfcOwnerHistory",
                "OwningUser": {
                    "Class": "IfcPersonAndOrganization",
                    "ThePerson": {
                        "Class": "IfcPerson"
                    },
                    "TheOrganization": {
                        "Class": "IfcOrganization",
                        "Name": "BIM-Tools"
                    }
                },
                "OwningApplication": {
                    "Class": "IfcApplication",
                    "ApplicationDeveloper": {
                        "Class": "IfcOrganization",
                        "Name": "BIM-Tools"
                    },
                    "Version": "'2.2.2'",
                    "ApplicationFullName": "'IFC manager for sketchup'",
                    "ApplicationIdentifier": "'su_ifcmanager'"
                },
                "ChangeAction": ".ADDED.",
                "CreationDate": 1582034331
            },
            "Name": "Wall 01",
            "Description": "The Great Wall",
            "GlobalId": "0meHXtOwHDhwxSDf2okNDz"
        }
    ]
}

validate(instance=instance, schema=schema)