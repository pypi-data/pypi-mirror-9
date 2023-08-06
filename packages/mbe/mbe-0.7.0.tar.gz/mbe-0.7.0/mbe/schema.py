"""
Created on Mar 6, 2015

@author: Nicklas Boerjesson
@note: The schema tools

"""

from urllib.parse import urlparse
import os
import json

from jsonschema.validators import RefResolver
from jsonschema.exceptions import SchemaError



# strict-rfc3339


from mbe.misc.schema_mongodb import MongodbValidator


class SchemaTools():
    """
        The schema tools class does all the handling, validation and transformation of schemas in MBE.
    """
    # The json_schema_objects keeps the parsed and instantiated schema objects.
    json_schema_objects = None
    # json_schema_folder is the folder of where the json schemas are kept
    json_schema_folders = None
    # TODO: json_schema_folder should probably be an array or something. Anyway there should be a way to plug-in more.

    # An instance of the mongodb JSON validator.
    mongodb_validator = None

    def mbe_uri_handler(self, uri):
        """
        # TODO: Memoize.

        Handle the mbe:// namespace references

        :param uri: The uri to handle
        :return: The schema
        """

        # Use urlparse to parse the file location from the URI
        _file_location = os.path.abspath(os.path.join(self._mbe_schema_folder, urlparse(uri).netloc))

        # noinspection PyTypeChecker
        _schema_file = open(_file_location, "r", encoding="utf-8")
        _json = json.loads(_schema_file.read())
        # Cumbersome, but needs to close the file properly
        _schema_file.close()

        return _json

    # noinspection PyDefaultArgument
    def __init__(self, _json_schema_folders=[]):
        """
        Initiate the SchemaTools class

        :param _json_schema_folders: A list of folders where schema files are stored

        """
        if not _json_schema_folders:
            _json_schema_folders = []

        _resolver = RefResolver(base_uri="",
                                handlers={"mbe": self.mbe_uri_handler}, referrer=None, cache_remote=True)

        self.mongodb_validator = MongodbValidator(resolver=_resolver)

        self.json_schema_objects = {}

        # Load MBE base schemas from the "schemas" subfolder
        self._mbe_schema_folder = os.path.join(os.path.dirname(__file__), 'schemas')
        self.load_schemas_from_directory(self._mbe_schema_folder)

        # Load application specific schemas
        for _curr_folder in _json_schema_folders:
            self.load_schemas_from_directory(os.path.abspath(_curr_folder))
        pass

    @staticmethod
    def check_schema_fields(_curr_schema_obj, _curr_file):
        """ Check so all mandatory fields are in the schema
        :param _curr_schema_obj: Schema to check
        :param _curr_file: File name use in error message

        """

        def raise_field_error(_collection):
            raise Exception("MongoBackend.load_schemas_from_directory: The \"" + _collection + "\"" +
                            " field is not in the schema-\"" + _curr_file + "\"")

        if "collection" not in _curr_schema_obj:
            raise_field_error("collection")
        elif "schemaId" not in _curr_schema_obj:
            raise_field_error("schemaId")
        elif "version" not in _curr_schema_obj:
            raise_field_error("version")

    def load_schema_from_file(self, _file_name):
        """
        Loads a specifield schema from a file, checks it and stores it in the schema cache.

        :param _file_name: The name of the schema file

        """
        try:
            _curr_file = open(_file_name, "r")
        except Exception as e:
            raise Exception("load_schemas_from_directory: Error loading \"" + _file_name +
                            "\": " + str(e))
        try:
            _json_schema_obj = json.load(_curr_file)

        except Exception as e:
            raise Exception("load_schemas_from_directory: Error parsing \"" + _file_name +
                            "\"" + str(e))

        _curr_file.close()

        try:
            self.check_schema_fields(_json_schema_obj, _file_name)
            self.mongodb_validator.check_schema(_json_schema_obj)

        except SchemaError as scherr:
            raise Exception("MongoSchema: Init, schema SchemaError in " + _file_name + " at path:" + str(
                scherr.path) + "\nMessage:\n" + str(scherr.message))
        except Exception as e:
            raise Exception("MongoSchema: Init, schema validation in " + _file_name + ", error :" + str(e))

        self.json_schema_objects[_json_schema_obj["schemaId"]] = _json_schema_obj

    def load_schemas_from_directory(self, _schema_folder):
        """
        Load and validate all schemas in a folder, add to json_schema_objects

        :param _schema_folder: Where to look

        """
        _only_files = [f for f in os.listdir(_schema_folder) if
                       os.path.isfile(os.path.join(_schema_folder, f)) and f[-5:].lower() == ".json"]
        for _file in _only_files:
            self.load_schema_from_file(os.path.join(_schema_folder, _file))

    def apply(self, _data, _schema_id=None):
        """
        Validate the JSON in _data against a JSON schema.

        :param _data: The JSON data to validate
        :param _schema_id: If set, validate against the specified schema, and not the one in the data.
        :return: the schema object that was validated against.

        """
        if _schema_id is not None:
            _json_schema_obj = self.json_schema_objects[_schema_id]
        else:
            _json_schema_obj = self.json_schema_objects[_data["schemaId"]]

        self.mongodb_validator.apply(_data, _json_schema_obj)
        return _data, _json_schema_obj

