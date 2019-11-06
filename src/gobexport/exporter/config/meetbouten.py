from shapely.geometry import shape, mapping

from gobexport.exporter.dat import dat_exporter


class MeetboutExportConfig:
    """Meetbouten config

    Example:
        meetboutid: 22081299:
        http://localhost:5000/meetbouten/meetbouten/?id=22081299
        =>
        $$22081299$$|$$$$|120951|491840|-1,9926||$$20010920$$|||$$$$|$$N$$|$$Orionplantsoen 7$$|$$$$||$$A$$
        |$$PB15 $$|1|POINT (120951.0 491840.0)

    """
    products = {
        'dat': {
            'exporter': dat_exporter,
            'endpoint': '/gob/meetbouten/meetbouten/?view=enhanced&ndjson=true',
            'filename': 'DAT/MBT_MEETBOUT.dat',
            'mime_type': 'plain/text',
            'format': 'identificatie:str|ligtInBuurt.code:str|geometrie:coo:x|geometrie:coo:y|hoogteTovNap:num:4|'
                      'zakkingCumulatief:num:1|datum:dat|bouwblokzijde:num|eigenaar:num|indicatieBeveiligd:str|'
                      'ligtInStadsdeel.code:str|nabijNummeraanduiding.bronwaarde:str|locatie:str|'
                      'zakkingssnelheid:num:1|status.code:str:{1: "A", 2:"A", 3:"V"}|ligtInBouwblok.code:str|'
                      'blokeenheid:num|geometrie:geo'
        }
    }


class MetingenExportConfig:
    """
    Metingen config

    Example:
        metingid: 621:
        http://localhost:5000/gob/meetbouten/metingen/621/
        =>
        621|$$19561003$$|$$N$$|,9169|1|$$14481027$$|$$13688000$$|$$$$|$$$$|1,00901442307691|2,29999999999997
        |$$Fugro$$|3|274||$$K$$|$$W$$

    """
    products = {
        'dat': {
            'exporter': dat_exporter,
            'endpoint': '/gob/meetbouten/metingen/?view=enhanced&ndjson=true',
            'filename': 'DAT/MBT_METING.dat',
            'mime_type': 'plain/text',
            'format': 'identificatie:num|datum:dat|typeMeting:str|hoogteTovNap:num:4|zakking:num:1|'
                      'hoortBijMeetbout.bronwaarde:str|refereertAanReferentiepunten.[0].bronwaarde:str|'
                      'refereertAanReferentiepunten.[1].bronwaarde:str|'
                      'refereertAanReferentiepunten.[2].bronwaarde:str|zakkingssnelheid:num:1|'
                      'zakkingCumulatief:num:1|isGemetenDoor:str|hoeveelsteMeting:num|aantalDagen:num|'
                      'pandmsl:str|ligtInStadsdeel.code:str|wijzeVanInwinnen.code:str:{1:"W",2:"T",3:"G"}'
        }
    }


class ReferentiepuntenExportConfig:
    """
    Example:
        referentiepuntid: 25280009:
        http://localhost:5000/gob/meetbouten/referentiepunten/25280009/
        =>
        $$25280009$$|121155|489090|2,2005|$$19790101$$|$$Zoutkeetsgracht 2 hoek Bokkinghangen$$
        |POINT (121155.0 489090.0)

    """
    products = {
        'dat': {
            'exporter': dat_exporter,
            'endpoint': '/gob/meetbouten/referentiepunten/?view=enhanced&ndjson=true',
            'filename': 'DAT/MBT_REFERENTIEPUNT.dat',
            'mime_type': 'plain/text',
            'format': 'identificatie:str|geometrie:coo:x|geometrie:coo:y|'
                      'hoogteTovNap:num:4|datum:dat|locatie:str|geometrie:geo'
        }
    }


class RollagenExportConfig:
    """
    Example:
        rollaagid: AK25:
        http://localhost:5000/gob/meetbouten/rollagen/AK25/
        =>
        $$AK25$$|1|121287|485235|POINT (121287.0 485245.0)

    """
    row_count = 0

    def row_formatter_rollagen(row):
        node = row['node']

        # Convert the bouwblok geometry to a centroid
        geom = shape(node['isGemetenVanBouwblok']['edges'][0]['node']['geometrie'])
        node['geometrie'] = mapping(geom.centroid)

        # Round the coordinates to three decimal places
        rounded_coordinates = []
        for coordinate in node['geometrie']['coordinates']:
            rounded_coordinates.append(str(round(coordinate, 3)))
        node['geometrie']['coordinates'] = rounded_coordinates
        return row

    query = """
{
  meetboutenRollagen(sort:identificatie_asc) {
    edges {
      node {
        identificatie
        isGemetenVanBouwblok {
          edges {
            node {
              code
              geometrie
            }
          }
        }
      }
    }
  }
}
"""

    products = {
        'dat': {
            'api_type': 'graphql',
            'exporter': dat_exporter,
            'row_formatter': row_formatter_rollagen,
            'filename': 'DAT/MBT_ROLLAAG.dat',
            'mime_type': 'plain/text',
            'format': 'identificatie:str|row_count:num|geometrie:coo:x|geometrie:coo:y|geometrie:geo',
            'query': query
        }
    }


configs = [
    MeetboutExportConfig,
    MetingenExportConfig,
    ReferentiepuntenExportConfig,
    RollagenExportConfig
]
