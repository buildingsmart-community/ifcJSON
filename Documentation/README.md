# ifcJSON Specification
This is the overall specification for ifcJSON.

## Table of Contents
  * [1. Overview](#1-overview)
    + [1.1 Objectives](#11-objectives)
    + [1.2 Development strategy](#12-development-strategy)
  * [2. ifcJSON Document Specification](#2-ifcjson-document-specification)
    + [2.1 Required objects, keys, or entities](#21-required-objects--keys--or-entities)
    + [2.2 Empty values, 'userdefined' values, and 'notdefined' values](#22-empty-values---userdefined--values--and--notdefined--values)
    + [2.4 Header](#24-header)
    + [2.5 Identifiers](#25-identifiers)
    + [2.6 Tree Structure](#26-tree-structure)
    + [2.7 camelCase, CamelCaps, or snake_case](#27-camelcase--camelcaps--or-snake-case)
    + [2.8 PredefinedTypes and ObjectTypes and Types](#28-predefinedtypes-and-objecttypes-and-types)
    + [2.9 Geometry](#29-geometry)
    + [2.10 Attributes, Properties and Property Sets](#210-attributes--properties-and-property-sets)
  * [3. ifcJSON Schema](#3-ifcjson-schema)
  * [4. More information](#4-more-information)

## 1. Overview

### 1.1 Objectives
JSON is used throughout the world for exchanging and using data. Building data needs to be available in JSON. Therefore, IFC needs to be available in JSON format. 

IFCJSON aims primarily at addressing the following problems with IFC:

1.	Many developers have never seen/used EXPRESS or STP instance files before, which increases the effort required to extract data required from them. 
2.	IFC instance populations are typically exchanged as files, which is at odds with linked, distributed, and rapidly changing data seen on most design and construction projects and products.

Multiple strategies can be followed, leading to different kinds of JSON. This document aims to specify the single recommended JSON specification for IFC.

### 1.2 Development strategy
A number of criteria could be followed for making a JSON version for IFC.

1.	Backwards compatibility
2.	Round-trip
3.	Human-readability
4.	Flexibility and extensibility
5.	Integration with code
6.	Parallel to XML format
7.	Parallel to EXPRESS schema
8.	Clear referencing structure (flat or nesting)

We cannot support all criteria in one format. Choices have to be made; or multiple JSON flavours need to be enabled. In this document, we aim to support 1 and 1 only JSON format for IFC. 

The following criteria are followed:
1.	Backwards compatibility
2.	Round-trip
3.	Parallel to EXPRESS schema

The following criteria are considered to be of less importance, so they are excluded. This ifcJSON version first and foremost tries to include all that is present in the original IFC EXPRESS schema.

The following criteria are therefore NOT followed:
1.	Human-readability
2.	Integration with code
3.	Clear referencing structure
4.	Direct usability

## 2. ifcJSON Document Specification
In the below sections, a more detailed specification is given for ifcJSON. We don't provide a full schema here, but rather list a number of general principles.

### 2.1 Required objects, keys, or entities
Several elements are required in the IFC EXPRESS Schema. These restrictions are largely released in the IFC4 JSON spec, thereby allowing easier and more specific data exchanges (transactional data exchange). The remaining restrictions are made available in the JSON schema for IFC. You can check whether a JSON file is valid against this JSON schema of IFC by using any of the freely available validators.

### 2.2 Empty values, 'userdefined' values, and 'notdefined' values
You are free to include empty values, yet you are encouraged to leave them out of the data exchange. The `NOTDEFINED` and `USERDEFINED` Enum elements are maintained and available.

This is valid:

~~~
"type" : "IfcDoor",
"globalId" : "157c866c-9c08-4348-a0ed-4d57cd66c9e2",
"name" : "A common door",
"description": "",
"overallHeight" : null,
"overallWidth" : null,
"predefinedType": "NOTDEFINED"
~~~

This is also valid, and preferable over empty values:

~~~
"type" : "IfcDoor",
"globalId" : "157c866c-9c08-4348-a0ed-4d57cd66c9e2",
"name" : "A common door"
~~~

This is encouraged:

~~~
"type" : "IfcDoor",
"globalId" : "157c866c-9c08-4348-a0ed-4d57cd66c9e2",
"name" : "A common door",
"description" : "Description of a standard door",
"overallHeight" : 1.4,
"overallWidth" : 0.7,
"predefinedType" : "GATE"
~~~

### 2.4 Header
A header is included in the IFCJSON file and is a direct translation of the header section in a SPF file.

### 2.5 Identifiers
An object is identified by its globalID, which is a UUID according to https://tools.ietf.org/html/rfc4122. Whereas the globalId attribute is only available to those elements that are descendent of the IfcRoot entity in the EXPRESS schema, we encourage a broader use of this globalId, to enable referencing between objects in a JSON file when useful.

~~~
"globalId": "028c968f-687d-484e-9c0a-5048a923b8c4"
~~~

Objects can be referenced in JSON by using the globalId attribute. In the example below, a reference is made to the ownerHistory object, which has the globalId `6d7919fd-2c83-497b-b21c-d4209e5162bf`.	
 
~~~
"type" : "IfcRelContainedInSpatialStructure",
"globalId" : "98fa75b8-371d-412a-be42-2326c68dfcf5",
"ownerHistory" : "6d7919fd-2c83-497b-b21c-d4209e5162bf",
"name" : "Default Building",
"description" : "Contents of Building Storey"
~~~

### 2.6 Tree Structure
Generally, the ifcJSON structure is flexible. Objects may be nested inline, or referenced using references to the globalId. It is recommended to use a tree structure (forward downward relationships) as much as possible, in order to improve human readability. All objects in IFC are maintained, included the objectified relationships (many-to-many and one-to-many and ternary and n-ary).

Example:

~~~
{
  "type" : "IfcProject",
  "globalId" : "22e66ddf-794d-40bb-8aa5-3dda450d8255",
  "name" : "Default Project",
  "description" : "Description of Default Project",
  "isDecomposedBy" : {
    "type" : "IfcRelAggregates",
    "globalId" : "57bfe2d2-b505-4bba-8278-f867834a0be0",
    "ownerHistory" : "6d7919fd-2c83-497b-b21c-d4209e5162bf",
    "name" : "ProjectContainer",
    "description" : "ProjectContainer for Sites",
    "relatedObjects" : [ {
      "type" : "IfcSite",
      "globalId" : "f55eaf97-145e-4431-b2f3-69f9634f244b",
      "ownerHistory" : "6d7919fd-2c83-497b-b21c-d4209e5162bf",
      "name" : "TU/e campus",
      "description" : "The High Tech campus of the Eindhoven University of Technology",
      "isDecomposedBy" : {
        "type" : "IfcRelAggregates",
        "globalId" : "d3e2bc1a-4cdb-49ed-9c4a-c60c97949121",
        "ownerHistory" : "6d7919fd-2c83-497b-b21c-d4209e5162bf",
        "name" : "SiteContainer",
        "description" : "SiteContainer For Buildings",
        "relatedObjects" : [ {
          "type" : "IfcBuilding",
          "globalId" : "3ca7e585-4e3e-4969-a86f-f049f4fbde52",
          "ownerHistory" : "6d7919fd-2c83-497b-b21c-d4209e5162bf",
          "name" : "Vertigo Building",
          "description" : "TU/e Department of the Built Environment"
        } ]
      }
    } ]
  }
}
~~~

### 2.7 camelCase, CamelCaps, or snake_case
The most commonly used notation in JSON is camelCase, mainly because of its alignment with a JavaScript and Python audience. Hence, the JSON version of IFC uses camelCase as much as possible.

This is valid:
~~~
"globalId": "028c968f-687d-484e-9c0a-5048a923b8c4"
~~~

This is not valid:
~~~
"GlobalId": "028c968f-687d-484e-9c0a-5048a923b8c4"
"global_id": "028c968f-687d-484e-9c0a-5048a923b8c4"
~~~

### 2.8 PredefinedTypes and ObjectTypes and Types
There are multiple ways to define the object type of an object in the IFC EXPRESS schema. In ifcJSON, the same structure is followed as in the original IFC schema and you can include type information in the `type`, `predefinedType` and `objectType` attributes. As indicated in the ifcJSON schema, the `type` and `objectType` attributes refer to a string. The `type` attribute is hereby reserved for the IFC type name. The `predefinedType` attribute is only available for a number of objects, and the allowed values for this attributes are listed in the ifcJSON schema (identical to EXPRESS schema). These predefinedType values do not need to be enclosed by dots (in other words: NOT `".GATE."`, but just `"GATE"`).

This is valid:
~~~
"type" : "IfcDoor",
"globalId" : "157c866c-9c08-4348-a0ed-4d57cd66c9e2",
"name" : "A common door",
"description" : "Description of a standard door",
"overallHeight" : 1.4,
"overallWidth" : 0.7,
"predefinedType" : "GATE"
~~~

This is also valid and allows userdefined subtypes.

~~~
"type" : "IfcDoor",
"globalId" : "157c866c-9c08-4348-a0ed-4d57cd66c9e2",
"name" : "A less common door",
"description" : "Description of a standard door",
"objectType" : "ThickMassiveWoodenDoor",
"overallHeight" : 1.4,
"overallWidth" : 0.7,
"predefinedType" : "USERDEFINED"
~~~

### 2.9 Geometry
Geometry is included similar to how it was included in the STEP file, thus allowing the inclusion of representation data and units and geometric contexts.

Example:

~~~
"representation" : {
  "type" : "IfcProductDefinitionShape",
  "representations" : [ {
    "type" : "IfcShapeRepresentation",
    "contextOfItems" : "e4c36548-94c3-4939-930f-94899539746b",
    "representationIdentifier" : "Body",
    "representationType" : "SweptSolid",
    "items" : [ {
      "type" : "IfcExtrudedAreaSolid",
      "sweptArea" : {
        "type" : "IfcArbitraryClosedProfileDef",
        "profileType" : "AREA",
        "outerCurve" : {
          "type" : "IfcPolyline",
          "points" : [ 
            {
              "type" : "IfcCartesianPoint",
              "coordinates" : [ 0.0, 0.0 ]
            }, {
              "type" : "IfcCartesianPoint",
              "coordinates" : [ 0.0, 0.1 ]
            }, {
              "type" : "IfcCartesianPoint",
              "coordinates" : [ 0.75, 0.1 ]
            }, {
              "type" : "IfcCartesianPoint",
              "coordinates" : [ 0.75, 0.0 ]
            }, {
              "type" : "IfcCartesianPoint",
              "coordinates" : [ 0.0, 0.0 ]
            } ]
        }
      },
      "position" : { ... },
      "extrudedDirection" : {
        "type" : "IfcDirection",
        "directionRatios" : [ 0.0, 0.0, 1.0 ]
      },
      "depth" : 2.1
    } ]
  } ]
}
~~~

### 2.10 Attributes, Properties and Property Sets
In ifcJSON, attributes, properties and property sets are included identical to how they are included in the IFC EXPRESS schema.

Example:

~~~
"type" : "IfcWall",
"globalId" : "f92c2898-fd68-44ef-9178-3348e340017b",
"isDefinedBy" : [ {
  "type" : "IfcRelDefinesByProperties",
  "globalId" : "d2ecfe17-45be-4b36-959d-1be3ec8193bd",
  "ownerHistory" : "6d7919fd-2c83-497b-b21c-d4209e5162bf",
  "relatingPropertyDefinition" : {
    "globalId" : "486f7679-1a8a-4deb-8798-5a7e0c8c7d51",
    "ownerHistory" : "6d7919fd-2c83-497b-b21c-d4209e5162bf",
    "name" : "Pset_WallCommon",
    "hasProperties" : [ 
      {
        "type" : "IfcPropertySingleValue",
        "name" : "IsExternal",
        "description" : "IsExternal",
        "nominalValue" : {
          "type" : "IfcBoolean",
          "booleanValue" : true
        }
      }, {
        "type" : "IfcPropertySingleValue",
        "name" : "Reference",
        "description" : "Reference",
        "nominalValue" : {
          "type" : "IfcText",
          "stringValue" : "insert URL"
        }
      }
    ]
  }
}]
~~~

## 3. ifcJSON Schema
Like the XSD schema specification and OWL ontology for IFC, also the ifcJSON schema can be automatically converted from the EXPRESS (ISO 10303 part 1) representation of the IFC schema. Roundtripping conversion from IFC-SPF files to JSON is also possible. Both schema and data conversion are not (yet) available. Yet, an ifcJSON schema is available in this repository and allows to validate which ifcJSON is valid.

ifcJSON schema defines a structure for what ifcJSON data is required and therefore its schema defines the validation and interaction control of ifcJSON data.

Example ifcJSON data:
~~~
{
  "type": "IfcWall",
  "globalId": "028c968f-687d-484e-9c0a-5048a923b8c4",
  "name": "my wall",
  "description": "Description of the wall",
  "objectPlacement": null,
  "objectType": "null",
  "representation": null,
  "tag": "267108",
  "ownerHistory": null,
  "predefinedType": "SOLIDWALL"
}
~~~

Corresponding ifcJSON Schema snippet:
~~~
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "http://example.com/product.schema.json",
  "title": "Wall",
  "description": "ifcJSON for Wall",
  "type": "object",
  "properties": {
  "type": "ifcWall",
  "globalId": {
    "type": "string",
    "maxLength": 22
  },
  "ownerHistory": {"oneOf":[
    {"type": "null"},
    {
	  "type": "object",
      "allOf": [{ "$ref": "#/properties/ifcOwnerHistory"}]
    }]
  },
  "name":{"oneOf":[
    {"type": "null"},
    {
	  "type": "string",
      "maxLength": 255
	}]
  },
  "description": {
    "type" : ["string", "null"]
  },
  "objectType": {"oneOf":[
    {"type": "null"},
    {
	  "type": "string",
      "maxLength": 255
	}]
  },
  "objectPlacement": {"oneOf":[
    {"type": "null" },
    {
	  "type": "object",
      "allOf": [{ "$ref": "#/properties/ifcLocalPlacement" }]
    }]
  },
  "representation": { 
    "type": "object",
    "allOf": [{ "$ref": "#/properties/ifcProductDefinitionShape" }]
  },
  "tag": {
    "type": "string",
    "maxLength": 255
  },
  "predefinedType": {
    "oneOf":[
      { "type": "null" },
      { "type": "string",
        "enum": ["MOVABLE",
          "PARAPET",
          "PARTITIONING",
          "PLUMBINGWALL",
          "SHEAR",
          "SOLIDWALL",
          "STANDARD",
          "POLYGONAL",
          "ELEMENTEDWALL",
          "USERDEFINED",
          "NOTDEFINED"]},
     ]
  }
}
~~~

## 4. More information
Contributions are welcome in all possible ways. Your first starting point is creating GitHub issues. Feel free to get in touch with the people in the ifcJSON-team.
