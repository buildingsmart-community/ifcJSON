import ifcopenshell
import json

ifc_file = ifcopenshell.open('./samples/7m900_tue_hello_wall_with_door.ifc')
schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(ifc_file.schema)
id_objects = {}

def entityToDict(entity):
    ref = {
        "Type": entity.is_a()
    }
    attr_dict = entity.__dict__

    # check for globalid
    if "GlobalId" in attr_dict:
        ref["ref"] = attr_dict["GlobalId"]
        if not attr_dict["GlobalId"] in id_objects:
            d = {
                "Type": entity.is_a()
            }

            for i in range(0,len(entity)):
                attr = entity.attribute_name(i)
                if attr in attr_dict:
                    if not attr == "OwnerHistory":
                        jsonValue = getEntityValue(attr_dict[attr])
                        if jsonValue:
                            d[attr] = jsonValue
                        if attr_dict[attr] == None:
                            continue
                        elif isinstance(attr_dict[attr], ifcopenshell.entity_instance):
                            d[attr] = entityToDict(attr_dict[attr])
                        elif isinstance(attr_dict[attr], tuple):
                            subEnts = []
                            for subEntity in attr_dict[attr]:
                                if isinstance(subEntity, ifcopenshell.entity_instance):
                                    subEntJson = entityToDict(subEntity)
                                    if subEntJson:
                                        subEnts.append(subEntJson)
                                else:
                                    subEnts.append(subEntity)
                            if len(subEnts) > 0:
                                d[attr] = subEnts
                        else:
                            d[attr] = attr_dict[attr]
            id_objects[attr_dict["GlobalId"]] = d
        return ref
    else:
        d = {
            "Type": entity.is_a()
        }

        for i in range(0,len(entity)):
            attr = entity.attribute_name(i)
            if attr in attr_dict:
                if not attr == "OwnerHistory":
                    jsonValue = getEntityValue(attr_dict[attr])
                    if jsonValue:
                        d[attr] = jsonValue
                    if attr_dict[attr] == None:
                        continue
                    elif isinstance(attr_dict[attr], ifcopenshell.entity_instance):
                        d[attr] = entityToDict(attr_dict[attr])
                    elif isinstance(attr_dict[attr], tuple):
                        subEnts = []
                        for subEntity in attr_dict[attr]:
                            if isinstance(subEntity, ifcopenshell.entity_instance):
                                # subEnts.append(None)
                                subEntJson = entityToDict(subEntity)
                                if subEntJson:
                                    subEnts.append(subEntJson)
                            else:
                                subEnts.append(subEntity)
                        if len(subEnts) > 0:
                            d[attr] = subEnts
                    else:
                        d[attr] = attr_dict[attr]
        return d

def getEntityValue(value):
    if value == None:
        jsonValue = None
    elif isinstance(value, ifcopenshell.entity_instance):
        jsonValue = entityToDict(value)
    elif isinstance(value, tuple):
        jsonValue = None
        subEnts = []
        for subEntity in value:
            subEnts.append(getEntityValue(subEntity))
        jsonValue = subEnts
    else:
        jsonValue = value
    return jsonValue


jsonObjects= []
entityIter = iter(ifc_file)
for entity in entityIter:
    entityToDict(entity)
for key in id_objects:
    jsonObjects.append(id_objects[key])
with open('7m900_tue_hello_wall_with_door.json', 'w') as outfile:
    json.dump(jsonObjects, outfile, indent=4)