from __future__ import absolute_import
from ..scan import Dispatcher
from ..errs import SchemaError
from ..spec.v2_0.objects import Operation
from ..utils import scope_compose

class TypeReduce(object):
    """ Type Reducer, collect Operation & Model
    spreaded in Resources put in a global accessible place.
    """
    class Disp(Dispatcher): pass

    def __init__(self):
        self.op = {}

    @Disp.register([Operation])
    def _op(self, path, obj, _):
        scope = obj.tags[0] if obj.tags and len(obj.tags) > 0 else None
        name = obj.operationId if obj.operationId else None

        new_scope = scope_compose(scope, name)
        if new_scope:
            if new_scope in self.op.keys():
                raise SchemaError('duplicated key found: ' + new_scope)

            self.op[new_scope] = obj

