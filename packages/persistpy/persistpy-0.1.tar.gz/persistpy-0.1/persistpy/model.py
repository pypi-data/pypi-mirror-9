import inflection
import inspect
from .query import ModelQuery
from .utils import ChangeTrackingList, ChangeTrackingDict
from bson.dbref import DBRef
from bson.objectid import ObjectId


class SchemaError(Exception):
    pass


class SchemaCoherenceError(SchemaError):
    pass


class ModelAttribute(object):
    def bind(self, model, name):
        self.model = model
        self.name = name
        return self


class ModelChangeTrackingList(ChangeTrackingList):
    def __init__(self, obj, attrname, *args, **kwargs):
        callback = lambda s, m: obj.__modified__.add(attrname)
        super(ModelChangeTrackingList, self).__init__(callback, *args, **kwargs)


class ModelChangeTrackingDict(ChangeTrackingDict):
    def __init__(self, obj, attrname, *args, **kwargs):
        callback = lambda s, m: obj.__modified__.add(attrname)
        super(ModelChangeTrackingDict, self).__init__(callback, *args, **kwargs)


def apply_change_tracking(data, obj, name=None):
    for k, v in data.iteritems():
        if isinstance(v, dict) and not isinstance(v, ChangeTrackingDict):
            data[k] = ModelChangeTrackingDict(obj, name or k, apply_change_tracking(v, obj, name or k))
        elif isinstance(v, list) and not isinstance(v, ChangeTrackingList):
            data[k] = ModelChangeTrackingList(obj, name or k, apply_change_tracking_list(v, obj, name or k))
    return data


def apply_change_tracking_list(lst, obj, name):
    for i in lst:
        if isinstance(i, list) and not isinstance(i, ChangeTrackingList):
            yield ModelChangeTrackingList(obj, name, apply_change_tracking_list(i, obj, name))
        elif isinstance(i, dict) and not isinstance(i, ChangeTrackingDict):
            yield ModelChangeTrackingDict(obj, name, apply_change_tracking(i, obj, name))
        else:
            yield i


class Field(ModelAttribute):
    def __init__(self, default=None, index=False, unique=False):
        self.default = default
        self.index = index
        self.unique = unique

    def make_default(self, obj):
        d = self.default
        if d == list:
            return ModelChangeTrackingList(obj, self.name)
        elif d == dict:
            return ModelChangeTrackingDict(obj, self.name)
        elif inspect.isfunction(d):
            return d(self)
        elif inspect.isclass(d):
            return d()
        return d

    def __eq__(self, other):
        return dict([(self.name, other)])

    def __ne__(self, other):
        return dict([(self.name, {"$ne": other})])

    def __gt__(self, other):
        return dict([(self.name, {"$gt": other})])

    def __ge__(self, other):
        return dict([(self.name, {"$gte": other})])

    def __lt__(self, other):
        return dict([(self.name, {"$lt": other})])

    def __le__(self, other):
        return dict([(self.name, {"$lte": other})])

    def contains(self, other):
        if isinstance(other, (str, int, bool, float)):
            return dict([(self.name, other)])
        return dict([(self.name, {"$elemMatch": other})])

    def match_any(self, *others):
        return dict([(self.name, {"$in": others})])

    def not_match_any(self, *others):
        return dict([(self.name, {"$nin": others})])

    def __str__(self):
        return self.name

    def __get__(self, obj, cls):
        if self.name not in obj.__data__:
            d = self.make_default(obj)
            if d is not None:
                obj.__data__[self.name] = d
        return obj.__getattr__(self.name)

    def __set__(self, obj, cls, value):
        obj.__setattr__(self.name, value)


class Alias(Field):
    def __init__(self, alias_of):
        self.name = alias_of

    def bind(self, model, name):
        self.model = model
        self.alias = name
        return self


class HasMany(ModelAttribute):
    def __init__(self, target, target_field=None, filters=None, sort=None, limit=None, skip=None):
        self._target = target
        self.target_field = target_field
        self.filters = filters
        self.sort = sort
        self.limit = limit
        self.skip = skip

    @property
    def target(self):
        if isinstance(self._target, str):
            self._target = self.model.__mapper__[self._target]
            if not self._target:
                raise SchemaError("A relationship of '%s' points to an unknown model '%s'" % (self.model.__name__, self._target))
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    def load(self, obj):
        q = self.target.query
        target_field = self.target_field or self.model.__name__.lower()
        field = getattr(self.target, target_field)
        if isinstance(field, Field) and field.default == list:
            q = q.filter(field.contains(obj))
        else:
            q = q.filter(field == obj)
        if self.filters:
            q = q.filter(*self.filters)
        if self.sort:
            q = q.sort(self.sort)
        if self.limit:
            q = q.limit(self.limit)
        if self.skip:
            q = q.skip(self.skip)
        return q

    def __get__(self, obj, cls):
        if obj.is_new():
            return []
        if self.name not in obj.__rels__:
            obj.__rels__[self.name] = self.load(obj)
        return obj.__rels__[self.name]

    def __set__(self, obj, cls, value):
        raise Exception("A relationship cannot be modified")


