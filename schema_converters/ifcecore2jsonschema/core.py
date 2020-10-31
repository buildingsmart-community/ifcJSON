import os
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.sys.path.insert(1, parent_dir)
    import ifcecore
    __package__='ifcecore'
    from ifcecore import core as ecore
    from jsonschema import JsonSchema
    from ifcjsonschema import IfcJsonSchemaEcore

    ifcschemaversion = 'IFC4.3'
    sourcepath = (Path(__file__).parent.parent / 'ifcecore' / 'models' / 'source' / 'uml.xml').resolve()
    targetfolder = (Path(__file__).parent.parent / 'schemas')
    dom = ecore.getxmidom(sourcepath)
    idx = ecore.buildindex(dom)
    pkg = ecore.makepackage(dom, idx)
    jsonschemapath = str((targetfolder / (ifcschemaversion + '-from-ecore.json')).resolve())
    schema = IfcJsonSchemaEcore(pkg, ifcschemaversion)
    schema.save(jsonschemapath)
