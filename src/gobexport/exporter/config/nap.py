from gobexport.exporter.dat import dat_exporter


class PeilmerkenExportConfig:
    """Peilmerken config

    Example:
        identificatie: 11080002:
        http://localhost:5000/gob/nap/peilmerken/?id=11080002
        =>
        $$11080002$$|1,538|2018|3|$$Chassestraat 59 "Wassenaerschool"(x = inspringende hoek; y = bovenkant
        gemetselde rollaag van de plint)$$|$$O$$|-31,0|83,0||POINT (119193.3 486914.2)

    """
    products = {
        'dat': {
            'exporter': dat_exporter,
            'endpoint': '/gob/nap/peilmerken/?view=enhanced',
            'filename': 'NAP_PEILMERK.dat',
            'mime_type': 'plain/text',
            'format': 'identificatie:str|hoogteTovNap:num:4|jaar:num|merk.code:num|omschrijving:str|'
                      'windrichting:str|xCoordinaatMuurvlak:num|yCoordinaatMuurvlak:num|rwsNummer:str|'
                      'geometrie:geo'
        }
    }
