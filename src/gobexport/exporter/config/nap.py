class PeilmerkenExportConfig:
    """Peilmerken config

    Example:
        identificatie: 22081299:
        http://localhost:5000/gob/nap/peilmerken/?id=22081299
        =>
        $$22081299$$|$$$$|120951|491840|-1,9926||$$20010920$$|||$$$$|$$N$$|$$Orionplantsoen 7$$|$$$$||$$A$$
        |$$PB15 $$|1|POINT (120951.0 491840.0)

    """
    format = 'identificatie:str|hoogte_tov_nap:num:3|jaar:num|merk_id:num|omschrijving:str|' \
             'windrichting:str|x_coordinaat_muurvlak:num|y_coordinaat_muurvlak:num|rws_nummer:str|' \
             'geometrie:geo'
    path = '/gob/nap/peilmerken/?view=enhanced'
