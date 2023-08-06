
from sqlchemyforms.widget import Widget

class StructWidget(Widget):
    html_type = 'struct'

    def __init__(self, *args, **kwargs):
        super(StructWidget, self).__init__(*args, **kwargs)
        self.depends_on = None
        self.struct = {}
        self.value_type = 'object'
        self.iterable.extend(['struct', 'depends_on'])

    def __repr__(self):
        return "<StructWidget(name=%(name)s, type=%(type)s, value=%(value)s, struct=%(struct)s, depends_on=%(depends_on)r)>" % self
