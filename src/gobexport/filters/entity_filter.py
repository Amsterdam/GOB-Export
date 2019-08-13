class EntityFilter:
    """Baseclass for EntityFilters. """

    def filter(self, entity: dict):
        raise NotImplementedError()
