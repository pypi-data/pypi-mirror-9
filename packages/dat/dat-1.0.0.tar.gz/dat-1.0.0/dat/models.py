from collections import defaultdict
from .fields import Field, Id
from .db import DatabaseInterface, mongo_client, DATABASE_NAME

import json
import logging
import pymongo


logger = logging.getLogger(__name__)


MAX_LIST_LENGTH = 3


class ModelRegistry(object):

    def __init__(self):
        self.models = {}

    def load(self, app_label, model_name):
        app_label = app_label.lower()
        model_name = model_name.lower()
        return self.models.get(app_label, {}).get(model_name)

    def register(self, app_label, model_name, model):
        app_label = app_label.lower()
        model_name = model_name.lower()
        if app_label in self.models:
            app_models = self.models.get(app_label)
            if model_name in app_models:
                return
            else:
                self.models[app_label][model_name] = model
        else:
            self.models[app_label] = {model_name: model}


cache = ModelRegistry()
load = cache.load
register = cache.register


def indexField(collection, name, field):
    if field.index or field.unique:
        kwargs = {}
        index = field.index if field.index else pymongo.ASCENDING
        kwargs['unique'] = field.unique
        kwargs['background'] = field.background
        kwargs['sparse'] = field.sparse
        if index == pymongo.GEO2D:
            kwargs['min'] = field.geo_min
            kwargs['max'] = field.geo_max
        if field.unique:
            kwargs['dropDups'] = field.drop_dups

        collection.create_index([(name, index), ], **kwargs)


def parseCompoundIndex(index):
    idx = []
    for elm in index:
        if isinstance(elm, (list, tuple)):
            idx += elm
        else:
            idx += [(elm, pymongo.ASCENDING), ]
    return idx


class Meta(object):

    def __init__(self, field_list):
        self.fields = {}
        self.fieldmap = defaultdict(list)
        for name, field in field_list:
            setattr(self, name, field)
            self.fields[name] = field
            self.fieldmap[field.__class__].append(name)
        self.fieldmap = dict(self.fieldmap)


class ModelBaseMeta(type):

    def __new__(cls, classname, bases, classDict):

        app_label = bases[0].__module__.split('.')[-2]

        # check the registry and exit if found
        model = load(app_label, classname)
        if model:
            return model

        # find fields from all base classes of this model
        collection_name = classDict['collection_name'] if 'collection_name' in classDict else classname.lower()
        _collection = mongo_client[DATABASE_NAME][collection_name]
        field_list = []
        for base in bases:
            # create the unique_together index
            if hasattr(base, 'unique_together'):
                idx = parseCompoundIndex(base.unique_together)
                _collection.create_index(idx, unique=True)
            if hasattr(base, 'compound_index'):
                idx = parseCompoundIndex(base.compound_index)
                _collection.create_index(idx)
            if hasattr(base, 'meta'):
                items = base.meta.fields.items()
                for name, field in items:
                    # single field index creation
                    indexField(_collection, name, field)
                # add the item to the list of fields to be stored in the meta
                # model
                field_list += items

        # clean the classDict by removing the fields from the desired
        # attributes i.e. the attributes we want to actively use on the model
        if 'unique_together' in classDict:
            idx = parseCompoundIndex(classDict['unique_together'])
            _collection.create_index(idx, unique=True)
        if 'compound_index' in classDict:
            idx = parseCompoundIndex(classDict['compound_index'])
            _collection.create_index(idx)
        for key, val in classDict.items():
            if issubclass(val.__class__, Field):
                field_list.append((key, val))
                indexField(_collection, key, val)
                del classDict[key]

        meta = Meta(field_list)

        # make the class
        new_class = type.__new__(cls, classname, bases, classDict)
        new_class.meta = meta

        # register the model in the ModelRegistry
        register(app_label, classname, new_class)

        return load(app_label, classname)


class Model(DatabaseInterface):

    __metaclass__ = ModelBaseMeta

    _id = Id()

    def __init__(self, *args, **kwargs):
        self._from_db = kwargs.get('_from_db', False)
        self._conditions = kwargs.get('_conditions')
        for fieldname, field in self.meta.fields.items():
            value = kwargs.get(fieldname, field.getDefault())
            setattr(self, fieldname, value)
            field.model = self
            field.name = fieldname
            field.value = value

    def __repr__(self):
        return u'<%s: %s>' % (self.__class__.__name__, self._id)

    def filterFields(self, field_type):
        """
        Filters the instances within _fields for the class type specified.
        """
        # get fieldnames
        fieldmap = self.meta.fieldmap
        if field_type in fieldmap:
            fieldnames = fieldmap[field_type]
            return [getattr(self, name) for name in fieldnames]
        return []

    def serialize(self, to_json=False):
        """
        For use in model serialization. It uses the dictionary returned from
        _fields property method (below).
        """
        data = {
            name: field.serialize(getattr(self, name), to_json=to_json)
            for name, field in self.meta.fields.items()
            if getattr(self, name) is not None
        }
        if to_json:
            return json.dumps(data)
        return data
