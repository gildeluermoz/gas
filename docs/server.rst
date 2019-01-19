=======
SERVEUR
=======

Cette documentation décrit l'installation du serveur accueillant GAS.

Prérequis
=========

* Ressources minimum serveur :

Un serveur disposant d'au moins de 1 Go RAM et de 5 Go d'espace disque.
Sudo est installé

* Disposer d'un utilisateur linux autre que root (recommandé)
Cet utilisateur est membre de sudo
 
  ::  
  
    sudo adduser --home /home/myuser myuser


* Récupérer le zip de l'application sur le Github du projet (X.Y.Z à remplacer par la version souhaitée de UsersHub)
 
  ::  
  
    cd /tmp
    wget https://github.com/gildeluermoz/gas/archive/X.Y.Z.zip
    unzip X.Y.Z.zip
    mkdir -p /home/myuser/gas
    cp gas-X.Y.Z/* /home/myuser/gas
    cd /home/gas


Installation et configuration du serveur
========================================

Installation pour Debian 9.
    * Cette documentation concerne une installation sur Debian. Pour tout autre environemment les commandes sont à adapter.
    * Vérifier que le répertoire ``/tmp`` existe et que l'utilisateur ``www-data`` y ait accès en lecture/écriture.


Installation de l'environnement logiciel
----------------------------------------
 
  ::  
  
    nano /etc/apt/sources.list
        #ajouter les backports et retirer les src 
    apt-get update
    apt-get upgrade
    apt-get install -y sudo ca-certificates
    adduser --home /home/myuser myuser
    adduser myuser sudo
    usermod -g www-data myuser
    usermod -a -G root myuser
        #Fermer la console et la réouvrir pour que les modifications soient prises en compte.
    
    sudo apt-get install -y postgresql
    sudo apt-get install -y python3 python3-dev python3-pip python3-setuptools python-virtualenv python3-wheel build-essential libssl-dev python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
    pip3 install --upgrade pip virtualenv
    apt-get install -y curl
    su myuser
    cd
    curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
    sudo apt-get install -y nodejs
    sudo apt-get install -y supervisor
    sudo apt-get install -y apache2
    sudo a2enmod rewrite
    sudo a2enmod proxy
    sudo a2enmod proxy_http
    sudo apache2ctl restart
    sudo -n -u postgres -s psql -c "CREATE ROLE my_pg_user WITH LOGIN PASSWORD 'userpass_change_it';"
    sudo -n -u postgres -s psql -c "CREATE ROLE my_pg_superuser WITH SUPERUSER LOGIN PASSWORD 'userpass_change_it';"

    # pour accéder à postresql avec pg_admin
    sed -e "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" -i /etc/postgresql/9.6/main/postgresql.conf
    sudo nano /etc/postgresql/9.6/main/pg_hba.conf
        # ajouter un ligne avec
        # host  all all 0.0.0.0/0  md5
    sudo service postgresql restart


* Création d'un super-utilisateur PostgreSQL
 
  ::  
  
    sudo su postgres
    psql
    CREATE ROLE gasuser WITH SUPERUSER LOGIN PASSWORD 'monpassachanger';
    \q
    exit

L'utilisateur ``gasuser`` est super utilisateur de PostgreSQL il sera utilisé par l'application pour se connecter à sa propre base de données mais aussi à toutes les autres bases qu'UsersHub doit gérer.

L'application fonctionne avec par default le mot de passe ``monpassachanger`` mais il est conseillé de le modifier !  
