"""Export meetbouten

Export meetbouten data in a file

The export file specifications can be found in:
    https://www.amsterdam.nl/stelselpedia/meetbouten-index/producten/prodspecs-mebo/

Headers:       None
Separator:     |
String marker: $$

Example:
    meetboutid: 22081299:
    http://localhost:5000/meetbouten/meetbouten/?id=22081299
    =>
    $$22081299$$|$$$$|120951|491840|-1,9926||$$20010920$$|1||$$$$|$$N$$|$$Orionplantsoen 7$$|$$$$||$$A$$
    |$$PB15 $$|1|POINT (120951.0 491840.0)

"""
import re

from export.api import API
from export.meetbouten.types import type_convert


def _export_meetbout(meetbout):
    """Exports a single meetbout

    The export format is a string containing the attributes and types to be converted.
    A declarative way of describing exports is used:
    The epxort format is used both to read the attributes and types and to write the correct output format

    :param meetbout:
    :return:
    """
    format = 'meetboutid:str|buurt:str|xcoordinaat:num|ycoordinaat:num|hoogte_tov_nap:num|zakking_cumulatief:num|' \
             'datum:dat|bouwblokzijde:num|eigenaar:num|indicatie_beveiligd:bool|stadsdeel:str|nabij_adres_text:str|' \
             'locatie:str|zakkingssnelheid:num|status:str|bouwblok:str|blokeenheid:num|geometrie:geo'
    pattern = re.compile('(\w+):(\w+)\|?')
    export = format
    for (attr_name, attr_type) in re.findall(pattern, format):
        attr_value = type_convert(attr_type, meetbout.get(attr_name, None))
        export = export.replace(f'{attr_name}:{attr_type}', attr_value)
    return export


def export_meetbouten(host, file):
    """Export meetbouten to a file

    The meetbouten that are exposed by the specified API host are retrieved, converted and written to
    the specified output file

    :param host: The API host
    :param file: The name of the file to write the ouput
    :return: None
    """
    api = API(host=host, path='/meetbouten/meetbouten/')

    with open(file, 'w') as fp:
        for entity in api:
            fp.write(_export_meetbout(entity) + '\n')
