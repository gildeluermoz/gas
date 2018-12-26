from flask import (
    redirect, url_for, render_template,
    Blueprint, request, flash
)
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired

from sqlalchemy import exc, and_

from datetime import datetime

from app.pypnusershub import route as fnauth
from app.env import db, URL_REDIRECT
from app.t_orders.forms import Order as orderform
from app.models import (TProducts, TGroups, TOrders, 
    TDeliveries, VOrdersResult, VGroupOrdersDetail, VGroupOrdersSum)

from config import config


route = Blueprint('order', __name__)


@route.route('order/info/<id_delivery>', methods=['GET'])
@fnauth.check_auth(3, False, URL_REDIRECT)
def info(id_delivery):
    """
    Route affichant le résumé d'une commande
    Des liens permettent de modifier la commande d'un relais
    """

     # get delivery informations with id_delivery filter
    delivery = TDeliveries.get_one(id_delivery)
    delivery['delivery_date'] = datetime.strptime(delivery['delivery_date'],'%Y-%m-%d').strftime('%d/%m/%Y')

    # get products order in t_products table with id_delivery filter
    q = db.session.query(TOrders.id_group).distinct()
    q.join(TProducts, TProducts.id_product == TOrders.id_product)
    q = q.filter(TProducts.id_delivery == id_delivery)
    data = q.all() 
    if data:
         ordergroups = [p[0] for p in data]
    else:
        flash("Aucun relais n'a passé commande pour le moment sur cette livraison.")
        return render_template(
            'error.html', 
            title="Houps ! Un petit soucis"
        )

    # get orders details
    orders = list()
    for og in ordergroups:
        order = dict()
        q = db.session.query(TOrders)
        q = q.join(TProducts, TProducts.id_product == TOrders.id_product)
        q = q.join(TDeliveries, TDeliveries.id_delivery == TProducts.id_delivery)
        q = q.filter(and_(TProducts.id_delivery == id_delivery, TOrders.id_group == og))
        order['products'] = [{'product':o.product_rel.as_dict(), 'nb':o.product_case_number, 'price':o.product_case_number*o.product_rel.selling_price} for o in q.all()]
        order['group'] = TGroups.get_one(og)
        mysum = 0
        for p in order['products']:
            mysum = mysum + p['price'] 
            order['group_price'] = mysum
        orders.append(order)

    # get orders sums
    q = db.session.query(VOrdersResult).filter(VOrdersResult.id_delivery == id_delivery)
    results = list()
    nbc = 0
    w = 0 
    selling = 0 
    buying = 0
    benef = 0
    for r in q.all():
        result = dict()
        result = r.as_dict()
        results.append(result)
        nbc = nbc + r.case_number
        w = w + r.weight
        selling = selling + r.selling_price
        buying = buying + r.buying_price
        benef = benef + r.benefice
    sums = dict()
    sums['case_number'] = nbc
    sums['weight'] = w
    sums['selling'] = selling
    sums['buying'] = buying
    sums['benefice'] = benef

    return render_template(
        'info_order.html', 
        orders=orders, 
        delivery=delivery,
        results=results, 
        sums=sums, 
        title="Commandes pour la livraison du " + delivery['delivery_date']
    )

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
    
    # get delivery informations with id_delivery filter
    delivery = TDeliveries.get_one(id_delivery)
    delivery['delivery_date'] = datetime.strptime(delivery['delivery_date'],'%Y-%m-%d').strftime('%d/%m/%Y')
    is_open = delivery['is_open']

    if is_open:
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
                try:
                    order = TOrders.get_one((id_group, p['id_product']))
                    if request.method == 'GET':
                        form = process(form, order)
                except:
                    pass   
            del form.id_group
            group =  TGroups.get_one(id_group)
            title = "Commande du relais '"+group['group_name']+"' pour la livraison du " + delivery['delivery_date']
        else:
            title = "Nouvelle commande pour la livraison du " + delivery['delivery_date']    
        
        if request.method == 'POST':
            if form.validate_on_submit() and form.validate():
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
                q = db.session.query(VGroupOrdersDetail)
                q = q.filter(and_(VGroupOrdersDetail.id_delivery == id_delivery, VGroupOrdersDetail.id_group == id_group))
                group_order = [go.as_dict() for go in q.all()]
                group_order_sum = VGroupOrdersSum.get_one((id_delivery, id_group))
                return render_template(
                    'info_group_order.html', 
                    group_order=group_order, 
                    group_order_sum=group_order_sum, 
                    group=group, 
                    delivery=delivery, 
                    title="Résumé de la commande pour la livraison du " + delivery['delivery_date']
                )
            else:
                errors = form.errors
                flash(errors)
        
        return render_template(
            'order.html', nbcase=nbcase,  form=form, title=title
        )
    else:
        flash("Aucune modification n'est possible sur cette commande.")
        return render_template(
            'error.html', 
            title="La commande est fermée."
        )


@route.route('order/delete/<id_product>/<id_group>', methods=['GET', 'POST'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def delproduct(id_product, id_group):
    """
    Route qui supprime la commande d'un relais dont les id_product et id_group sont en paramètres
    Retourne une redirection vers la liste des commandes
    """
    try:
        TOrders.delete(id_product, id_group)
        return redirect(url_for('order.orders'))
    except (exc.SQLAlchemyError, exc.DBAPIError) as e:
        flash("Peut-être que tu essaies de faire quelque chose qui n'est pas cohérent.")
        flash(e)
        return render_template(
            'error.html', 
            title="Houps ! Une erreur s'est produite"
        )


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
    form[nbc].process_data(order['product_case_number'] or 0)
    form.id_group.process_data(order['id_group'])
    return form
