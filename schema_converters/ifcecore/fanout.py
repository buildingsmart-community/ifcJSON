"""
Splits an EMFJSON package into a collection of files, one file per EClass

core.py <= :prev  
"""

from pathlib import Path
import json

def fanout(filepath, targetfolder):
    with open(filepath, "r") as inf:
        pkg = json.loads(inf.read())
        for ecls in pkg['eClassifiers']:
            outfile = (targetfolder / (ecls['name'] + '.json')).resolve()
            with open(outfile, 'w') as outf:
                outf.write(json.dumps(ecls, indent=4))


if __name__ == "__main__":
    sourcepath = (Path(__file__).parent / 'models' / 'targets'/ 'ifc-ecore.json').resolve()
    targetfolder = (Path(__file__).parent / 'classes')
    fanout(sourcepath, targetfolder)
