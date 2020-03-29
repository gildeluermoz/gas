GAS
=========

Titre inspiré des GROUPEMENTS d'ACHATS SOLIDAIRES italiens

Présentation
------------

GAS est un outil en ligne permettant de gérer les commandes des associations de consommateurs. 
Les développements sont volontairement orientés vers le logiciel libre. Le code s'appuie sur des langages et des librairies open-source. D'autres développeurs peuvent enrichir l'outil.
L'outil a été développé initialement pour l'association Sens Pressés de Briançon (Hautes-Alpes). Il est depuis utilisé par l'association Désalternativ de l'Argentière la Bessée.
L'objectif est de le rendre générique et paramétrable au maximum.


Les fonctionnalités
-------------------
* Gestion d'une liste d'adhérents
    * affectation de droits d'accès différentiés avec des profils adhérent, relais, gestionnaire, administrateur.
    * rattachement à un relais
    * possibilité de désactiver un adhérent
    * possibilité pour chacun de gérer son mot de passe
    
* Gestion d'une liste de relais
    * seuls les relais peuvent commander

* Gestion des produits mis en commande
    * ratachement à une livraison, nom du produit, prix d'achat, prix de vente, commentaire
    * possibilité de dupliquer facilement un produit pour une autre commande (le prix d'un produit peut évoluer d'une commande à l'autre)
    * possibilité de désactiver un produit non disponible, même en cours de commande. Le prix de la commande est alors corrigé.
    
* Gestion des livraisons
    * activation/désactivation, 
    * date limite de commande et date de livraison, 
    * ouverture/fermeture des commandes.
    * génération automatique d'un lien vers le formaulaire pour commander
    
* Gestion des commandes
    * formulaire de commande par relais
        * fiche récap une fois la commande relais enregistrée
        * on peut revenir autant de fois que souhaité sur sa commande, pas d'erreur possible : pas de doublons
        * possibilité, pour le gestionnaire uniquement, d'affecter une réduction pour un relais (100% pour un relais solidaire par exemple)
        
    * fiche récapitulative
        * toutes les commandes par relais
        * totaux (nbre de caisses, total des achats et des ventes, bilan)
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
