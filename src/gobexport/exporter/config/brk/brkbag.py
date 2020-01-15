from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.utils import get_entity_value
from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.filters.entity_filter import EntityFilter
from gobexport.exporter.config.brk.utils import brk_filename


class BrkBagCsvFormat:

    def if_vot_relation(self, trueval: str, falseval: str):
        return {
            'condition': 'isempty',
            'reference': 'heeftEenRelatieMetVerblijfsobject.[0].identificatie',
            'negate': True,
            'trueval': trueval,
            'falseval': falseval,
        }

    def get_format(self):
        return {
            'BRK_KOT_ID': 'identificatie',
            'KOT_AKRKADGEMEENTECODE_CODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.code',
            'KOT_AKRKADGEMEENTECODE_OMS': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
            'KOT_SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
            'KOT_PERCEELNUMMER': 'perceelnummer',
            'KOT_INDEX_LETTER': 'indexletter',
            'KOT_INDEX_NUMMER': 'indexnummer',
            'KOT_STATUS_CODE': 'status',
            'KOT_MODIFICATION': '',
            'BAG_VOT_ID': 'heeftEenRelatieMetVerblijfsobject.[0].bronwaarde',
            'DIVA_VOT_ID': '',
            'AOT_OPENBARERUIMTENAAM': self.if_vot_relation(
                trueval='ligtAanOpenbareruimte.naam',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.openbareruimtenaam'
            ),
            'AOT_HUISNUMMER': self.if_vot_relation(
                trueval='heeftHoofdadres.huisnummer',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisnummer'
            ),
            'AOT_HUISLETTER': self.if_vot_relation(
                trueval='heeftHoofdadres.huisletter',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisletter'
            ),
            'AOT_HUISNUMMERTOEVOEGING': self.if_vot_relation(
                trueval='heeftHoofdadres.huisnummertoevoeging',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisnummertoevoeging'
            ),
            'AOT_POSTCODE': self.if_vot_relation(
                trueval='heeftHoofdadres.postcode',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.postcode'
            ),
            'AOT_WOONPLAATSNAAM': self.if_vot_relation(
                trueval='ligtInWoonplaats.naam',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam'
            ),
            'BRON_RELATIE': {
                'action': 'literal',
                'value': 'BRK'
            }
        }


class BrkBagExportConfig:
    format = BrkBagCsvFormat()

    query = '''
{
  brkKadastraleobjecten {
    edges {
      node {
        identificatie
        aangeduidDoorKadastralegemeente {
          edges {
            node {
              broninfo
            }
          }
        }
        aangeduidDoorKadastralegemeentecode {
          edges {
            node {
              broninfo
            }
          }
        }
        aangeduidDoorKadastralesectie {
          edges {
            node {
              code
            }
          }
        }
        perceelnummer
        indexletter
        indexnummer
        status
        heeftEenRelatieMetVerblijfsobject {
          edges {
            node {
              identificatie
              bronwaarde
              status
              broninfo
                heeftHoofdadres {
                edges {
                  node {
                    identificatie
                    ligtAanOpenbareruimte {
                      edges {
                        node {
                          naam
                        }
                      }
                    }
                    huisnummer
                    huisletter
                    huisnummertoevoeging
                    postcode
                    ligtInWoonplaats {
                      edges {
                        node {
                          naam
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
'''

    class VotFilter(EntityFilter):
        """Only include rows with VOT statuses, for VOT's where status is defined:
        2   Niet gerealiseerd verblijfsobject
        3   Verblijfsobject in gebruik (niet ingemeten)
        4   Verblijfsobject in gebruik
        6   Verblijfsobject buiten gebruik

        """
        valid_status_codes = [2, 3, 4, 6]
        vot_identificatie = 'heeftEenRelatieMetVerblijfsobject.[0].identificatie'
        status_code = 'heeftEenRelatieMetVerblijfsobject.[0].status.code'
        city = 'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam'

        def filter(self, entity: dict):
            if get_entity_value(entity, self.vot_identificatie):
                status_code = get_entity_value(entity, self.status_code)
                return status_code and int(status_code) in self.valid_status_codes
            elif get_entity_value(entity, self.city):
                return not get_entity_value(entity, self.city).lower().startswith('amsterdam')

            return True

    products = {
        'csv': {
            'exporter': csv_exporter,
            'entity_filters': [
                NotEmptyFilter('heeftEenRelatieMetVerblijfsobject.[0].bronwaarde'),
                VotFilter(),
            ],
            'api_type': 'graphql_streaming',
            'secure': True,
            'unfold': True,
            'query': query,
            'filename': lambda: brk_filename("BRK_BAG"),
            'mime_type': 'plain/text',
            'format': format.get_format(),
        }
    }
