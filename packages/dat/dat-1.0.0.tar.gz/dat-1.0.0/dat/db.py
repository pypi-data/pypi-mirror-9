from pymongo import MongoClient, MongoReplicaSetClient, ASCENDING, DESCENDING
from pymongo.errors import OperationFailure
from .utils import classproperty
from .exceptions import MultipleObjectsExist, DoesNotExist, QueryError

import os
import sys
import logging

logger = logging.getLogger(__name__)

# keep this stuff super secret
DAT_REPLICA_SET_URI = os.environ.get('DAT_REPLICA_SET_URI')
DAT_REPLICA_SET_NAME = os.environ.get('DAT_DATABASE_NAME')
# E.G.
# DAT_REPLICA_SET_URI = (
#     "mongodb://<USER_NAME>:<PASSWORD>@<URI_1>:<PORT_1>,<URI_2>:<PORT_2>/"
#     "<DATABASE_NAME>"
# )
# DAT_REPLICA_SET_NAME = "set-<UID_HASH>"


DATABASE_NAME = os.environ.get('DAT_DATABASE_NAME', 'dat')

if DAT_REPLICA_SET_URI and DAT_REPLICA_SET_NAME:
    mongo_client = MongoReplicaSetClient(
        DAT_REPLICA_SET_URI, replicaSet=DAT_REPLICA_SET_NAME
    )
else:
    mongo_client = MongoClient()

BSON_TYPES = {
    'Double': 1,
    'String': 2,
    'Object': 3,
    'Array': 4,
    'Binary': 5,
    'Undefined': 6,
    'ObjectId': 7,
    'Boolean': 8,
    'Date': 9,
    'Null': 10,
    'RegEx': 11,
    'JavaScript': 13,
    'Symbol': 14,
    'JavaScript': 15,
    'Integer32': 16,
    'Timestamp': 17,
    'Integer64': 18,
    'MinKey': 255,
    'MaxKey': 127
}


def getUniqueInnerKeys(document):
    unique_names = set()
    for key, dct in document.items():
        unique_names.add(*dct.keys())
    return unique_names


def parseUpdateKwargs(kwargs):
    for key, value in kwargs.items():
        if '__' in key:
            raise ValueError(
                'dat.db.QuerySet.update does not support alternate operators '
                'or modifiers via keyword arguments. Unsupported: %s' % key
            ), None, sys.exc_info()[2]
    return {'$set': kwargs}


