# BuildingSMART Test set
The files in this directory are converted with the JAVA-based converter in https://github.com/pipauwel/IFC.JAVA/. 

The original SPF files (.ifc) are:
- collected from https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/ (section E - examples)
- corrected so that they are valid ifc files
- parsed into a JAVA-based object model
- serialised into XML and JSON using the Jackson library (https://en.wikipedia.org/wiki/Jackson_(API))

In this particular conversion procedure, we stayed as close as possible to the EXPRESS schema of IFC and STEP files, implying that all basic data types are wrapped into IFC-specific objects (e.g. IfcInteger), for example. Alternative conversion procedures are also possible, and recommended for particular use case scenario's.

