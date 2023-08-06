Changelog
=========
0.3.2
-----
* Bug fix: Serialization of blobs broken with botocore 0.85.0

0.3.1
-----
* Bug fix: Crash when parsing description of table being deleted

0.3.0
-----
* **Breakage**: Dropping support for python 3.2 due to lack of botocore support
* Feature: Support JSON document data types
Features thanks to DynamoDB upgrades: https://aws.amazon.com/blogs/aws/dynamodb-update-json-and-more/

0.2.2
-----
* Tweak: Nose plugin allows setting region when connecting to DynamoDB Local

0.2.1
-----
* Feature: New, unified ``connect`` method

0.2.0
-----
* Feature: More expressive 'expected' conditionals
* Feature: Queries can filter on non-indexed fields
* Feature: Filter constraints may be OR'd together
Features thanks to DynamoDB upgrades: http://aws.amazon.com/blogs/aws/improved-queries-and-updates-for-dynamodb/

0.1.3
-----
* Bug fix: sometimes crash after deleting table
* Bug fix: DynamoDB Local nose plugin fails

0.1.2
-----
* Bug fix: serializing ints fails

0.1.1
-----
* Feature: Allow ``access_key`` and ``secret_key`` to be passed to the ``DynamoDBConnection.connect_to_*`` methods

0.1.0
-----
* First public release
