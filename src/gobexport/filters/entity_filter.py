class EntityFilter:
    """Baseclass for EntityFilters. """

    def filter(self, entity: dict):
        raise NotImplementedError()

    def reset(self):
        # Some filters need a reset after exporting a file
        pass
