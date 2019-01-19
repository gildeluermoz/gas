===========
APPLICATION
===========

Configuration de la base de données PostgreSQL
==============================================

* Créer et mettre à jour le fichier ``config/settings.ini``
 
  ::  
  
    cp config/settings.ini.sample config/settings.ini
    nano config/settings.ini

Renseigner le nom de la base de données, l'utilisateur PostgreSQL et son mot de passe. Il est possible mais non conseillé de laisser les valeurs proposées par défaut. 

ATTENTION : Les valeurs renseignées dans ce fichier sont utilisées par le script d'installation de la base de données ``install_db.sh``. L'utilisateurs PostgreSQL doit être en concordance avec celui créé lors de la dernière étape de l'installation serveur ``Création d'un utilisateur PostgreSQL``. 


Création de la base de données
==============================

* Création de la base de données et chargement des données initiales
 
  ::  
  
    cd /home/myuser/gas
    sudo ./install_db.sh


Configuration de l'application
==============================

* Se loguer sur le serveur avec l'utilisateur linux ``myuser``
   

* Installation et configuration de l'application
 
  ::  
  
    cd /home/myuser/gas
    ./install_app.sh

Vérifier et mettre à jour le paramètre `URL_APPLICATION` dans `config/config.py`


Configuration apache
====================

Créer le fichier `/etc/apache2/sites-avalaible/gas.conf` avec ce contenu
 
  ::  
  
    <Location /gas>
        ProxyPass  http://localhost:3001
        ProxyPassReverse  http://localhost:3001
    </Location>

Activé le site et recharger la conf apache
 
  ::  
  
    sudo a2ensite gas.conf
    sudo service apache2 restart

* Pour tester, se connecter à l'application via http://mon-domaine.fr/gas et les login et pass admin/admin

* choisir le mode d'authentification dans le fichier ``config/config.php``

Mise à jour de l'application
----------------------------

* Suivre les instructions disponibles dans la doc de la release choisie

Personnalisation
----------------

Todo