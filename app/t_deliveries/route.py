from flask import (
    Blueprint, redirect, url_for, render_template,
    request, flash
)
from datetime import datetime

from app.pypnusershub import routes as fnauth

from app.env import URL_REDIRECT

from app import genericRepository
from app.t_deliveries import forms as deliveriesforms
from app.models import TDeliveries
from config import config


route = Blueprint('delivery', __name__)

"""
Route des livraisons
"""


@route.route('delivery/list', methods=['GET', 'POST'])
@fnauth.check_auth(3, False, URL_REDIRECT)
def deliveries():

    """
    Route qui affiche la liste des livraisons
    Retourne un template avec pour paramètres :
                                            - une entête de tableau --> fLine
                                            - le nom des colonnes de la base --> line
                                            - le contenu du tableau --> table
                                            - le chemin de mise à jour --> pathU
                                            - le chemin de suppression --> pathD
                                            - le chemin d'ajout --> pathA
                                            - le chemin de la page d'information --> pathI
                                            - une clé (clé primaire dans la plupart des cas) --> key
                                            - un nom (nom de la table) pour le bouton ajout --> name
                                            - un nom de listes --> name_list
                                            - ajoute une colonne pour accéder aux infos de l'utilisateur --> see
    """

    fLine = ['active', 'ID', 'Nom', 'Date', 'Commentaire']
    columns = ['active', 'id_delivery', 'delivery_name', 'delivery_date', 'delivery_comment']
    contents = TDeliveries.get_all(columns)
    for c in contents:
        c['delivery_date'] = datetime.strptime(c['delivery_date'],'%Y-%m-%d').strftime('%d/%m/%Y')
    return render_template(
        'table_database.html',
        table=contents,
        fLine=fLine,
        line=columns,
        pathI=config.URL_APPLICATION + '/delivery/info/',
        pathU=config.URL_APPLICATION + '/delivery/update/',
        key='id_delivery',
        pathD=config.URL_APPLICATION + '/delivery/delete/',
        pathA=config.URL_APPLICATION + '/delivery/add/new',
        pathP=config.URL_APPLICATION + '/order/info/',
        otherCol='True',
        Members="Commandes",
        name="une livraison",
        name_list="Livraisons",
        see='False'
    )


@route.route('delivery/add/new', defaults={'id_delivery': None}, methods=['GET', 'POST'])
@route.route('delivery/update/<id_delivery>', methods=['GET', 'POST'])
@fnauth.check_auth(6, False, URL_REDIRECT)
def addorupdate(id_delivery):
    """
    Route affichant un formulaire vierge ou non (selon l'url) pour ajouter ou mettre à jour une livraison
    L'envoie du formulaire permet l'ajout ou la mise à jour de l'éléments dans la base
    Retourne un template accompagné du formulaire
    Une fois le formulaire validé on retourne une redirection vers la liste des livraisons
    """

    form = deliveriesforms.Delivery()
    if id_delivery == None:
        if request.method == 'POST':
            if form.validate_on_submit() and form.validate():
                form_org = pops(form.data)
                form_org.pop('id_delivery')
                TDeliveries.post(form_org)
                return redirect(url_for('delivery.deliveries'))
            else:
                flash(form.errors)
    else:
        o = TDeliveries.get_one(id_delivery)
        if request.method == 'GET':
            form = process(form, o)
        if request.method == 'POST':
            if form.validate_on_submit() and form.validate():
                form_org = pops(form.data)
                form_org['id_delivery'] = o['id_delivery']
                TDeliveries.update(form_org)
                return redirect(url_for('delivery.deliveries'))
            else:
                flash(form.errors)
    return render_template('delivery.html', form=form, title="Formulaire des livraisons")


@route.route('delivery/delete/<id_delivery>', methods=['GET', 'POST'])
@fnauth.check_auth(6, False, URL_REDIRECT)
def delete(id_delivery):
    """
    Route qui supprime une livraison dont l'id est donné en paramètres dans l'url
    Retourne une redirection vers la liste des livraisons
    """

    TDeliveries.delete(id_delivery)
    return redirect(url_for('delivery.deliveries'))

def pops(form):

    """
    Methode qui supprime les éléments indésirables du formulaires
    Avec pour paramètre un formulaire
    """
    form.pop('submit')
    form.pop('csrf_token')
    return form

def process(form, org):

    """
    Methode qui rempli le formulaire par les données de l'éléments concerné
    Avec pour paramètres un formulaire et une livraison
    """

    form.delivery_name.process_data(org['delivery_name'])
    form.delivery_date.process_data(datetime.strptime(org['delivery_date'],'%Y-%m-%d'))
    form.delivery_comment.process_data(org['delivery_comment'])
    form.active.process_data(org['active'])
    return form
