# IFC2JSON_python
Python converter from IFC SPF to JSON

# Getting Started

## Requirements
- ifcopenshell (using packagemanager or in folder ./ifcopenshell)

## Usage
```
python ifc2json.py -i model.ifc -o model_-_ifcjson4.json -v 4
```
```
optional arguments:
  -h, --help  show this help message and exit
  -i I        input ifc file path
  -o O        output json file path
  -v V        IFC.JSON version, options: "4"(default), "5a"
```
