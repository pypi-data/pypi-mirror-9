"""
     The access module contains features providing an abstraction layer over MongoDB.
"""

import copy

from bson import ObjectId
from jsonschema.exceptions import ValidationError

from mbe.constants import schemaId_conditions
from mbe.logging import Logging
from mbe.schema import SchemaTools

__author__ = 'nibo'


class DatabaseAccess():
    """
        The database access class handles all communication with the database
        It provides logging, validation against a schema and hiding ObjectIds.
    """

    database = None
    schema_tools = None
    logging = None

    def __init__(self, _database, _json_schema_folders=None):
        """
        Initialize a database access object
        :param _database: A MongoDB client object
        :param _json_schema_folders: A list of application specific JSON schema folders

        """

        self.database = _database

        self.logging = Logging(_database=self.database)

        # Database access is dependent on schema tools for validation.
        self.schema_tools = SchemaTools(_json_schema_folders)

    def verify_document(self, _data, _collection_name, _caller_name):
        """
        Check so that the collection for the specified schema in the input data match the supplied collection in
        _collection_name.

        :param _data: The data to check.
        :param _collection_name: Name of the collection that it should be checked against
        :param _caller_name: The name of the calling function for logging


        """

        if "schemaId" in _data:
            try:
                _curr_schema = self.schema_tools.json_schema_objects[_data["schemaId"]]
            except:
                raise Exception(
                    _caller_name + ": Error - invalid data structure, schemaId not found: " + _data["schemaId"])

            if _curr_schema["collection"] != _collection_name:
                raise Exception(
                    _caller_name + ": Invalid schemaId. " + _caller_name + " is restricted to the   \"" +
                    _collection_name + "\"-collection.")
        else:
            # An MBE document must *always* have a schemaId property
            raise Exception(_caller_name + ": Missing schemaId.")

    @staticmethod
    def verify_condition(_data, _collection_name, _caller_name):
        """
        Validates the conditions' structure and the collection it queries.

        :param _data: The data to check.
        :param _collection_name: Name of the collection that it should be checked against
        :param _caller_name: The name of the calling function for logging

        """

        if "conditions" not in _data:
            raise Exception(_caller_name + ": Error - Not a valid condition, \"conditions\"-property missing")

        if "collection" in _data and _data["collection"] != _collection_name:
            raise Exception(_caller_name + ": Error - collection omitted or wrong, only queries against"
                                           " the " + _collection_name + " collection is permitted.")

    def manage_input(self, _input, _schema_id=None):
        """
        Validate, convert _id to objectId instances and parse collection from input, whether it is data to save or a\
        condition.
        Note: This should not be run twice on the same data.

        :param _input: Data to handle
        :param _schema_id: If set the schema to validate against
        :return: A tuple with the data and the database collection specified in the schema.

        """
        try:
            # Apply(if _schema_id is set, validate against that schema instead)
            _input, _schema_obj = self.schema_tools.apply(_input, _schema_id)
        except ValidationError as e:
            raise ValidationError("handle_input: Validation error:" + str(e) + ". Data: \n" + str(_input))
        except Exception as e:
            raise Exception(
                "handle_input: Non-validation error from validation: Type: " + e.__class__.__name__ + " Message:" + str(
                    e) + ". Data: \n" + str(_input))

        # In a condition, the input data is under the conditions-field
        if _schema_id == schemaId_conditions:
            _data = copy.deepcopy(_input["conditions"])
            _collection = _input["collection"]
        else:
            _collection = _schema_obj["collection"]
            _data = copy.deepcopy(_input)

        return _data, self.database[_collection]

    @staticmethod
    def load_exactly_one_document(_collection, _id, _zero_error=None, _duplicate_error=None):
        """
        Raises provided errors if not exactly one row in result.

        :param _collection: The collection to load from
        :param _id: The _id of the document
        :param _zero_error: Error to report if no documents are found
        :param _duplicate_error: Error to report when duplicate documents are found
        :return: The document
        """

        _document_cursor = _collection.find({"_id": _id})
        if _document_cursor.count() == 0:
            if _zero_error is not None:
                raise Exception(_zero_error + "_id: " + str(
                    _id) + " could not be found.")
            else:
                return None
        elif _document_cursor.count() > 1:
            if _duplicate_error is not None:
                raise Exception(
                    "Access.save: Tried saving existing, but found duplicate documents with(try to remove either) _id: "
                    + str(_id) + ".")
            else:
                return None
        elif _document_cursor.count() == 1:
            return _document_cursor[0]

    def save(self, _document, _user, _old_document=None, _allow_save_id=False):
        """
        Save a document to a collection

        :param _document: The data to save
        :param _user: A user object
        :param _old_document: If available, the existing data, used to avoid an extra read when logging changes.
        :param _allow_save_id: If set, to not assume that _id being set means updating an existing document.
        :return: The object id of the saved document

        """
        if _user is not None:
            _user_id = _user["_id"]
        else:
            _user_id = None

        _document, _collection = self.manage_input(_document)

        if _old_document is None and "_id" in _document:
            # Load the existing data
            if not _allow_save_id:
                _zero_error = "Access.save: Tried to save data over existing but didn't find an existing node."
            else:
                _zero_error = None

            _old_document = self.load_exactly_one_document(_collection, _document["_id"], _zero_error=_zero_error,
                                                           _duplicate_error="Access.save: Tried to save data over "
                                                                            "existing but found duplicate nodes")
            if (_old_document is not None) and (str(_old_document["schemaId"]) != str(_document["schemaId"])):
                raise Exception(
                    "Access.save: Cannot change schema of an existing node, remove and add. _id: " + str(
                        _document["_id"]) + ", new:" + str(_old_document["schemaId"]) + ", old:" + str(
                        _old_document["schemaId"]))

        if _old_document is not None:
            _old_document, _dummy_collection = self.manage_input(_old_document)

        _result = str(_collection.save(_document))
        self.logging.log_save(_document, _user_id, _old_document)
        return _result

    def remove_documents(self, _documents, _user, _collection_name=None):
        """
        Remove the documents in the documents lis

        :param _documents: The list of documents
        :param _user: A user object
        :param _collection_name: The collection from where to remove them.
        :return: Nothing
        """
        if _user is not None:
            _user_id = _user["_id"]
        else:
            _user_id = None
        _result = []
        # Loop through documents and remove them
        _collection = self.database[_collection_name]
        for _document in _documents:
            # noinspection PyUnusedLocal
            _result.append(_collection.remove(_document))

            self.logging.log_remove(_document, _user_id)

        return _result

    def remove_condition(self, _condition, _user):
        """
        Remove documents that match the supplied MBE condition

        :param _condition: A MongoDB search criteria
        :return:
        """
        if _user is not None:
            _user_id = _user["_id"]
        else:
            _user_id = None
        _raw_condition, _collection = self.manage_input(_condition, schemaId_conditions)
        _removed_documents_cursor = _collection.find(_raw_condition)

        _documents = [x for x in _removed_documents_cursor]
        _result = []
        for _document in _documents:
            # noinspection PyUnusedLocal
            _result.append(_collection.remove(_raw_condition))
            self.logging.log_remove(_document, _user_id)

        return _result

    def find(self, _conditions, _do_not_fix_object_ids=False):
        """
        Return a list of documents that match the supplied MBE condition.
        :param _conditions: An MBE condition
        :return: A list of matching documents
        """

        def _recurse_object_ids(_data):

            if isinstance(_data, list):
                _destination = []
                for _curr_row in _data:
                    _destination.append(_recurse_object_ids(_curr_row))

                return _destination
            elif isinstance(_data, dict):
                _destination = {}
                for _curr_key, _curr_value in _data.items():
                    _destination[_curr_key] = _recurse_object_ids(_curr_value)
                return _destination

            elif isinstance(_data, ObjectId):
                return str(_data)
            else:
                return _data

        _raw_conditions, _collection = self.manage_input(_conditions, schemaId_conditions)
        _result = list(_collection.find(_raw_conditions))
        if not _do_not_fix_object_ids:
            return _recurse_object_ids(_result)
        else:
            return _result

    # noinspection PyMethodMayBeStatic
    def transform_collection(self, _destination_schema, _map, _row_callback):
        """
        NOT IMPLEMENTED.
        :param _destination_schema:
        :param _map:
        :param _row_callback:
        :return:
        """

        pass
        # Iterate all documents

        # Copy _id to new document
        # Copy all data using map and field id:s to document
        # If set, use callback to finish what has to be manually done


        # Write cumulative log entry using map changes and results from _row_callback