"""
    Different datas used for testing.
"""

import hashlib

__author__ = 'nibo'

test_credential = {"usernamePassword": {"username": "tester", "password": "test"}}

test_user_data = {
    "name": "TestUser",
    "credentials": test_credential,
    "createdWhen": "2014-11-13T01:00:00+00:00",
    "schemaId": "2fb3b2c9-a29c-4fc0-b29d-6eed738b6dab",
    "canRead": ["000000010000010001e64c28"],
    "canWrite": ["000000010000010001e64c28"],
    "groups": ["000000010000010001e64d02"]
}

test_hashed_credential = {
    "usernamePassword": {"username": "tester", "password": hashlib.md5("test".encode('utf-8')).hexdigest()}}

test_hashed_user_data = {
    "name": "TestUser",
    "credentials": test_hashed_credential,
    "createdWhen": "2014-11-13T01:00:00+00:00",
    "schemaId": "2fb3b2c9-a29c-4fc0-b29d-6eed738b6dab",
    "canRead": ["000000010000010001e64c28"],
    "canWrite": ["000000010000010001e64c28"],
    "groups": ["000000010000010001e64d02"]
}

test_find_user_query = {
    "conditions": test_hashed_user_data,
    "collection": "node"
}

test_node = {
    "name": "test_node",
    "createdWhen": "2014-11-13T01:00:00+00:00",
    "parent_id": "000000010000010001e64d40",
    "schemaId": "a9ca8030-6ea4-11e4-9803-0800200c9a66",
    "canRead": ["000000010000010001e64c28", "000000010000010001e64d02"],
    "canWrite": ["000000010000010001e64c28", "000000010000010001e64d02"]
}

test_find_node_query = {
    "conditions": test_node,
    "collection": "node"
}

test_find_node_log_query = {
    "conditions": {"name": "test_node"},
    "collection": "event"

}

test_session_id = None

schemaId_custom = "7a0c71a6-9845-4997-b53d-288989755632"

