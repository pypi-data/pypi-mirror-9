
import sys
from sqlchemyforms.validators.is_in_db import IsInDBValidator
from sqlchemyforms.validators.is_in_set import IsInSetValidator
from sqlchemyforms.validators.simple import URLValidator
from sqlchemyforms.field import Field
from sqlchemyforms.table.column import Column
from plutonium.modules.tools import Storage

from structed_data_validator import StructedDataValidator

Feed = getattr(sys.modules['plutonium.models.feed'], 'Feed')
Output = getattr(sys.modules['plutonium.models.output'], 'Output')
Filter = getattr(sys.modules['plutonium.models.filter'], 'Filter')

# form_field_definitions needed for determine which field needed for the form, add validators, etc
Feed.form_field_definitions = [
    Field(Feed.id),
    Field(Feed.url, [URLValidator()]),
    Field(Feed.name),
    Field(Feed.enabled),
    Field(Feed.output, [IsInDBValidator(Output.id, [Output.name])]),
    Field(Feed.update_interval),
    Field(Feed.target_path_pattern),
    Field(Feed.filters, [IsInDBValidator(Filter.id, [Filter.name], multiple = True)]),
]

# table_definitions needed for filtering the data, and pre-rendering
Feed.table_definitions = Storage(
    columns = [
        Column(Feed.id),
        Column(Feed.enabled),
        Column(Feed.name),
        Column(Feed.update_interval),
        #Column(Feed.last_update),
        Column(Feed.output, fetcher = lambda v: v.name),
        Column(Feed.filters, fetcher = lambda v: len(v))
    ],
    sorting_defaults = Storage(
        key = Feed.id,
        dir = 'asc'
    ),
    row_per_page = 20
)

Output.form_field_definitions = [
    Field(Output.id),
    Field(Output.name),
    Field(Output.type, [IsInSetValidator(lambda: {val: val for val in Output.output_plugins.keys()})]),
    Field(Output.params, [StructedDataValidator(lambda: {name: Output.output_plugins[name].get_required_params_struct() for name in Output.output_plugins}, Output.type)]),
]

Output.table_definitions = Storage(
    columns = [
        Column(Output.id),
        Column(Output.name),
        Column(Output.type),
    ],
    sorting_defaults = Storage(
        key = Output.id,
        dir = 'asc'
    ),
    row_per_page = 20
)

Filter.form_field_definitions = [
    Field(Filter.id),
    Field(Filter.name),
    Field(Filter.pattern),
    Field(Filter.source_node),
    Field(Filter.type),
]

Filter.table_definitions = Storage(
    columns = [
        Column(Filter.id),
        Column(Filter.name),
        Column(Filter.pattern),
        Column(Filter.source_node),
        Column(Filter.type),
    ],
    sorting_defaults = Storage(
        key = Filter.id,
        dir = 'asc'
    ),
    row_per_page = 20
)