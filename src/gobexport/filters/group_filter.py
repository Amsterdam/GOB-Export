from typing import List
from gobexport.filters.entity_filter import EntityFilter


class GroupFilter(EntityFilter):
    """GroupFilter is an EntityFilter that takes a list of EntityFilters. An entity only passes the GroupFilter when it
    passes all EntityFilters passed in the constructor.

    """

    def __init__(self, filters: List[EntityFilter]):
        self.filters = filters

    def filter(self, entity: dict):
        """Filters entity through all filters. Returns True if entity passes, False otherwise.

        :param entity:
        :return:
        """
        return all([f.filter(entity) for f in self.filters])

    def reset(self):
        for f in self.filters:
            f.reset()