class QuerySet(object):

    def __repr__(self):
        return '<QuerySet(%s, %s, %s, limit=%s)>' % (
            self.model_class.__name__,
            self.conditions,
            self.projection,
            self._limit
        )

    def __init__(self, model_class, conditions, projection, limit=None):
        self.conditions = conditions
        self.projection = projection
        self.model_class = model_class
        self._limit = limit

    def serialize(self, to_json=False):
        return [instance.serialize(to_json=to_json) for instance in self]

    def filter(
        self, conditions=None, projection=None, include=None, exclude=None,
        limit=None
    ):
        # busts _cursor
        conditions = conditions or {}
        projection = projection or {}
        self.conditions.update(conditions)
        if self.projection is None and projection:
            self.projection = {}
        if projection:
            self.projection.update(
                DatabaseInterface.parseProjections(
                    projection, include=include, exclude=exclude
                )
            )
        self._clear()
        return self

    def _clear(self):
        if hasattr(self, '_cursor'):
            del self._cursor
        if hasattr(self, '_cache'):
            del self._cache

    @property
    def cursor(self):
        if not hasattr(self, '_cursor'):
            self._cursor = self.model_class.collection.find(
                self.conditions, self.projection
            )
            if hasattr(self, '_limit') and self._limit:
                self._cursor = self._cursor.limit(self._limit)
            if hasattr(self, '_hint') and self._hint:
                self._cursor = self._cursor.hint(self._hint)
            if hasattr(self, '_sort') and self._sort:
                self._cursor = self._cursor.sort(*self._sort)
            if hasattr(self, '_skip') and self._skip:
                self._cursor = self._cursor.skip(self._skip)
        return self._cursor

    def skip(self, value):
        self._skip = value
        if hasattr(self, '_cursor'):
            del self._cursor
        return self

    def limit(self, value):
        self._limit = value
        self._clear()
        return self

    def sort(self, key_or_list, direction=ASCENDING):
        self._sort = (key_or_list, direction)
        self._clear()
        return self

    def hint(self, field):
        self._hint = field
        self._clear()
        return self

    def distinct(self, key_or_list):
        return self.cursor.distinct(key_or_list)

    def __iter__(self):
        cursor = self.cursor.clone()
        try:
            for document in cursor:
                yield self.model_class(_from_db=True, **document)
        except OperationFailure, e:
            raise QueryError(e.details.get('$err')), None, sys.exc_info()[2]

    def __getitem__(self, index):
        try:
            if not hasattr(self, '_cache'):
                self._cache = tuple(self)
            return self._cache[index]
        except OperationFailure, e:
            raise QueryError(e.details.get('errmsg')), None, sys.exc_info()[2]

    def __len__(self):
        return self.count(with_limit_and_skip=True)

    def count(self, with_limit_and_skip=False):
        return self.cursor.count(with_limit_and_skip=with_limit_and_skip)

    def exists(self):
        return bool(self.count(with_limit_and_skip=True))

    def update(
        self, document=None, multi=True, upsert=False,
        getUniqueInnerKeys=getUniqueInnerKeys,
        parseUpdateKwargs=parseUpdateKwargs, **kwargs
    ):
        """
        SINGLE VALUE FIELDS
        $currentDate    - Sets the value of a field to current date, either
                          as a Date or a Timestamp.
        $inc	        - Increments the value of the field by the specified
                          amount.
        $max	        - Only updates the field if the specified value is
                          greater than the existing field value.
        $min	        - Only updates the field if the specified value is
                          less than the existing field value.
        $mul	        - Multiplies the value of the field by the specified
                          amount.
        $rename	        - Renames a field.
        $setOnInsert	- Sets the value of a field if an update results in an
                          insert of a document. Has no effect on update
                          operations that modify existing documents.
        $set	        - Sets the value of a field in a document.
        $unset	        - Removes the specified field from a document.

        LIST/SET FIELDS
        $               - Acts as a placeholder to update the first element
                          that matches the query condition in an update.
        $addToSet       - Adds elements to an array only if they do not already
                          exist in the set.
        $pop            - Removes the first or last item of an array.
        $pullAll        - Removes all matching values from an array.
        $pull           - Removes all array elements that match a specified
                          query.
        $pushAll        - Deprecated. Adds several items to an array.
        $push           - Adds an item to an array.

        LIST MODIFIERS
        $each           - Modifies the $push and $addToSet operators to append
                          multiple items for array updates.
        $position       - Modifies the $push operator to specify the position
                          in the array to add elements.
        $slice          - Modifies the $push operator to limit the size of
                          updated arrays.
        $sort           - Modifies the $push operator to reorder documents
                          stored in an array.
        """
        document = document or {}
        if document and kwargs:
            raise ValueError(
                'Unsupported method input: using both a dictionary and kwargs '
                'is not supported. Please use %s or %s.' % (document, kwargs)
            ), None, sys.exc_info()[2]
        elif kwargs:
            document.update(parseUpdateKwargs(kwargs))
        elif not document:
            raise ValueError(
                'Either supply a mongo-like document with operators and '
                'modifiers, or a series of keyword arguements to be set.'
            ), None, sys.exc_info()[2]

        # maintain the integrity of the data schema by checking if the user has
        # tried to insert a new field to the found documents.
        actual_fieldnames = set(self.model_class.meta.fields.keys())
        doc_fieldnames = getUniqueInnerKeys(document)
        wrong_fieldnames = tuple(doc_fieldnames - actual_fieldnames)
        if wrong_fieldnames:
            raise ValueError(
                'Could not find the fields %s in the list of %r\'s fields: '
                '%s' % (
                    wrong_fieldnames,
                    self.model_class,
                    tuple(actual_fieldnames)
                )
            )

        acknowledgement = self.model_class.collection.update(
            self.conditions, document, multi=multi, upsert=upsert, **kwargs
        )
        logger.debug(acknowledgement)
        return self


