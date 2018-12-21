from flask import (
    redirect, url_for, render_template,
    Blueprint, request, flash
)
from flask_wtf import FlaskForm
from wtforms import (IntegerField)
from wtforms.validators import DataRequired

from app.pypnusershub import routes as fnauth
from app.env import db, URL_REDIRECT
from app.t_orders.forms import Order as orderform
from app.models import TProducts, TGroups, TOrders, TDeliveries

from config import config


route = Blueprint('order', __name__)


@route.route('order/add/<id_delivery>', defaults={'id_group': None}, methods=['GET', 'POST'])
@route.route('order/update/<id_delivery>/<id_group>', methods=['GET', 'POST'])
@fnauth.check_auth(3, False, URL_REDIRECT)
def addorupdate(id_delivery, id_group):

    """
    Route affichant un formulaire pour ajouter ou mettre à jour une commande
    L'envoie du formulaire permet l'ajout ou la mise à jour de la commande dans la base
    Retourne un template accompagné du formulaire pré-rempli ou non
    Une fois le formulaire validé on retourne une redirection vers un résumé de la commande
    """
    # test if product is in t_orders table
        # if yes process
        # if not pass
    
    # get delivery informations with id_delivery filter
    delivery = TDeliveries.get_one(id_delivery)
    # get products order in t_products table with id_delivery filter
    q = db.session.query(TProducts)
    q = q.filter(TProducts.id_delivery == id_delivery)
    products = [p.as_dict() for p in q.all()]
    
    # construct form with delivery products
    nbcase = list()
    for p in products:
        orderform.append_nbcase(
            'nb'+str(p['id_product']), 
            p['product_name']
        )
        nbcase.append('nb'+str(p['id_product']))
    form = orderform(request.form)
    form.id_group.choices = TGroups.selectActiveGroups()
    
    if id_group is not None:
        for p in products:
            order = TOrders.get_one((id_group, p['id_product']))
            if request.method == 'GET':
                form = process(form, order)
        del form.id_group
        group =  TGroups.get_one(id_group)
        title = "Commande du relais '"+group['group_name']+"' pour la livraison du " + delivery['delivery_date']
    else:
        
        title = "Nouvelle commande pour la livraison du " + delivery['delivery_date']    

    if request.method == 'POST':
        if id_group is None:
            id_group = form.data['id_group']
            group =  TGroups.get_one(id_group)
        form_order = pops(form.data)
        for key, value in form_order.items():
            post_order = dict()
            post_order['id_group'] = id_group
            if key[0:2] == 'nb':
                post_order['id_product'] = key[2:]
                post_order['product_case_number'] = value
                TOrders.update(post_order)
        return render_template(
            'group_order_info.html', form_order=form_order, group=group, products=products, title="Résumé de la commande pour la livraison du " + delivery['delivery_date']
        )
        # if form.validate_on_submit() and form.validate():

    #     else:
    #         errors = form.errors
    #         flash(errors)

    return render_template(
        'order.html', nbcase=nbcase,  form=form, title=title
    )


@route.route('order/delete/<id_product>/<id_group>', methods=['GET', 'POST'])
@fnauth.check_auth(6, False, URL_REDIRECT)
def delproduct(id_product, id_group):
    """
    Route qui supprime la commande d'un relais dont les id_product et id_group sont en paramètres
    Retourne une redirection vers la liste des commandes
    """
    TOrders.delete(id_product, id_group)
    return redirect(url_for('order.orders'))


def pops(form):
    """
    Methode qui supprime les éléments indésirables du formulaires
    Avec pour paramètre un formulaire
    """
    form.pop('submit')
    form.pop('csrf_token')
    return form


def process(form, order):
    """
    Methode qui rempli le formulaire par les données de l'éléments concerné
    Avec pour paramètres un formulaire et un product
    """
    nbc = 'nb'+str(order['id_product'])
    form[nbc].process_data(order['product_case_number'])
    form.id_group.process_data(order['id_group'])
    return form
