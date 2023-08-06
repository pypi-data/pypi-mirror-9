import types
from bson.objectid import ObjectId
from pymongo import ASCENDING, DESCENDING
from .utils import log_operation


def and_(*args):
    return {"$and": args}


def or_(*args):
    return {"$or": args}


class LazyModelList(object):
    def __init__(self, data, model, instanciator=None):
        self.data = data
        self.model = model
        self.cursor = 0
        if instanciator:
            self.instanciate = instanciator

    def __iter__(self):
        self.cursor = 0
        return self

    def next(self):
        self.cursor += 1
        if isinstance(self.data, types.GeneratorType):
            attrs = self.data.next()
        else:
            try:
                attrs = self.data[self.cursor - 1]
            except IndexError:
                raise StopIteration
        return self.instanciate(attrs)

    def instanciate(self, data):
        return self.model.from_data(data)

    def as_list(self):
        return list(self)

    def for_json(self):
        return self.as_list()


class Query(object):
    def __init__(self, collection):
        self.collection = collection
        self._fields = set()
        self._spec = {}
        self._sort = []
        self._skip = None
        self._limit = None
        self._cursor = None

    def select(self, *args):
        q = self.clone()
        q._fields.update(args)
        return q

    def filter(self, *args):
        q = self.clone()
        for f in args:
            q._spec.update(f)
        return q

    def filter_by(self, **kwargs):
        q = self.clone()
        if 'id' in kwargs:
            kwargs['_id'] = kwargs.pop('id')
        q._spec.update(kwargs)
        return q

    def sort(self, field, direction=None):
        q = self.clone()
        if field is None:
            q._sort = []
            return
        if direction is None:
            if isinstance(field, tuple):
                (field, direction) = field
            elif " " in field:
                (field, str_dir) = field.rsplit(" ", 1)
                direction = ASCENDING if str_dir.lower() == "asc" else DESCENDING
            else:
                direction = ASCENDING

        q._sort.append((field, direction))
        return q

    def skip(self, offset):
        return self.clone(_skip=offset)

    def limit(self, limit):
        return self.clone(_limit=limit)

    def clone(self, **overrides):
        attr_to_clone = ('_fields', '_spec', '_sort', '_skip', '_limit')
        data = {}
        for attr in attr_to_clone:
            v = getattr(self, attr)
            if isinstance(v, dict):
                data[attr] = dict(v)
            elif isinstance(v, list):
                data[attr] = list(v)
            else:
                data[attr] = v
        data.update(overrides)
        q = self.__class__(self.collection)
        q.__dict__.update(data)
        return q

    @property
    def cursor(self):
        if self._cursor is None:
            kwargs = dict()
            if self._fields:
                kwargs["fields"] = self._fields
            if self._sort:
                kwargs["sort"] = self._sort
            if self._skip:
                kwargs["skip"] = self._skip
            if self._limit:
                kwargs["limit"] = self._limit
            log_operation(self.collection.name, "find", dict(kwargs, spec=self._spec))
            # apply incoming son transformers because pymongo doesn't do it on queries
            spec = self.collection.database._fix_incoming(self._spec, self.collection)
            self._cursor = self.collection.find(spec, **kwargs)
        return self._cursor

    def fetch(self, id):
        if not isinstance(id, ObjectId):
            id = ObjectId(id)
        q = self.filter_by(_id=id)
        for o in q.cursor.limit(-1):
            return o
        return None

    def all(self):
        return list([o for o in self.cursor])

    def first(self):
        for o in self.cursor.limit(-1):
            return o
        return None

    def one(self):
        o = self.first()
        if o is None:
            raise Exception()
        return o

    def count(self):
        return self.cursor.count()

    def update(self, data):
        spec = self.collection.database._fix_incoming(self._spec, self.collection)
        return self.collection.update(spec, data, multi=True)

    def delete(self):
        spec = self.collection.database._fix_incoming(self._spec, self.collection)
        self.collection.remove(spec)

    def __iter__(self):
        return iter(self.cursor)

    def __len__(self):
        return self.count()

    def for_json(self):
        return self.all()

    def __repr__(self):
        return "Query(fields=%s, spec=%s, sort=%s, limit=%s, skip=%s)" %\
            (self._fields, self._spec, self._sort, self._limit, self._skip)


class ModelQuery(Query):
    lazy_model_list_class = LazyModelList

    def __init__(self, model):
        super(ModelQuery, self).__init__(model.__session__[model.__collectionname__])
        self.model = model

    def get(self, id):
        data = self.fetch(id)
        if data is not None:
            return self.model.from_data(data)

    def all(self, as_object=True):
        if as_object:
            return self.lazy_model_list_class(self.cursor, self.model)
        return self.cursor

    def first(self, as_object=True):
        for o in self.cursor.limit(-1):
            if as_object:
                return self.model.from_data(o)
            return o
        return None

    def clone(self, **overrides):
        attr_to_clone = ('_fields', '_spec', '_sort', '_skip', '_limit')
        data = {}
        for attr in attr_to_clone:
            v = getattr(self, attr)
            if isinstance(v, dict):
                data[attr] = dict(v)
            elif isinstance(v, list):
                data[attr] = list(v)
            else:
                data[attr] = v
        data.update(overrides)
        q = self.__class__(self.model)
        q.__dict__.update(data)
        return q

    def for_json(self):
        return self.all().for_json()