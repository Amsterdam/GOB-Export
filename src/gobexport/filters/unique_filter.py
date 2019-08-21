from gobexport.filters.entity_filter import EntityFilter
from gobexport.exporter.utils import get_entity_value


class UniqueFilter(EntityFilter):
    """UniqueFilter

    EntityFilter that checks is the value of the specified value is unique. Duplicates will be filtered out.
    """

    def __init__(self, field: str):
        self.values = set()
        self.field = field

    def filter(self, entity: dict):
        value = get_entity_value(entity, self.field)
        if value in self.values:
            return False
        else:
            self.values.add(value)
            return True