class DatabaseInterface(object):
    """
    A mixin interface for models to connect with the database. It contains both
    class methods and instance methods to allow the user to update one or many
    documents in the .
    """

    MultipleObjectsExist = MultipleObjectsExist
    DoesNotExist = DoesNotExist
    QueryError = QueryError
    ASCENDING = ASCENDING
    DESCENDING = DESCENDING

    queryFactory = QuerySet
    _client = mongo_client

    @classproperty
    def _db(cls):
        return cls._client[DATABASE_NAME]

    @classproperty
    def collection(cls):
        if hasattr(cls, 'collection_name'):
            collection_name = cls.collection_name
        else:
            collection_name = cls.__name__.lower()
        return cls._db[collection_name]

    ###########################################################################
    # helper methods - cleaning developer input
    @classmethod
    def parseProjections(cls, projection, include=None, exclude=None):
        include = include or []
        exclude = exclude or []
        for field in include:
            projection[field] = 1
        for field in exclude:
            projection[field] = 0
        return projection

    @classmethod
    def parseConditions(cls, **kwargs):
        conditions = {}
        for key, value in kwargs.items():
            if not key:
                raise QueryError(
                    'Field name must be specified on a query, it may not be an'
                    'empty string or begin with "__".'
                ), None, sys.exc_info()[2]
            parts = key.split('__')
            num_parts = len(parts)
            if num_parts == 1:
                conditions[key] = value
            elif num_parts == 2:
                field, modifier = parts
                conditions[field] = {'$%s' % modifier: value}
            elif num_parts > 2:
                raise QueryError(
                    'Two occurrences of "__" is not supported in query '
                    'statements.'
                ), None, sys.exc_info()[2]
        return conditions

    ###########################################################################
    # Class methods to create and retrieve data
    @classmethod
    def bulk_create(cls, model_list):
        bulkop = cls.collection.initialize_unordered_bulk_op()
        for model in model_list:
            bulkop.insert(model.serialize())
        ack = bulkop.execute()
        logger.debug(ack)
        return len(model_list)

    @classmethod
    def create(cls, **data):
        """
        a convenience method that inserts the document without hitting the save
        method
        """
        model = cls(**data)
        _id = cls.collection.insert(model.serialize())
        model._id = _id
        model._from_db = True
        return model

    @classmethod
    def get(
        cls, conditions=None, projection=None, include=None, exclude=None,
        *args, **kwargs
    ):
        conditions = conditions or {}
        if kwargs:
            conditions.update(cls.parseConditions(**kwargs))
        projection = projection or {}
        projection = cls.parseProjections(
            projection, include=include, exclude=exclude
        )
        projection = projection or None
        cursor = cls.collection.find(conditions, projection)
        if cursor.count() > 1:
            raise MultipleObjectsExist(
                '%r.get returned multiple instances for the given conditions:'
                '\n%s' % (cls, conditions)
            ), None, sys.exc_info()[2]
        try:
            return cls(_from_db=True, _conditions=conditions, **cursor[0])
        except IndexError, e:
            logger.debug(str(e))
            raise DoesNotExist(
                '%r.get could not find an instance matching the '
                'given conditions:\n%s' % (cls, conditions)
            ), None, sys.exc_info()[2]

    @classmethod
    def filter(
        cls, conditions=None, projection=None, include=None, exclude=None,
        limit=None, *args, **kwargs
    ):
        """
        Returns a QuerySet which does not execute the cursor until a method
        that calls __iter__ is used. filters can be daisy chained and modified
        to include hints, sort, distinct, limit

        VALUE CONDITIONS
        $gt     - Matches values that are greater than the value specified in
                  the query.
        $gte	- Matches values that are greater than or equal to the value
                  specified in the query.
        $in	    - Matches any of the values that exist in an array specified in
                  the query.
        $lt	    - Matches values that are less than the value specified in the
                  query.
        $lte	- Matches values that are less than or equal to the value
                  specified in the query.
        $ne	    - Matches all values that are not equal to the value specified
                  in the query.
        $nin	- Matches values that do not exist in an array specified to the
                  query.

        ARRAY CONDITIONS
        $all        - Matches arrays that contain all elements specified in the
                      query.
        $elemMatch	- Selects documents if element in the array field matches
                      all the specified $elemMatch condition.
        $size       - Selects documents if the array field is a specified size.

        PROJECTIONS
        $           - Projects the first element in an array that matches the
                      query condition.
        $elemMatch	- Projects the first element in an array that matches the
                      specified $elemMatch condition.
        $meta       - Projects the document's score assigned during $text
                      operation.
        $slice      - Limits the number of elements projected from an array.
                      Supports skip and limit slices.

        ELEMENT
        $exists     - Matches documents that have the specified field.
        $type       - Selects documents if a field is of the specified type.

        LOGICAL
        $and	- Joins query clauses with a logical AND returns all documents
                  that match the conditions of both clauses.
        $nor	- Joins query clauses with a logical NOR returns all documents
                  that fail to match both clauses.
        $not	- Inverts the effect of a query expression and returns
                  documents that do not match the query expression.
        $or     - Joins query clauses with a logical OR returns all documents
                  that match the conditions of either clause.

        GEOSPATIAL
        $geoIntersects	- Selects geometries that intersect with a GeoJSON
                          geometry.
        $geoWithin      - Selects geometries within a bounding GeoJSON geometry
        $nearSphere     - Returns geospatial objects in proximity to a point on
                          a sphere.
        $near           - Returns geospatial objects in proximity to a point.
        """
        conditions = conditions or {}
        if kwargs:
            conditions.update(cls.parseConditions(**kwargs))
        projection = projection or {}
        projection = cls.parseProjections(
            projection, include=include, exclude=exclude
        )
        projection = projection or None
        return cls.queryFactory(cls, conditions, projection, limit=limit)

    @classmethod
    def all(cls, projection=None, include=None, exclude=None):
        "a convenience method that returns all documents in a collection"
        projection = projection or {}
        projection = cls.parseProjections(
            projection, include=include, exclude=exclude
        )
        projection = projection or None
        return cls.queryFactory(cls, {}, projection)

    ###########################################################################
    # Instance Methods
    def save(self, **kwargs):
        "saves the model document and sets _from_db to True"
        document = self.serialize()
        _id = self.collection.save(document, **kwargs)
        self._id = _id
        self._from_db = True
        return self
