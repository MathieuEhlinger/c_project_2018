# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 12:01:09 2019

@author: Mathieu
"""


"""
size est le nombre de cellules que tu veux dans chaque échantillon
size = [50]
créera une liste de fichiers avec à chaque fois 50 cellules
size = [50,100]
créera, pour chaque fichier en entrée, une fois un fichier avec 50 cellules, puis un avec 100
size = [50, 75,100], size = [50,60,70,80]...
Ca devrait marcher à chaque fois, évite juste les doublons ^^

L'argument 'all' est remplacé par la valeur maximale.
Les valeurs trop élevées sont remplacées par la valeur max.
Les doubblons sont éliminés.

"""

size = [30, 200, 'all']

"""
Rand : tu peux le remplacer par n'importe quel entier positif si tu veux que 
d'autres cellules soit choisies ( on parle de changement de seed ).
"""

rand = 23

"""
Quelques paramètres pour TheOne. 

use_new_format = True
Pour obtenir le nouveau type de fichier, False pour ne pas le générer

death_to_the:old_ways=True
Pour détruire les fichiers tracks, stats et data, False sinon

remove_org_data=True
Pour supprimer les fichiers initiaux, False sinon
"""

use_new_format=True
death_to_the_old_ways=True
remove_org_data_to=True
remove_org_data_dom=True

#-------------------------------
from DOM import main_mom
from TO import run_to

run_to(use_new_format=use_new_format, death_to_the_old_ways=\
       death_to_the_old_ways,remove_org_data=remove_org_data_to)
print('DOM is running...')
main_mom(size = size, rand=rand,directory ='output tadom', 
         remove_org_data_dom=remove_org_data_dom)