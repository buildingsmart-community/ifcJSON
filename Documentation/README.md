# IFC.JSON Specification
This is the overall specification for IFC.JSON.

## Table of Contents
  * [1. Overview](#1-overview)
    + [1.1 Objectives](#11-objectives)
    + [1.2 Development strategy](#12-development-strategy)
  * [2. ifcJSON Document Specification](#2-ifcjson-document-specification)
    + [2.1 Required objects, keys, or entities](#21-required-objects--keys--or-entities)
    + [2.2 Empty values, 'userdefined' values, and 'notdefined' values](#22-empty-values---userdefined--values--and--notdefined--values)
    + [2.3 IFC prefix](#23-ifc-prefix)
    + [2.4 Header](#24-header)
    + [2.5 Identifiers](#25-identifiers)
    + [2.6 Tree Structure](#26-tree-structure)
    + [2.7 camelCase, CamelCaps, or snake_case](#27-camelcase--camelcaps--or-snake-case)
    + [2.8 PredefinedTypes and ObjectTypes and Classes](#28-predefinedtypes-and-objecttypes-and-classes)
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

The following criteria are considered to be of less importance, so they are excluded. This IFC.JSON version first and foremost tries to include all that is present in the original IFC EXPRESS schema.

The following criteria are therefore NOT followed:
1.	Human-readability
2.	Integration with code
3.	Clear referencing structure
4.	Direct usability

## 2. ifcJSON Document Specification
In the below sections, a more detailed specification is given for ifcJSON. We don't provide a full schema here, but rather list a number of general principles.

### 2.1 Required objects, keys, or entities
Several elements are required in the IFC Schema. These are recorded also in the IFC JSON Schema and must be followed. You can check whether an IFC schema is valid using any of the freely available validators.

### 2.2 Empty values, 'userdefined' values, and 'notdefined' values
You are free to include empty values, yet you are encouraged to leave them out of the data exchange. The `NOTDEFINED` and `USERDEFINED` Enum elements are maintained and available.

This is valid:

~~~
"Class": "Project",
"GlobalId": "7e8368b59c66436aa047bebfe824ad81",
"Name": "0YvctVUKr0kugbFTf53O9L",
"Description": "",
"ObjectType": null,
"LongName": null,
"Phase": null,
"Type": "NOTDEFINED"
~~~

This is encouraged:

~~~
"Class": "Project",
"GlobalId": "7e8368b59c66436aa047bebfe824ad81",
"Name": "0YvctVUKr0kugbFTf53O9L",
"Type": "NOTDEFINED"
~~~

### 2.3 IFC prefix
The IFC prefix is kept, in order to maintain backwards compatibility.

This is valid:

~~~
IfcWall    
~~~

This is not valid:

~~~
Wall
~~~

### 2.4 Header
A header is included in the IFCJSON file and is a direct translation of the header section in a SPF file.

### 2.5 Identifiers
An object is identified by its GlobalID, which is a UUID according to https://tools.ietf.org/html/rfc4122. The GlobalId property is to be added only to those elements that are descendent of the IfcRoot Class, as is the case in the IFC EXPRESS schema. Literals and geometric items and list hence do not need a GlobalId.

~~~
"GlobalId": "028c968f-687d-484e-9c0a-5048a923b8c4"
~~~

Furthermore, a line number is included, taken from the STEP file if available, and generated otherwise. This line number is used for internal referencing within the IFCJSON file.

~~~
"Class": "Project",
"GlobalId": "7e8368b59c66436aa047bebfe824ad81",
"Name": "0YvctVUKr0kugbFTf53O9L",
"Id": "_00365"
~~~

Objects can be referenced in JSON by using the ref key-value pair. In the example below, a reference is made to the object with internal id `365`.	
 
~~~
"ref": "_00365"
~~~

### 2.6 Tree Structure
Generally, the IFC.JSON structure is flexible. Objects may be nested inline, or referenced using "ref" tag and Id value. It is recommended to use a tree structure (forward downward relationships) as much as possible. All objects that are commonly available in the IFC-SPF file are to be maintained, and relationships are to be included in the same direction. As a result, the tree is relatively flat. Yet, it is recommended to follow the ID structure in the IFCJSON file to obtain the data that you need.

Example:

~~~
[
  {
    "Class": "IfcProject",
    "GlobalId": "cb78a8c2-fb1e-4e12-8f29-6c0d7c39ca0b",
    "Name": "Default Project",
    "Description": "Description of Default Project",
    "Id": "_00365"
  },
  {
    "Class": "IfcSite",
    "GlobalId": "f07e69ce-3709-4ef5-a029-e27de7e95991",
    "Name": "'TU/e campus'",
    "Description": "'The High Tech campus of the Eindhoven University of Technology'",
    "CompositionType": ".ELEMENT.",
    "RefElevation": 0,
    "Id": "_00366"
  },
  {
    "Class": "IfcBuilding",
    "GlobalId": "f3b41796-63ea-4a63-b0aa-f1d7978a6e47",
    "Name": "Vertigo Building",
    "Description": "TU/e Department of the Built Environment",
    "CompositionType": ".ELEMENT.",
    "ElevationOfRefHeight": 0,
    "ElevationOfTerrain": 0,,
    "Id": "_00367"
  },
  {
    "Class": "IfcRelAggregates",
    "Id": "_00368",
    "RelatingObject": {
      "Class": "IfcProject",
      "ref": "_00365"
    },
    "RelatedObjects": [
      {
        "Class": "IfcSite",
        "ref": "_00366"
      }
    ]
  },
  {
    "Class": "IfcRelAggregates",
    "Id": "_00369",
    "RelatingObject": {
      "Class": "IfcSite",
      "ref": "_00366"
    },
    "RelatedObjects": [
      {
        "Class": "IfcBuilding",
        "ref": "_00367"
      }
    ]
  }
]
~~~

### 2.7 camelCase, CamelCaps, or snake_case
Considering that there is no standard notation in JSON, we use the notation standards followed in IFC documentation, which is CamelCaps.

This is valid:
~~~
"GlobalId": "028c968f-687d-484e-9c0a-5048a923b8c4"
~~~

This is not valid:
~~~
"globalId": "028c968f-687d-484e-9c0a-5048a923b8c4"
"global_id": "028c968f-687d-484e-9c0a-5048a923b8c4"
~~~

### 2.8 PredefinedTypes and ObjectTypes and Classes
There are multiple ways to define the object type of an object in the IFC EXPRESS schema. In IFC.JSON, the same structure is followed and you can include type information in the `Class`, `PredefinedType` and `ObjectType` attributes. As indicated in the IFC.JSON schema, the `Class` and `ObjectType` attributes refer to a string. The `Class` attribute is hereby reserved for the IFC class name. The `PredefinedType` attribute is only available for a number of objects, and the allowed values for this attributes are listed in the IFC.JSON schema (identical to EXPRESS schema).

This is valid:
~~~
{
  "Class": "IfcDoor",
  "GlobalId": "f3b96025-a1f3-42a8-b047-b6cc5b1880ff",
  "Name": "A common door",
  "Description": "Description of a standard door",
  "ObjectType" : "IfcDoor",
  "PredefinedType" : ".DOORSUBTYPE."
}
~~~

### 2.9 Geometry
Geometry may be treated in multiple ways. Geometry is included similar to how it was included in the STEP file, thus allowing the inclusion of representation data and units and geometric contexts. Furthermore, it is allowed to include geometry in other formats. 

- Geometry formats: in principle, any geometry description can be used and handled, including OBJ, GTLF, point cloud, STEP, and a potentially scalable set of future geometry types and formats.
- Referencing geometry:
	- Nested inline, embedded in the JSON tree - recommended when including STEP geometry (CSG geometry).
	- Nested inline, with a simple string - recommended for any BREP geometry (triangulated mesh geometry).
	- Referenced elsewhere in the JSON data using a GlobalID
	- Referenced externally by URI

### 2.10 Attributes, Properties and Property Sets
In IFC.JSON, attributes, properties and property sets are included identical to how they are included in the IFC EXPRESS schema. The ifcJSON schema indicates how this can be done (`IfcRelDefinesByProperties`).

## 3. ifcJSON Schema
Like the XSD schema specification and OWL ontology for IFC, also the IFC.JSON schema can be automatically converted from the EXPRESS (ISO 10303 part 1) representation of the IFC schema. Roundtripping conversion from IFC-SPF files to JSON is also possible. Both schema and data conversion are not (yet) available. Yet, an ifcJSON schema is available in this repository and allows to validate which IFC.JSON is valid.

ifcJSON schema defines a structure for what ifcJSON data is required and therefore its schema defines the validation and interaction control of ifcJSON data.

Example ifcJSON data:
~~~
{
  "class": "Wall",
  "globalId": "028c968f-687d-484e-9c0a-5048a923b8c4",
  "name": "my wall",
  "description": "Description of the wall",
  "objectPlacement": { },
  "objectType": "null",
  "representation": { },
  "tag": "267108",
  "id": "_00365",
  "ownerHistory": "null",
  "predefinedType": "null"
}
~~~

Corresponding ifcJSON Schema snippet (validated with above snippet using https://www.jsonschemavalidator.net/):
~~~
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "http://example.com/product.schema.json",
  "title": "Wall",
  "description": "IFC.JSON for Wall",
  "type": "object",
  "properties": {
  "class": "ifcWall",
  "globalId": {
    "type": "string",
    "maxLength": 22
  },
  "id": {
    "type": "string"
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
  },
  "required": ["class", "globalId", "ownerHistory", "name", "description", "objectType", "objectPlacement", "representation", "tag", "predefinedType"]
}
~~~

## 4. More information
Contributions are welcome in all possible ways. Your first starting point is creating GitHub issues. Feel free to get in touch with the people in the IFC.JSON-team.
