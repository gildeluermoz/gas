from flask import (
    redirect, url_for, render_template,
    Blueprint, request, flash
)

from sqlalchemy import exc

from app.pypnusershub import route as fnauth
from app.pypnusershub.db.tools import user_from_token

from app.env import db, URL_REDIRECT
from app.t_products import forms as t_productsforms
from app.models import TProducts, TGroups, TDeliveries, TOrders

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
    fLine = ['Actif', 'Livraison', 'Nom', 'Unité', 'Achat', 'Vente', 'Poids', 'Remarques']  # noqa
    columns = ['active', 'id_product', 'delivery_name', 'product_name', 'product_unit', 'buying_price', 'selling_price', 'case_weight', 'product_comment']  # noqa
    contents = TProducts.get_all(columns=columns, orderbyfields=['id_product'], sortdirection='desc')
    tab = []
    for data in contents:
        g = data
        g['delivery_name'] = '<a href="'+config.URL_APPLICATION + '/delivery/info/' + str(data['delivery_rel']['id_delivery'])+'">'+ data['delivery_rel']['delivery_name'] + '</a>'
        tab.append(g)

    return render_template(
        "table_database.html",
        user_right=user_right,
        fLine=fLine,
        line=columns,
        table=tab,
        sortdirection='desc',
        sortcol=1,
        see="False",
        duplicate="True",
        key="id_product",
        pathI=config.URL_APPLICATION + "/product/info/",
        pathU=config.URL_APPLICATION + "/product/update/",
        pathD=config.URL_APPLICATION + "/product/delete/",
        pathA=config.URL_APPLICATION + "/product/add/new",
        pathC=config.URL_APPLICATION + "/product/duplicate/",
        name="un produit",
        name_list="Produits"
    )


@route.route('product/add/new', defaults={'id_product': None}, methods=['GET', 'POST'])
@route.route('product/update/<id_product>', methods=['GET', 'POST'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def addorupdate(id_product):

    """
    Route affichant un formulaire vierge ou non (selon l'url) pour ajouter ou mettre à jour un produit
    L'envoie du formulaire permet l'ajout ou la mise à jour du produit dans la base
    Retourne un template accompagné du formulaire pré-rempli ou non selon le paramètre id_product
    Une fois le formulaire validé on retourne une redirection vers la liste de produits
    """
    form = t_productsforms.Product()
    form.id_delivery.choices = TDeliveries.selectActiveDeliveries(False)

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

@route.route('product/duplicate/<id_product>', methods=['GET', 'POST'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def duplicate(id_product):

    """
    Route affichant un formulaire avec duplication d'un produit
    L'envoie du formulaire permet l'ajout du produit dans la base
    Retourne un template accompagné du formulaire pré-rempli ou non selon le paramètre id_product
    Une fois le formulaire validé on retourne une redirection vers la liste de produits
    """
    form = t_productsforms.Product()
    form.id_delivery.choices = TDeliveries.selectActiveDeliveries(False)
    product = TProducts.get_one(id_product)

    if request.method == 'GET':
        product['id_delivery']=0
        form = process(form, product)

    if request.method == 'POST':
        if form.validate_on_submit() and form.validate():
            form_product = pops(form.data)
            form_product.pop('id_product')
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
    usedProducts = db.session.query(TOrders).filter(TOrders.id_product == id_product).all()
    if len(usedProducts) == 0:
        try:
            TProducts.delete(id_product)
            return redirect(url_for('product.products'))
        except (exc.SQLAlchemyError, exc.DBAPIError) as e:
            flash("Peut-être que tu essaies de faire quelque chose qui n'est pas cohérent.")
            flash(e)
            return render_template(
                'error.html', 
                title="Houps ! Une erreur s'est produite"
            )
    else:
        flash("Tu essaies de supprimer un produit qui est utilisé dans la commande de " + str(len(usedProducts)) + " relais.")
        flash("Tu veux peut-être désactiver ce produit pour qu'il ne soit plus comptabilisé dans la commande. Pour cela ouvre le formulaire du produit pour le modifier et décoche 'Actif'.")
        flash("Si tu souhaites réellement supprimer le produit, il faut au préalable supprimer toutes les commandes qui portent sur ce produit.")
        return render_template(
            'error.html', 
            title="Houps !"
        )


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
    form.product_unit.process_data(product['product_unit'])
    form.buying_price.process_data(product['buying_price'])
    form.selling_price.process_data(product['selling_price'])
    form.case_weight.process_data(product['case_weight'])
    form.product_comment.process_data(product['product_comment'])
    return form
