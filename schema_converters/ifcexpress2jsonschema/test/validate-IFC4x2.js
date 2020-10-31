'use strict';

const fs = require('fs');
var jsonlint = require('jsonlint');
var Ajv = require('ajv');
var ajv = new Ajv({ allErrors: true });

var schemaPath = '../IFC4x2.json'
var schemaPathTypes = '../IFC4x2-types.json'
var schemaPathEntities = '../IFC4x2-entities.json'

ajv.addSchema(require(schemaPath), 'IFC4x2');
ajv.addSchema(require(schemaPathTypes), 'types');
ajv.addSchema(require(schemaPathEntities), 'entities');

const ifcJsonFile = './7m900_tue_hello_wall_with_door_4.json'

fs.readFile(schemaPath, "utf8", function (err, data) {
    if (err) throw err;
    var valid = jsonlint.parse(data);
    if (valid) console.log('Schema ifcJSON Valid!');
    else console.log('Schema ifcJSON Invalid');
});
fs.readFile(schemaPathTypes, "utf8", function (err, data) {
    if (err) throw err;
    var valid = jsonlint.parse(data);
    if (valid) console.log('Schema types Valid!');
    else console.log('Schema types Invalid');
});
fs.readFile(schemaPathEntities, "utf8", function (err, data) {
    if (err) throw err;
    var valid = jsonlint.parse(data);
    if (valid) console.log('Schema entities Valid!');
    else console.log('Schema entities Invalid');
});
fs.readFile(ifcJsonFile, "utf8", function (err, data) {
    if (err) throw err;
    var ifcJson = JSON.parse(data);
    validateifcJSON(ifcJson);
});


function validateifcJSON(data) {
    var valid = ajv.validate('IFC4x2', data);
    if (valid) console.log('IFC JSON file Valid!');
    else console.log('IFC JSON file Invalid: ' + ajv.errorsText(ajv.validate.errors));
}