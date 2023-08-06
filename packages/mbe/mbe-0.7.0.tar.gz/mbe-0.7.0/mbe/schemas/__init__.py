"""
In schemas, all the built-in schemas of MBE is stored.

MBE schemas have the following custom properties outside the normal JSON schemas:
* objectId : a property marked with that will be considered a MongoDB objectId and will be converted.
* collection: The collection tells the system where the data is headed
* schemaId: The schemaId tells the system what the schemaId of the schema is.  1).


1) There is also a schemaId in all JSON data that enters the system . It tells the system what a packet of data claims
to contain. If the packet states a certain schemaId, it has to conform to that definition and can only end up where
the collection custom property in the schema says it your end up.
That is, if the user has the permission to write there.
"""

__author__ = 'nibo'
