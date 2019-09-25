from gobexport.filters.entity_filter import EntityFilter
from gobexport.exporter.utils import get_entity_value


class NotEmptyFilter(EntityFilter):
    """NotEmptyFilter

    EntityFilter that checks if not all supplied fields are empty. At least one of the input fields should have a value
    defined.
    """

    def __init__(self, *fields):
        self.fields = fields

    def filter(self, entity: dict):
        return all([get_entity_value(entity, field) for field in self.fields])
