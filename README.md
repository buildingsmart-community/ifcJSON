# ifcJSON-4
This repository contains the specification for ifcJSON-4 - version in sync with IFC EXPRESS Schema.

## What
JSON is used throughout the world for exchanging and using data. Building data needs to be available in JSON. Therefore, IFC needs to be available in JSON format. 

ifcJSON aims primarily at addressing the following problems with IFC:
1. Many developers have never seen/used EXPRESS or STP instance files before, which increases the effort required to extract data required from them. 
2. IFC instance populations are typically exchanged as files, which is at odds with linked, distributed, and rapidly changing data seen on most design and construction projects and products.

ifcJSON seeks the best balance between a best practice JSON representation AND compatibility with the IFC source schema.

Main focus:
- Backward compatibility
- Round-trip
- Parallel to EXPRESS schema

To a lesser degree (Due to adhering to the IFC schema):
- Human-readability
- Integration with code
- Clear referencing structure
- Direct usability

The initial standard will be developed based on IFC4 and more specifically IFC4.3.
IFC5 developments will be closely followed, especially for expected improvements in human-readability.

## Getting started
The repository is organised in different sections:
- [Documentation](Documentation): your starting point to find out what this ifcJSON is about
- [Samples](Samples): ifcJSON data examples
- [Schema](Schema): ifcJSON schemas
- [File converters](file_converters): Python tools for reading and converting between ifcJSON and IFC SPF
- [Schema converters](schema_converters): Python tools for converting IFC schemas into JSON-Schema

## More information
Contributions are welcome in all possible ways. Your first starting point is creating GitHub issues. Feel free to get in touch with the people in the ifcJSON-team.
