"""
    Initialization for MBE tests.
"""

import os

from mbe.misc.init import init_database
from mbe.node import Node

__author__ = 'nibo'

from mbe.authentication import init_authentication


# Test users uuids
object_id_user_root = "000000010000010001e64c30"
object_id_user_test = "000000010000010001e64c31"
object_id_user_testagent = "000000010000010001e64c32"

object_id_right_admin_nodes = "000000010000010001e64d01"

script_dir = os.path.dirname(__file__)

def before_feature(context, feature):
    """

    Initialisation for all features.

    :param context:
    :param feature:
    :return:

    """

    context.db_access = init_database("test_MBE", _data_files=[os.path.abspath(os.path.join(script_dir, "data/init_data.json"))],
                                      _json_schema_folders=[os.path.abspath(os.path.join(script_dir, "schemas"))])

    context.auth = init_authentication(context.db_access)

    if feature.name == "Node management":
        context.node = Node(_database_access=context.db_access, _rights=[object_id_right_admin_nodes])

