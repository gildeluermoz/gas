#!/bin/bash

. config/settings.ini

# Création des fichiers de configuration
cd config

echo "Création du fichier de configuration ..."
if [ ! -f config.py ]; then
  cp config.py.sample config.py
fi

echo "préparation du fichier config.py..."
sed -i "s/SQLALCHEMY_DATABASE_URI = .*$/SQLALCHEMY_DATABASE_URI = \"postgresql:\/\/$user_pg:$user_pg_pass@$db_host:$pg_port\/$db_name\"/" config.py

cd ..

# Installation de l'environement python

echo "Installation du virtual env..."
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Installation de l'environement javascript

cd app/static
npm install
cd ../..


#Lancement de l'application
DIR=$(readlink -e "${0%/*}")
sudo -s cp gas-service.conf /etc/supervisor/conf.d/
sudo -s sed -i "s%APP_PATH%${DIR}%" /etc/supervisor/conf.d/gas-service.conf

sudo -s supervisorctl reread
sudo -s supervisorctl reload