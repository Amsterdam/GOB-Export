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
            'endpoint': '/gob/meetbouten/meetbouten/?view=enhanced',
            'filename': 'MBT_MEETBOUT.dat',
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
            'endpoint': '/gob/meetbouten/metingen/?view=enhanced',
            'filename': 'MBT_METING.dat',
            'mime_type': 'plain/text',
            'format': 'identificatie:num|datum:dat|typeMeting:str|hoogteTovNap:num:4|zakking:num:1|'
                      'hoortBijMeetbout.bronwaarde:str|refereert_aan_referentiepunten.0.bronwaarde:str|'
                      'refereert_aan_referentiepunten.1.bronwaarde:str|'
                      'refereert_aan_referentiepunten.2.bronwaarde:str|zakkingssnelheid:num:1|'
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
            'endpoint': '/gob/meetbouten/referentiepunten/?view=enhanced',
            'filename': 'MBT_REFERENTIEPUNT.dat',
            'mime_type': 'plain/text',
            'format': 'identificatie:num|geometrie:coo:x|geometrie:coo:y|'
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
    products = {
        'dat': {
            'exporter': dat_exporter,
            'endpoint': '/gob/meetbouten/rollagen/?view=enhanced',
            'filename': 'MBT_ROLLAAG.dat',
            'mime_type': 'plain/text',
            'format': 'identificatie:str|idx:num|geometrie:coo:x|geometrie:coo:y|geometrie:geo'
        }
    }
