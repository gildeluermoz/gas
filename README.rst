GAS
=========

Titre inspiré des GROUPEMENTS d'ACHATS SOLIDAIRES italiens

Présentation
------------

GAS est un outil en ligne permettant de gérer les commandes des associations de consommateurs. 
Les développements sont volontairement orientés vers le logiciel libre. Le code s'appuie sur des langages et des librairies open-source. D'autres développeurs peuvent enrichir l'outil.
L'outil est développé pour l'association Sens Pressés de Briançon (Hautes-Alpes)
L'objectif est de le rendre générique et paramétrable au maximum.


Les fonctionnalités
-------------------
* Gestion d'une liste d'adhérents
    * affectation de droits d'accès différentiés avec des profils adhérent, relais, gestionnaire, administrateur.
    * rattachement à un relais
    * possibilité de désactiver un adhérent
    * possibilité pour chacun de gérer son mot de passe
* Gestion d'une liste de relais
* Gestion des produits mis en commande
Comme les prix d'achat et ventes peuvent changer d'une livraison à l'autre, il faut recréer chacun des produits pour chacune des livraisons)
* Gestion des livraisons
    * activation/désactivation, 
    * date limite de commande et date de livraison, 
    * ouverture/fermeture des commandes.
* Gestion des commandes
    * formulaire de commande par relais
        * fiche récap une fois la commande relais enregistrée
        * ajout et modification (pas d'erreur possible : pas de doublons)
        * possibilité pour le gestionnaire uniquement d'affecter une réduction pour un relais (100% pour un relais solidaire par exemple)
    * fiche récapitulative
        * toutes les commandes par relais
        * totaux (nbre de caisses, achats, ventes, bilan)
        * impression
            * commande par relais (bandelettes)
            * récapitulatif 

Installation
-----------

Consulter la documentation :  `<https://github.com/gildeluermoz/gas/tree/master/docs>`_


License
-------

* OpenSource - GPLv3
* Copyright (c) 2019 - Gil Deluermoz