class ModelMeta(type):
    def __init__(cls, name, bases, attrs):
        dct = {}
        schema = {}
        for attr, value in attrs.iteritems():
            if isinstance(value, ModelAttribute):
                schema[attr] = value
            else:
                dct[attr] = value

        type.__init__(cls, name, bases, dct)
        if not hasattr(cls, "__schema__") or not cls.__schema__:
            type.__setattr__(cls, "__schema__", {})
        elif hasattr(cls, "__schema__"):
            cls.__schema__ = dict(cls.__schema__)

        if not cls.__collectionname__:
            cls.__collectionname__ = inflection.pluralize(inflection.underscore(name))

        if not isinstance(cls.__mapper__, UnboundedMapperProperty):
            # auto register the model on the mapper when the property is bound
            cls.__mapper__.register(cls)

        for k, v in schema.iteritems():
            setattr(cls, k, v)

    def __setattr__(cls, name, value):
        if isinstance(value, ModelAttribute):
            cls.__schema__[name] = value.bind(cls, name)
        elif name in cls.__schema__:
            del cls.__schema__[name]
        type.__setattr__(cls, name, value)

    def __getattr__(cls, name):
        if name not in cls.__schema__:
            return Field().bind(cls, name)
        return cls.__schema__[name]

    @property
    def collection(cls):
        return cls.__session__[cls.__collectionname__]

    def ensure(cls, **attrs):
        for name, value in attrs.iteritems():
            if not isinstance(value, ModelAttribute):
                raise Exception("Mapped attributes must be of type ModelAttribute")
            if name in cls.__schema__ and not isinstance(cls.__schema__[name], type(value)):
                raise SchemaCoherenceError("Attribute '%s' is expected to be of type '%s' but is '%s'" % \
                    (name, type(value).__name__, type(cls.__schema__[name]).__name__))
            elif name not in cls.__schema__:
                setattr(cls, name, value)
        return cls

    def lazy(cls, _id):
        obj = cls.__new__(cls)
        object.__setattr__(obj, '_id', _id)
        object.__setattr__(obj, "__lazy__", True)
        return obj

    def from_data(cls, data):
        obj = cls.__new__(cls)
        object.__setattr__(obj, '_id', data.pop('_id', None))
        object.__setattr__(obj, "___data___", apply_change_tracking(data, obj))
        return obj

    @property
    def id(self):
        return Alias('_id')
        

class UnboundedMapperProperty(object):
    def __get__(self, obj, cls):
        raise Exception("Model '%s' is not bound to any mapper" % cls.__name__)
        

class UnboundedSessionProperty(object):
    def __get__(self, obj, cls):
        raise Exception("Model '%s' is not bound to any session" % cls.__name__)


class QueryProperty(object):
    def __get__(self, obj, cls):
        return cls.query_class(cls)


class RelProperty(object):
    def __get__(self, obj, cls):
        self.obj = obj
        self.cls = cls
        return self

    def __getattr__(self, name):
        model_name = inflection.camelize(inflection.singularize(name))
        return HasMany(model_name).bind(self.cls, name).load(self.obj)


class BaseModel(object):
    __session__ = UnboundedSessionProperty()
    __mapper__ = UnboundedMapperProperty()
    __schema__ = None
    __collectionname__ = None
    query = QueryProperty()
    query_class = ModelQuery
    rel = RelProperty()

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls, *args, **kwargs)
        object.__setattr__(obj, "_id", None)
        object.__setattr__(obj, "___data___", {})
        object.__setattr__(obj, "__rels__", {})
        object.__setattr__(obj, "__modified__", set())
        object.__setattr__(obj, "__lazy__", False)
        for attr in cls.__schema__:
            if isinstance(attr, Field):
                d = attr.make_default(obj)
                if d is not None:
                    obj.___data___[attr.name] = d
        return obj

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    @property
    def id(self):
        return str(self._id)

    @id.setter
    def id(self, value):
        if not isinstance(value, ObjectId):
            value = ObjectId(value)
        object.__setattr__(self, "_id", value)

    @property
    def __data__(self):
        if self.__lazy__:
            self.refresh()
            object.__setattr__(self, "__lazy__", False)
        return self.___data___

    @__data__.setter
    def __data__(self, data):
        object.__setattr__(obj, "___data___", data)

    def __getattr__(self, name):
        return self.__data__.get(name)

    def __setattr__(self, name, value):
        self.__data__[name] = value
        self.__modified__.add(name)

    def __contains__(self, name):
        return name in self.__data__

    def __delattr__(self, name):
        del self.__data__[name]
        self.__modified__.add(name)

    def is_new(self):
        return not self._id

    def is_modified(self):
        return len(self.__modified__) > 0

    def refresh(self):
        if self._id:
            data = self.query.fetch(self._id)
            if data is None:
                raise Exception("Cannot refresh model: _id does not match any document")
            data.pop('_id', None)
            self.___data___.update(apply_change_tracking(data, self))
            object.__setattr__(self, "__modified__", set())

    def save(self):
        self.__session__.save(self)

    def delete(self):
        self.__session__.delete(self)

    def clone(self):
        obj = self.__class__()
        object.__setattr__(obj, "___data___", dict(self.___data___))
        return obj

    def for_json(self):
        dct = {'_id': str(self._id)}
        for k, v in self.__data__.iteritems():
            if isinstance(v, BaseModel):
                dct[k] = v.for_json()
            else:
                dct[k] = v
        return dct

    def __bson__(self):
        return DBRef(self.__collectionname__, self._id)

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self._id)


def make_bound_model(name, session=None, mapper=None, model_class=BaseModel, metaclass=ModelMeta):
    return metaclass(name, (model_class,), {
        "__session__": session or UnboundedSessionProperty(),
        "__mapper__": mapper or UnboundedMapperProperty()})