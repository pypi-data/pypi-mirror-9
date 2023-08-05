import datetime
import decimal
import weakref

from cubicweb import cwvreg

from cubes.wsme.types import Base, Any, JsonData, binary
from cubes.wsme.controller import WSCRUDController

import wsme.types


class WSMERegistry(wsme.types.Registry):
    """The wsme types registry.
    To be populated before type solving"""

    @staticmethod
    def get(vreg):
        instance = getattr(vreg, '_wsme_registry', None)
        if instance is None:
            vreg._wsme_registry = instance = WSMERegistry(vreg)
            Any.reginit(vreg)
            instance.register(JsonData)

        return instance

    def __init__(self, vreg):
        super(WSMERegistry, self).__init__()

        self.vreg = weakref.proxy(vreg)

        self.cwtypes = {
            'Boolean': bool,
            'Int': long,
            'BigInt': long,
            'Float': float,
            'Boolean': bool,
            'Decimal': decimal.Decimal,
            'Date': datetime.date,
            'Time': datetime.time,
            'Datetime': datetime.datetime,
            'TZDatetime': datetime.datetime,
            'String': wsme.types.text,
            'Password': wsme.types.text,
            'Bytes': binary
        }

    def finalize_init(self):
        for class_ in self.complex_types:
            if issubclass(class_, Base):
                class_.finalize_init()

    def guess_datatype(self, etype):
        return self.cwtypes.get(etype)

    def register(self, class_):
        class_ = super(WSMERegistry, self).register(class_)
        etype = getattr(class_, '__etype__', None)

        if etype is not None:
            self.cwtypes[etype] = class_

        return class_


class ControllerRegistry(cwvreg.CWRegistry):
    def initialization_completed(self):
        etypes = set()
        # make sure all etypes have a corresponding wstype
        for eschema in self.vreg.schema.entities():
            if not eschema.final:
                etypes.add(eschema.type)

            wstype = self.vreg.wsme_registry.guess_datatype(eschema.type)
            if wstype is None:
                new_class = type(eschema.type, (Base,), {
                    '__etype__': eschema.type,
                    '__autoattr__': True
                })
                new_class.reginit(self.vreg)

        self.vreg.wsme_registry.finalize_init()

        # make sure there is a wscontroller for each etype
        controllers = {
            ctrl.__cwetype__.__etype__: ctrl
            for ctrl in (
                self.vreg['controllers']['webservice']
                if 'webservice' in self.vreg['controllers']
                else ())
        }

        for etype in etypes.difference(controllers.keys()):
            wstype = self.vreg.wsme_registry.guess_datatype(etype)
            new_ctrl = type(etype + 'Controller', (WSCRUDController,), {
                '__cwetype__': wstype
            })
            self.vreg.register(new_ctrl)

        super(ControllerRegistry, self).initialization_completed()


cwvreg.CWRegistryStore.REGISTRY_FACTORY['controllers'] = ControllerRegistry
cwvreg.CWRegistryStore.wsme_registry = property(WSMERegistry.get)
