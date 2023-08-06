from ..core.pycompat import OrderedDict
import copy

from .common import AbstractWritableDataStore


class InMemoryDataStore(AbstractWritableDataStore):
    """
    Stores dimensions, variables and attributes
    in ordered dictionaries, making this store
    fast compared to stores which save to disk.
    """
    def __init__(self, variables=None, attributes=None):
        self._variables = OrderedDict() if variables is None else variables
        self._attributes = OrderedDict() if attributes is None else attributes

    def get_attrs(self):
        return self._attributes

    def get_variables(self):
        return self._variables

    def set_variable(self, k, v):
        new_var = copy.deepcopy(v)
        # we copy the variable and stuff all encodings in the
        # attributes to imitate what happens when writing to disk.
        new_var.attrs.update(new_var.encoding)
        new_var.encoding.clear()
        self._variables[k] = new_var

    def set_attribute(self, k, v):
        # copy to imitate writing to disk.
        self._attributes[k] = copy.deepcopy(v)

    def set_dimension(self, d, l):
        # in this model, dimensions are accounted for in the variables
        pass
