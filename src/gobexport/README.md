# Tests

De checks zijn uitgebreid met test op kolom lengte. Voorbeeld:

    "minlength_col_1": [
        1,
        2
    ],
    "maxlength_col_1": [
        3,
        5
    ],

Specificeert dat kolom 1 een minimale lengte moeten hebben van 1 t/m 2 en de maximale lengte tussen 3 en 5 (inclusief 3 en 5 zelf).

Zo kunnen niet alleen verplichte attributen worden getest, maar kan ook worden getest op andere attribuut eigenschappen. Bijvoorbeeld dat een id altijd 14 karakters lang is:

    "min_col_1": [
        14,
        14
    ],
    "max_col_1": [
        14,
        14
    ],

 Of dat een id altijd 8 of 14 (maar niet iets daartussen) karakters lang is:
 
      "min_col_1": [
         8,
         8
     ],
     "max_col_1": [
         14,
         14
     ],
 
  Verder kan worden opgegeven of een kolom, of een combinatie van kolommen, of combinaties daarvan uniek moeten zijn.
  
  Om bijvoorbeeld aan te geven dat de waarden in kolom 1 en de waarden in  kolom 3 + kolom 7 uniek moeten zijn:
  
      "unique_cols": [[1], [3,7]]
  
  Of om aan te geven dat alleen de waarden in kolom 2 uniek moeten zijn:
  
      "unique_cols": [[2]]
  
