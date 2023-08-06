import logging
from blinker import Namespace
import functools


logger = logging.getLogger("persistpy")
signal_namespace = Namespace()


def log_operation(coll, op, data=None, pk=None):
    logger.debug("collection=%s operation=%s data=%s _id=%s" % (coll, op, data, pk))


def create_change_tracking_type(name, wrapped_type, methods):
    def make_tracked_method(method_name):
        method = getattr(wrapped_type, method_name)
        def tracked_method(self, *args, **kwargs):
            rv = method(self, *args, **kwargs)
            self.callback(self, method_name)
            return rv
        return tracked_method

    attrs = dict((m, make_tracked_method(m)) for m in methods)
    def init(self, callback, *args, **kwargs):
        wrapped_type.__init__(self, *args, **kwargs)
        self.callback = callback
    attrs["__init__"] = init

    return type(name, (wrapped_type,), attrs)


# ChangeTrackingList = create_change_tracking_type("TrackingList", list, ("__delitem__",
#     "__delslice__", "__iadd__", "__imul__", "__setitem__", "__setslice__",
#     "append", "extend", "insert", "pop", "remove", "reverse", "sort"))

# ChangeTrackingDict = create_change_tracking_type("TrackingDict", dict, ("__delitem__",
#     "__setitem__", "clear", "pop", "popitem", "setdefault", "update"))


ChangeTrackingList = create_change_tracking_type("TrackingList", list, (
    "append", "extend", "insert", "pop", "remove", "reverse", "sort"))

ChangeTrackingDict = create_change_tracking_type("TrackingDict", dict, (
    "clear", "pop", "popitem", "setdefault", "update"))