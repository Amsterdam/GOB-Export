from gobexport.filters.entity_filter import EntityFilter
from gobexport.exporter.utils import get_entity_value


class NotEmptyFilter(EntityFilter):
    """NotEmptyFilter

    EntityFilter that check if the value of the specified field is not empty
    """

    def __init__(self, field: str):
        self.field = field

    def filter(self, entity: dict):
        return not not get_entity_value(entity, self.field)
