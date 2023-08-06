from pymongo import MongoClient
from pymongo.collection import Collection as BaseCollection
from .model import make_bound_model, BaseModel
from .utils import logger, signal_namespace, log_operation
from .manipulator import SONManipulator
from .query import Query
import inspect


class MapperException(Exception):
    pass


class Mapper(object):
    def __init__(self, session=None, dynamic_model_creation=True):
        self._session = session
        self.dynamic_model_creation = dynamic_model_creation
        self.models = {}
        self.id_maps = {}

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session):
        self._session = session
        for model in self.models:
            model.__session__ = session

    def register(self, model):
        self.models[model.__name__] = model

    def create_model(self, name):
        return make_bound_model(name, session=self._session, mapper=self)

    def create_model_base(self, name="Model"):
        base = make_bound_model(name, session=self._session, mapper=self)
        base.__collectionname__ = None
        return base

    def ensure_model(self, name):
        name = str(name)
        if name in self.models:
            return self.models[name]
        if not self.dynamic_model_creation:
            raise Exception("Model '%s' does not exist" % name)
        model = self.create_model(name)
        self.register(model)
        return model

    def id_map(self, name):
        if inspect.isclass(name):
            name = name.__name__
        if name not in self.id_maps:
            self.id_maps[name] = {}
        return self.id_maps[name]

    def from_collection(self, name, ensure=False, raise_exc=True):
        for model in self.models.itervalues():
            if model.__collectionname__ == name:
                return model
        if ensure:
            return self.ensure_model(name)
        if raise_exc:
            raise MapperException("Collection '%s' is not mapped to any class" % name)

    def __getitem__(self, name):
        return self.ensure_model(name)

    def __contains__(self, name):
        return name in self.models


class Collection(BaseCollection):
    @property
    def query(self):
        return Query(self)


class Session(object):
    mapper_class = Mapper

    before_model_saved_signal = signal_namespace.signal("before_model_saved")
    model_saved_signal = signal_namespace.signal("model_saved")
    before_model_inserted_signal = signal_namespace.signal("before_model_inserted")
    model_inserted_signal = signal_namespace.signal("model_inserted")
    before_model_updated_signal = signal_namespace.signal("before_model_updated")
    model_updated_signal = signal_namespace.signal("model_updated")
    model_deleted_signal = signal_namespace.signal("model_deleted")

    def __init__(self, db, **kwargs):
        self.db = db
        self.db.add_son_manipulator(SONManipulator(self))
        self.mapper = self.mapper_class(self)

    def create_model_base(self, *args, **kwargs):
        return self.mapper.create_model_base(*args, **kwargs)

    def get(self, name):
        return Collection(self.db, name)

    def __getattr__(self, name):
        return self.get(name)

    def __getitem__(self, name):
        return self.get(name)

    def save(self, obj):
        for obj in self.flatten_modified_objects(obj):
            self.before_model_saved_signal.send(self, obj=obj)
            if obj.is_new():
                self.insert(obj)
            else:
                self.update(obj)
            self.model_saved_signal.send(self, obj=obj)

    def insert(self, obj):
        self.before_model_inserted_signal.send(self, obj=obj)
        _id = self._insert(obj)
        if _id is not None:
            object.__setattr__(obj, "_id", _id)
        obj.__modified__.clear()
        self.model_inserted_signal.send(self, obj=obj)

    def _insert(self, obj):
        data = dict(obj.__data__)
        coll = self[obj.__collectionname__]
        log_operation(coll.name, "insert", data)
        return coll.insert(data)

    def update(self, obj):
        self.before_model_updated_signal.send(self, obj=obj)
        self._update(obj)
        obj.__modified__.clear()
        self._clear_id_map(obj)
        self.model_updated_signal.send(self, obj=obj)

    def _update(self, obj):
        data = dict((c, obj.__data__[c]) for c in obj.__modified__)
        if not data:
            return
        coll = self[obj.__collectionname__]
        log_operation(coll.name, "update", data, obj._id)
        coll.update({"_id": obj._id}, {"$set": data}, manipulate=True)

    def delete(self, obj):
        self._delete(obj)
        self._clear_id_map(obj)
        self.model_deleted_signal.send(self, obj=obj)

    def _delete(self, obj):
        coll = self[obj.__collectionname__]
        log_operation(coll.name, "remove", None, obj._id)
        coll.remove({"_id": obj._id})

    def _clear_id_map(self, obj):
        self.mapper.id_map(obj.__class__.__name__).pop(obj._id, None)

    def flatten_modified_objects(self, obj):
        def flatten(it):
            for v in it:
                if isinstance(v, list):
                    for i in flatten(v):
                        yield i
                elif isinstance(v, dict):
                    for i in flatten(v.itervalues()):
                        yield i
                elif isinstance(v, BaseModel) and (v.is_new() or v.is_modified()):
                    yield v
        for i in flatten(obj.__data__.itervalues()):
            yield i
        yield obj