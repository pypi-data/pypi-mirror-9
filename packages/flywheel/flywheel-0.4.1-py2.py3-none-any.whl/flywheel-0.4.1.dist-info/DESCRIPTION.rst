Flywheel
========
:Master Build: |build|_ |coverage|_
:Documentation: http://flywheel.readthedocs.org/
:Downloads: http://pypi.python.org/pypi/flywheel
:Source: https://github.com/mathcamp/flywheel

.. |build| image:: https://travis-ci.org/mathcamp/flywheel.png?branch=master
.. _build: https://travis-ci.org/mathcamp/flywheel
.. |coverage| image:: https://coveralls.io/repos/mathcamp/flywheel/badge.png?branch=master
.. _coverage: https://coveralls.io/r/mathcamp/flywheel?branch=master

Object mapper for Amazon's DynamoDB

Getting Started
===============
This is what a basic model looks like (schema taken from this `DynamoDB
API documentation
<http://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html>`_)
::

    from flywheel import Model, Field, GlobalIndex

    class GameScore(Model):
        __metadata__ = {
            'global_indexes': [
                GlobalIndex('GameTitleIndex', 'title', 'top_score')
            ],
        }
        userid = Field(hash_key=True)
        title = Field(range_key=True)
        top_score = Field(data_type=int)
        top_score_time = Field(data_type=datetime)
        wins = Field(data_type=int)
        losses = Field(data_type=int)

        def __init__(self, title, userid):
            self.title = title
            self.userid = userid

Create a new top score::

    >>> score = GameScore('Master Blaster', 'abc')
    >>> score.top_score = 9001
    >>> score.top_score_time = datetime.utcnow()
    >>> engine.sync(score)

Get all top scores for a user::

    >>> scores = engine.query(GameScore).filter(userid='abc').all()

Get the top score for Galaxy Invaders::

    >>> top_score = engine.query(GameScore).filter(title='Galaxy Invaders')\
    ...     .first(desc=True)

Atomically increment a user's "wins" count on Alien Adventure::

    >>> score = GameScore('Alien Adventure', 'abc')
    >>> score.incr_(wins=1)
    >>> engine.sync(score)

Get all scores on Comet Quest that are over 9000::

    >>> scores = engine.query(GameScore).filter(GameScore.top_score > 9000,
    ...                                         title='Comet Quest').all()


Changelog
=========
0.4.1
-----
* **Warning**: Stored datetime objects will now be timezone-aware 
* **Warning**: Stored datetime objects will now keep their microseconds 

0.4.0
-----
* **Breakage**: Dropping support for python 3.2 due to lack of botocore support
* **Breakage**: Changing the ``list``, ``dict``, and ``bool`` data types to use native DynamoDB types instead of JSON serializing
* **Breakage** and bug fix: Fixing serialization of ``datetime`` and ``date`` objects (for more info see the commit) 
* Feature: Can now do 'contains' filters on lists
* Feature: Fields support multiple validation checks
* Feature: Fields have an easy way to enforce non-null values (``nullable=False``)

Data type changes are due to an `update in the DynamoDB API
<https://aws.amazon.com/blogs/aws/dynamodb-update-json-and-more/>`_

0.3.0
-----
* **Breakage**: Engine namespace is slightly different. If you pass in a string it will be used as the table name prefix with no additional '-' added.

0.2.1
-----
* **Breakage**: Certain queries may now require you to specify an index where it was auto-detected before
* Feature: Queries can now filter on non-indexed fields
* Feature: More powerful "sync-if" constraints
* Feature: Can OR together filter constraints in queries

All changes are due to an `update in the DynamoDB API
<http://aws.amazon.com/blogs/aws/improved-queries-and-updates-for-dynamodb/>`_

0.2.0
-----
* **Breakage**: Engine no longer accepts boto connections (using dynamo3 instead)
* **Breakage**: Removing S3Type (no longer have boto as dependency)
* Feature: Support Python 3.2 and 3.3
* Feature: ``.count()`` terminator for queries 
* Feature: Can override throughputs in ``Engine.create_schema()`` 
* Bug fix: Engine ``namespace`` is truly isolated 

0.1.3
-----
* Bug fix: Some queries fail when global index has no range key 

0.1.2
-----
* Bug fix: Field names can begin with an underscore 
* Feature: Models have a nice default __init__ method 

0.1.1
-----
* Bug fix: Can call ``incr_()`` on models that have not been saved yet 
* Bug fix: Model comparison with ``None`` 

0.1.0
-----
* First public release


