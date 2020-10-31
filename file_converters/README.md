# IFC2JSON_python
Python converter from IFC SPF to JSON

# Getting Started

## Requirements
- ifcopenshell (using conda or in folder ./ifcopenshell)

## Installation ifcopenshell using Conda

1. Download the Conda installer for your OS setup. https://docs.conda.io/en/latest/miniconda.html
2. After installing Conda, create an environment for ifcJSON with:
```
conda create --name ifcjson
```
3. Then activate the new environment:
```
conda activate ifcjson
```
4. Install ifcopenshell, and install it from conda-forge:
```
conda install -c conda-forge ifcopenshell
```

## Installation ifcopenshell from direct download
Download a recent copy of ifcopenshell from: https://github.com/IfcOpenBot/IfcOpenShell/commits/v0.6.0

Most commits with a "comment" have links to builds for most platforms and python versions, make sure you pick the 0.6 branch, not master.

## Usage
```
python ifc2json.py -i model.ifc -o model.json
```
```
optional arguments:
  -h, --help  show this help message and exit
  -i I        input ifc file path
  -o O        output json file path
  -v V        ifcJSON version, options: "4"(default), "5a"
```
