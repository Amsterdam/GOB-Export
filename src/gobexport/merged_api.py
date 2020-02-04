from itertools import zip_longest

from gobcore.exceptions import GOBException


class MergedApi:
    """MergedAPI combines the result of two API objects into one.

    The :merge_attributes: attributes from the result from :secondary_api: are merge into the results from
    :primary_api: . The :match_attributes: list contains the attributes that together uniquely identify the results in
    both API's.

    This class expects the same number of rows from both API's, with the same ordering, so that rows with matching
    positions are the rows with matching keys. If the keys at a certain position don't match an exception is raised.
    """

    def __init__(self, primary_api, secondary_api, match_attributes, merge_attributes):
        self.base_api = primary_api
        self.merged_api = secondary_api
        self.match_attributes = match_attributes
        self.attributes = merge_attributes

    def _item_key(self, item: dict):
        return tuple([item.get(column) for column in self.match_attributes])

    def __iter__(self):

        for left, right in zip_longest(self.base_api, self.merged_api):
            if left is None or right is None:
                raise GOBException("Length of results from API's don't match.")

            if self._item_key(left) != self._item_key(right):
                raise GOBException("Rows in API results don't match.")

            left.update({col: right.get(col) for col in self.attributes})
            yield left
