from flask import (
    redirect, url_for, render_template,
    Blueprint, request, flash
)

from flask_bcrypt import (
    generate_password_hash
)

from app.pypnusershub import route as fnauth
from app.pypnusershub.db.tools import user_from_token

from app.env import URL_REDIRECT
from app.t_products import forms as t_productsforms
from app.models import TProducts, TGroups, TDeliveries

from config import config


route = Blueprint('product', __name__)


@route.route('products/list', methods=['GET'])
@fnauth.check_auth(2, False, URL_REDIRECT)
def products():

    """
    Route qui affiche la liste des utilisateurs
    Retourne un template avec pour paramètres :
        - les droits de l'utilisateur selon son porfil --> user_right
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
    user_profil = user_from_token(request.cookies['token']).id_profil
    user_right = list()
    if user_profil >= 4:
        user_right = ['C','R','U','D']
    else:
        user_right = ['R']
    fLine = ['Actif', 'ID', 'Livraison', 'Nom', 'Achat', 'Vente', 'Poids', 'Remarques']  # noqa
    columns = ['active', 'id_product', 'delivery_name', 'product_name', 'buying_price', 'selling_price', 'case_weight',  'product_comment']  # noqa
    contents = TProducts.get_all(columns)
    tab = []
    for data in contents:
        g = data
        g['delivery_name'] = data['delivery_rel']['delivery_name']
        tab.append(g)

    return render_template(
        "table_database.html",
        user_right=user_right,
        fLine=fLine,
        line=columns,
        table=tab,
        see="False",
        key="id_product",
        pathI=config.URL_APPLICATION + "/product/info/",
        pathU=config.URL_APPLICATION + "/product/update/",
        pathD=config.URL_APPLICATION + "/product/delete/",
        pathA=config.URL_APPLICATION + "/product/add/new",
        name="un produit",
        name_list="Produits"
    )


@route.route('product/add/new', defaults={'id_product': None}, methods=['GET', 'POST'])
@route.route('product/update/<id_product>', methods=['GET', 'POST'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def addorupdate(id_product):

    """
    Route affichant un formulaire vierge ou non (selon l'url) pour ajouter ou mettre à jour un utilisateurs
    L'envoie du formulaire permet l'ajout ou la mise à jour de l'utilisateur dans la base
    Retourne un template accompagné du formulaire pré-rempli ou non selon le paramètre id_product
    Une fois le formulaire validé on retourne une redirection vers la liste de produits
    """
    form = t_productsforms.Product()
    form.id_delivery.choices = TDeliveries.selectActiveDelivery()

    if id_product is not None:
        product = TProducts.get_one(id_product)
        if request.method == 'GET':
            form = process(form, product)

    if request.method == 'POST':
        if form.validate_on_submit() and form.validate():
            form_product = pops(form.data)
            form_product.pop('id_product')

            if id_product is not None:
                form_product['id_product'] = product['id_product']
                TProducts.update(form_product)
            else:
                TProducts.post(form_product)
            return redirect(url_for('product.products'))
        else:
            errors = form.errors
            flash(errors)

    return render_template(
        'product.html', form=form, title="Formulaire des produits pour une livraison"
    )


@route.route('product/delete/<id_product>', methods=['GET', 'POST'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def delproduct(id_product):
    """
    Route qui supprime un utilisateur dont l'id est donné en paramètres dans l'url
    Retourne une redirection vers la liste d'utilisateurs
    """
    TProducts.delete(id_product)
    return redirect(url_for('product.products'))


def pops(form):
    """
    Methode qui supprime les éléments indésirables du formulaires
    Avec pour paramètre un formulaire
    """
    form.pop('submit')
    form.pop('csrf_token')
    return form


def process(form, product):
    """
    Methode qui rempli le formulaire par les données de l'éléments concerné
    Avec pour paramètres un formulaire et un product
    """

    form.active.process_data(product['active'])
    form.id_delivery.process_data(product['id_delivery'])
    form.product_name.process_data(product['product_name'])
    form.buying_price.process_data(product['buying_price'])
    form.selling_price.process_data(product['selling_price'])
    form.case_weight.process_data(product['case_weight'])
    form.product_comment.process_data(product['product_comment'])
    return form
