# Common tools for ifc2json
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

import ifcopenshell
import ifcopenshell.guid as guid


class IFC2JSON:
    """Base class for all IFC SPF to IFC.JSON writers
    """

    DIMENSIONALEXPONENTS = {
        'METRE': (1, 0, 0, 0, 0, 0, 0),
        'SQUARE_METRE': (2, 0, 0, 0, 0, 0, 0),
        'CUBIC_METRE': (3, 0, 0, 0, 0, 0, 0),
        'GRAM': (0, 1, 0, 0, 0, 0, 0),
        'SECOND': (0, 0, 1, 0, 0, 0, 0),
        'AMPERE': (0, 0, 0, 1, 0, 0, 0),
        'KELVIN': (0, 0, 0, 0, 1, 0, 0),
        'MOLE': (0, 0, 0, 0, 0, 1, 0),
        'CANDELA': (0, 0, 0, 0, 0, 0, 1),
        'RADIAN': (0, 0, 0, 0, 0, 0, 0),
        'STERADIAN': (0, 0, 0, 0, 0, 0, 0),
        'HERTZ': (0, 0, -1, 0, 0, 0, 0),
        'NEWTON': (1, 1, -2, 0, 0, 0, 0),
        'PASCAL': (-1, 1, -2, 0, 0, 0, 0),
        'JOULE': (2, 1, -2, 0, 0, 0, 0),
        'WATT': (2, 1, -3, 0, 0, 0, 0),
        'COULOMB': (0, 0, 1, 1, 0, 0, 0),
        'VOLT': (2, 1, -3, -1, 0, 0, 0),
        'FARAD': (-2, -1, 4, 2, 0, 0, 0),
        'OHM': (2, 1, -3, -2, 0, 0, 0),
        'SIEMENS': (-2, -1, 3, 2, 0, 0, 0),
        'WEBER': (2, 1, -2, -1, 0, 0, 0),
        'TESLA': (0, 1, -2, -1, 0, 0, 0),
        'HENRY': (2, 1, -2, -2, 0, 0, 0),
        'DEGREE_CELSIUS': (0, 0, 0, 0, 1, 0, 0),
        'LUMEN': (0, 0, 0, 0, 0, 0, 1),
        'LUX': (-2, 0, 0, 0, 0, 0, 1),
        'BECQUEREL': (0, 0, -1, 0, 0, 0, 0),
        'GRAY': (2, 0, -2, 0, 0, 0, 0),
        'SIEVERT': (2, 0, -2, 0, 0, 0, 0),
        'OTHERWISE': (0, 0, 0, 0, 0, 0, 0)
    }

    def toLowerCamelcase(self, string):
        """Convert string from upper to lower camelCase"""

        return string[0].lower() + string[1:]

    def getDimensionsForSiUnit(self, entity):
        dimensions = {}
        if entity.Name in self.DIMENSIONALEXPONENTS:
            dimExps = self.DIMENSIONALEXPONENTS[entity.Name]
            if dimExps[0] != 0:
                dimensions['LengthExponent'] = dimExps[0]
            if dimExps[1] != 0:
                dimensions['MassExponent'] = dimExps[1]
            if dimExps[2] != 0:
                dimensions['TimeExponent'] = dimExps[2]
            if dimExps[3] != 0:
                dimensions['ElectricCurrentExponent'] = dimExps[3]
            if dimExps[4] != 0:
                dimensions['ThermodynamicTemperatureExponent'] = dimExps[4]
            if dimExps[5] != 0:
                dimensions['AmountOfSubstanceExponent'] = dimExps[5]
            if dimExps[6] != 0:
                dimensions['LuminousIntensityExponent'] = dimExps[6]

        return dimensions

    def getAttributeValue(self, value):
        """Recursive method that walks through all nested objects of an attribute
        and returns a IFC.JSON-4 model structure

        Parameters:
        value

        Returns:
        attribute data converted to IFC.JSON-4 model structure

        """
        if value == None or value == '':
            jsonValue = None
        elif isinstance(value, ifcopenshell.entity_instance):
            entity = value
            entityAttributes = entity.__dict__

            # Remove empty properties
            if entity.is_a() == 'IfcPropertySingleValue':
                try:
                    value = entity.NominalValue.wrappedValue
                    if not value:
                        return None
                except:
                    return None

            # Add unit dimensions https://standards.buildingsmart.org/IFC/DEV/IFC4_2/FINAL/HTML/schema/ifcmeasureresource/lexical/ifcdimensionsforsiunit.htm
            if entity.is_a() == 'IfcSIUnit':
                entityAttributes['dimensions'] = self.getDimensionsForSiUnit(
                    entity)

            # All objects with a GlobalId must be referenced, all others nested
            if entity.id() in self.rootobjects:
                entityAttributes["GlobalId"] = self.rootobjects[entity.id()]
                return self.createReferenceObject(entityAttributes, self.compact)
            else:
                if 'GlobalId' in entityAttributes:
                    entityAttributes["GlobalId"] = guid.split(
                        guid.expand(entity.GlobalId))[1:-1]

            return self.createFullObject(entityAttributes)
        elif isinstance(value, tuple):
            jsonValue = None
            subEnts = []
            for subEntity in value:
                attrValue = self.getAttributeValue(subEntity)
                if attrValue:
                    subEnts.append(attrValue)
            jsonValue = subEnts
        else:
            jsonValue = value
        return jsonValue
