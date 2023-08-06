from copy import copy

from sqlchemyforms.validators.simple import SimpleValidator
from sqlchemyforms.tools import Storage
from widgets import StructWidget

class StructedDataValidator(SimpleValidator):

    widget_type = StructWidget

    struct_types = {
        int: ('integer', 'number'),
        str: ('text', 'string'),
        bool: ('checkbox', 'boolean')
    }

    def __init__(self, struct, depends_on = None):
        """
            depends_on: an other sqlalchemy field. if it is not none the struct must be a dict, values keyed by possible values of depends_on field
        """
        self.struct = struct
        self.depends_on = depends_on

    def format_struct_desc(self, struct):
        for field in struct:
            if field.nodes:
                self.format_struct_desc(field.nodes)
            else:
                field.value_type =  self.struct_types[field.type][1]
                field.type =  self.struct_types[field.type][0]

    def check(self, value):
        return ''

    def process_widget(self, widget, db):

        struct = copy(self.struct() if hasattr(self.struct, '__call__') else self.struct)

        if self.depends_on is None:
            self.format_struct_desc(struct)
        else:
            widget.depends_on = self.depends_on.key
            for name in struct:
                self.format_struct_desc(struct[name])

        widget.struct = struct

    def format_value(self, value, field_type):
        # reverse of format_struct_desc
        return value