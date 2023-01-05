"""Shared BRK Format classes."""


class SharedKadastraleobjectenCsvFormat:
    """CSV format class for BRK Kadastraleobjecten exports."""

    def if_vve(self, trueval, falseval):
        return {
            "condition": "isempty",
            "reference": "betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie",
            "negate": True,
            "trueval": trueval,
            "falseval": falseval,
        }

    def if_sjt(self, trueval, falseval=None):
        val = {
            "condition": "isempty",
            "reference": "vanKadastraalsubject.[0].identificatie",
            "negate": True,
            "trueval": trueval,
        }

        if falseval:
            val["falseval"] = falseval

        return val

    def if_empty_geen_waarde(self, reference):
        return {
            "condition": "isempty",
            "reference": reference,
            "negate": True,
            "trueval": reference,
            "falseval": {"action": "literal", "value": "geenWaarde"},
        }

    def comma_concatter(self, value):
        return value.replace("|", ", ")

    def concat_with_comma(self, reference):
        """Replace occurrences of '|' in `reference` with commas."""
        return {
            "action": "format",
            "value": reference,
            "formatter": self.comma_concatter,
        }

    def format_kadgrootte(self, value):
        floatval = float(value)

        if floatval < 1:
            return str(floatval)
        return str(int(floatval))

    def vve_or_subj(self, attribute):
        return self.if_vve(
            trueval=f"betrokkenBijAppartementsrechtsplitsingVve.[0].{attribute}",
            falseval=f"vanKadastraalsubject.[0].{attribute}",
        )

    def row_formatter(self, row):
        """Merges all 'isOntstaanUitGPerceel' relations into one object.

        With identificatie column concatenated into one, separated by comma's.

        (Very) simplified example:
        in     = { isOntstaanUitGPerceel: [{identificatie: 'A'}, {identificatie: 'B'}, {identificatie: 'C'}]}
        result = { isOntstaanUitGPerceel: [{identificatie: 'A,B,C'}]}

        :param row:
        :return:
        """
        identificatie = ",".join(
            [
                edge["node"]["identificatie"]
                for edge in row["node"]["isOntstaanUitGPerceel"].get("edges")
            ]
        )

        row["node"]["isOntstaanUitGPerceel"] = {
            "edges": [{"node": {"identificatie": identificatie}}]
        }

        return row
