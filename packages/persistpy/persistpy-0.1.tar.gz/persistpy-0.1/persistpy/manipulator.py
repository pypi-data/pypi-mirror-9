from pymongo.son_manipulator import SONManipulator as BaseSONManipulator
from bson.objectid import ObjectId
from bson.dbref import DBRef
from .model import BaseModel
import datetime
from jsonpickle.pickler import Pickler
from jsonpickle.unpickler import Unpickler
from jsonpickle.backend import JSONBackend
from jsonpickle import tags


class SONManipulator(BaseSONManipulator):
    def __init__(self, session):
        super(SONManipulator, self).__init__()
        self.session = session

    def transform_incoming(self, son, collection):
        for (key, value) in son.items():
            son[key] = self.transform_incoming_value(value, collection)
        return son

    def transform_incoming_value(self, value, collection):
        if isinstance(value, dict):
            return self.transform_incoming(value, collection)
        if isinstance(value, list):
            return [self.transform_incoming_value(v, collection) for v in value]
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            return datetime.datetime.combine(value, datetime.time(0, 0, 0))
        if isinstance(value, datetime.time):
            return datetime.datetime.combine(datetime.date(0, 0, 0), value)
        bson = getattr(value, '__bson__', None)
        if bson:
            return bson()
        return value

    def transform_outgoing(self, son, collection):
        for (key, value) in son.items():
            son[key] = self.transform_outgoing_value(value, collection)
        return son

    def transform_outgoing_value(self, value, collection):
        if isinstance(value, list):
            return [self.transform_outgoing_value(v, collection) for v in value]
        if isinstance(value, dict):
            value = self.transform_outgoing(value, collection)
            for t in tags.RESERVED:
                if t in value:
                    unpickler = Unpickler(backend=JSONBackend())
                    return unpickler.restore(value)
            return value
        if isinstance(value, DBRef):
            model = self.session.mapper.from_collection(value.collection, ensure=True)
            return model.lazy(value.id)
        return value


class BSONMethodMixin(object):
    def __bson__(self):
        pickler = Pickler(backend=JSONBackend())
        return pickler.flatten(self)