class PeilmerkenExportConfig:
    """Peilmerken config

    Example:
        identificatie: 11080002:
        http://localhost:5000/gob/nap/peilmerken/?id=11080002
        =>
        $$11080002$$|1,538|2018|3|$$Chassestraat 59 "Wassenaerschool"(x = inspringende hoek; y = bovenkant
        gemetselde rollaag van de plint)$$|$$O$$|-31,0|83,0||POINT (119193.3 486914.2)

    """
    format = 'identificatie:str|hoogte_tov_nap:num:3|jaar:num|merk_id:num|omschrijving:str|' \
             'windrichting:str|x_coordinaat_muurvlak:num|y_coordinaat_muurvlak:num|rws_nummer:str|' \
             'geometrie:geo'
    path = '/gob/nap/peilmerken/?view=enhanced'
