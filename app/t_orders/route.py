from flask import (
    redirect, url_for, render_template,
    Blueprint, request, flash, send_file, make_response
)
from flask_wtf import FlaskForm
import flask_excel as excel
from wtforms.validators import DataRequired

from sqlalchemy import exc, and_

from datetime import datetime

from weasyprint import HTML

from app.pypnusershub import route as fnauth
from app.pypnusershub.db.tools import user_from_token
from app.env import db, URL_REDIRECT, APP_ROOT
from app.t_orders.forms import Order as orderform
from app.t_orders.forms import OrderChoice as orderchoiceform
from app.models import (TProducts, TGroups, TOrders, 
    TDeliveries, VOrdersResult, VGroupOrdersDetail, VGroupOrdersSum
)

from config import config


route = Blueprint('order', __name__)


@route.route('order/info/<id_delivery>', methods=['GET'])
@fnauth.check_auth(3, False, URL_REDIRECT)
def info(id_delivery):
    """
    Route affichant le résumé d'une commande
    Des liens permettent de modifier la commande d'un relais
    """

    user_profil = user_from_token(request.cookies['token']).id_profil
    user_right = list()
    if user_profil == 6:
        user_right = ['C','R','U','D']
    elif user_profil >= 3 and user_profil < 6:
        user_right = ['C','R','U']
    else:
        user_right = ['R']

     # get delivery informations with id_delivery filter
    delivery = TDeliveries.get_one(id_delivery)
    delivery['delivery_date'] = datetime.strptime(delivery['delivery_date'],'%Y-%m-%d').strftime('%d/%m/%Y')

    # get products order in t_products table with id_delivery filter
    q = db.session.query(TOrders.id_group, TGroups.group_name).distinct()
    q = q.join(TProducts, TProducts.id_product == TOrders.id_product)
    q = q.join(TGroups, TGroups.id_group == TOrders.id_group)
    q = q.filter(and_(TProducts.id_delivery == id_delivery, TProducts.active == True))
    q = q.order_by(TGroups.group_name)
    data = q.all() 
    if data:
         ordergroups = [p[0] for p in data]
    else:
        flash("Aucun produit n'a été enregistré pour cette livraison.")
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
        q = q.filter(and_(TProducts.id_delivery == id_delivery, TProducts.active == True, TOrders.id_group == og))
        q = q.order_by(TProducts.product_name)
        order['products'] = [{'product':o.product_rel.as_dict(), 'nb':o.product_case_number, 'price':round(o.product_case_number*o.product_rel.selling_price*(1+(o.group_discount/100)),2)} for o in q.all()]
        order['group'] = TGroups.get_one(og)
        mysum = 0
        if len(order['products']) > 0:
            for p in order['products']:
                mysum = mysum + p['price'] 
                order['group_price'] = round(mysum,2)
        else:
            order['group_price'] = 0
            order['products'] = {}

        orders.append(order)
    if len(orders) == 0:
        flash("Aucun " + config.WORD_GROUP + " n'a passé commande pour le moment sur cette livraison.")
        return render_template(
            'error.html', 
            title="Houps ! Un petit soucis"
        )
    # get orders sums
    q = db.session.query(VOrdersResult).filter(VOrdersResult.id_delivery == id_delivery).order_by(VOrdersResult.product_name)
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
    sums['selling'] = round(selling, 2)
    sums['buying'] = buying
    sums['benefice'] = benef

    return render_template(
        'info_order.html', 
        user_right=user_right,
        orders=orders, 
        delivery=delivery,
        results=results, 
        sums=sums, 
        title="Commandes pour la livraison du " + delivery['delivery_date']
    )

def printorderinfo(id_delivery, action='print'):
    """
    Route permettant d'imprimer le résumé d'une commande
    """

     # get delivery informations with id_delivery filter
    delivery = TDeliveries.get_one(id_delivery)
    delivery['delivery_date'] = datetime.strptime(delivery['delivery_date'],'%Y-%m-%d').strftime('%d/%m/%Y')

    # get products order in t_products table with id_delivery filter
    q = db.session.query(TOrders.id_group, TGroups.group_name).distinct()
    q = q.join(TProducts, TProducts.id_product == TOrders.id_product)
    q = q.join(TGroups, TGroups.id_group == TOrders.id_group)
    q = q.filter(and_(TProducts.id_delivery == id_delivery, TProducts.active == True))
    q = q.order_by(TGroups.group_name)
    data = q.all() 
    if data:
         ordergroups = [p[0] for p in data]
    else:
        flash("Aucun produit n'a été enregistré pour cette livraison.")
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
        q = q.filter(and_(TProducts.id_delivery == id_delivery, TProducts.active == True, TOrders.id_group == og))
        q = q.order_by(TProducts.product_name)
        order['products'] = [{'product':o.product_rel.as_dict(), 'nb':o.product_case_number, 'price':round(o.product_case_number*o.product_rel.selling_price*(1+(o.group_discount/100)),2)} for o in q.all()]
        order['group'] = TGroups.get_one(og)
        mysum = 0
        if len(order['products']) > 0:
            for p in order['products']:
                mysum = mysum + p['price'] 
                order['group_price'] = mysum
        orders.append(order)
        if len(orders) == 0:
            flash("Aucun " + config.WORD_GROUP + " n'a passé commande pour le moment sur cette livraison.")
            return render_template(
                'error.html',
                title="Houps ! Un petit soucis"
            )
    # get orders sums
    q = db.session.query(VOrdersResult).filter(VOrdersResult.id_delivery == id_delivery).order_by(VOrdersResult.product_name)
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
    sums['selling'] = round(selling, 2)
    sums['buying'] = buying
    sums['benefice'] = benef

    if action == 'print':
        return render_template(
            'print_order.html', 
            orders=orders, 
            delivery=delivery,
            results=results, 
            sums=sums, 
            title=delivery['delivery_name']
        )
    if action == 'export':
        data = list()
        productline = ['RELAIS/PRODUITS']
        priceline = ['Prix']
        unitline = ['Unité']
        weightline = ['Poids']
        count = 0
        for o in orders:
            line = list()
            line.append(o['group']['group_name'].upper())
            if len(o['products']) > 0:
                for p in o['products']:
                    if count == 0:
                        productline.append(p['product']['product_name'].upper())
                        priceline.append(p['product']['selling_price'])
                        unitline.append(p['product']['product_unit'])
                        weightline.append(p['product']['case_weight'])
                    line.append(p['nb'] or 0)
                if count == 0:
                    productline.append('TOTAL')
                    priceline.append('')
                    unitline.append('')
                    weightline.append('')
                    data.extend([productline, priceline, unitline, weightline])
                    count = 1
                line.append("%.2f" % o['group_price'] or 0)
                data.append(line)
        return data

@route.route('order/print/<id_delivery>', methods=['GET'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def printorder(id_delivery):
    html = HTML(string=printorderinfo(id_delivery, 'print'))
    pdf_file = html.write_pdf(APP_ROOT+'/static/pdf/info_order.pdf')
    return send_file(
        APP_ROOT+'/static/pdf/info_order.pdf',  # file path or file-like object
        'application/pdf',
        as_attachment=True,
        attachment_filename="commande.pdf"
    )

@route.route('order/csvexport/<id_delivery>', methods=['GET'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def csvexport(id_delivery):
    data = printorderinfo(id_delivery, 'export')
    output = excel.make_response_from_array(data, 'csv', file_name="export_data")
    return output


@route.route('order/choice', defaults={'id_delivery': None, 'id_group': None}, methods=['GET', 'POST'])
@route.route('order/choice/<id_delivery>', defaults={'id_group': None}, methods=['GET', 'POST'])
@route.route('order/choice/<id_delivery>/<id_group>', methods=['GET', 'POST'])
@fnauth.check_auth(2, False, URL_REDIRECT)
def orderchoice(id_delivery=None, id_group=None):
    """
    Route affichant un formulaire préalable à la commande
    Il permet de choisir sa commande et son relais
    L'envoi du formulaire passe les paramètres id_delivery et id_group au formulaire principal de la commande
    Retourne un template accompagné du formulaire pré-rempli ou non
    """
    
    user_profil = user_from_token(request.cookies['token']).id_profil
    user_right = list()
    if user_profil >= 2:
        user_right = ['C','R','U','D']

    form = orderchoiceform()
    form.id_delivery.choices = TDeliveries.selectActiveDeliveries(True) # True select only open deliveries

    if user_profil <= 3:
        id_group = user_from_token(request.cookies['token']).id_group
        form.id_group.choices = TGroups.selectActiveGroups(id_group)
    else:
        form.id_group.choices = TGroups.selectActiveGroups()

    title = "Choisir une livraison et un  " + config.WORD_GROUP

    if id_delivery is not None:
        delivery = TDeliveries.get_one(id_delivery)
        title = "Choisir un "+config.WORD_GROUP+" pour la livraison '" + delivery['delivery_name'] + "'"
        if request.method == 'GET':
            form.id_delivery.process_data(id_delivery)
            form.id_group.process_data(id_group)
        del form.id_delivery

    if request.method == 'POST':
        if form.validate_on_submit() and form.validate():
            if id_delivery is None:
                id_delivery = form.data['id_delivery']
            if id_group is None:
                id_group = form.data['id_group']
            return redirect(url_for('order.addorupdate', id_delivery=id_delivery, id_group=id_group))
        else:
            errors = form.errors
            flash(errors)
        
    return render_template('order_choice.html', form=form, title=title)

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

    user_profil = user_from_token(request.cookies['token']).id_profil
    user_right = list()
    if user_profil == 6:
        user_right = ['C','R','U','D']
    elif user_profil >= 3 and user_profil < 6:
        user_right = ['C','R','U']
    else:
        user_right = ['R']

    # get delivery informations with id_delivery filter
    delivery = TDeliveries.get_one(id_delivery)
    delivery['delivery_date'] = datetime.strptime(delivery['delivery_date'],'%Y-%m-%d').strftime('%d/%m/%Y')
    is_open = delivery['is_open']

    if is_open:
        # get active products order in t_products table with id_delivery filter
        q = db.session.query(TProducts)
        q = q.filter(and_(TProducts.id_delivery == id_delivery, TProducts.active == True))
        q = q.order_by(TProducts.id_product)
        products = [p.as_dict() for p in q.all()]
        if len(products) == 0:
            flash("Aucun produit n'a été enregistré pour cette livraison.")
            return render_template(
                'error.html', 
                title="Houps ! Un petit soucis"
            )
        
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
        
        is_update = False
        if id_group is not None:
            # prevent manual change of id_group in the URL for unauthorized users
            if user_profil <= 3 and int(id_group) != user_from_token(request.cookies['token']).id_group:
                id_group = user_from_token(request.cookies['token']).id_group
                flash("Vous ne pouvez passer commande que pour votre " + config.WORD_GROUP)
                return render_template(
                    'error.html', 
                    title="Hum ! petit soucis"
                )
            for p in products:
                try:
                    order = TOrders.get_one((id_group, p['id_product']))
                    is_update = True
                    if request.method == 'GET':
                        form = process(form, order)
                except:
                    pass 
            del form.id_group
            group =  TGroups.get_one(id_group)
            title = "Commande du " + config.WORD_GROUP + " '" + group['group_name']+"' pour la livraison du " + delivery['delivery_date']
        else:
            title = "Nouvelle commande pour la livraison du " + delivery['delivery_date']    
        
        if request.method == 'POST' and user_profil < 4:
            form.hidden_group_discount.process_data(form.data['hidden_group_discount'])
        else:
            form.hidden_group_discount.process_data(form.data['group_discount'])
        if user_profil < 4:
            del form.group_discount

        if request.method == 'POST':
            if form.validate_on_submit() and form.validate():
                if id_group is None:
                    id_group = form.data['id_group']
                    group =  TGroups.get_one(id_group)
                form_order = pops(form.data)
                for key, value in form_order.items():
                    post_order = dict()
                    post_order['id_group'] = id_group
                    post_order['group_discount'] = form.data['hidden_group_discount']
                    if key[0:2] == 'nb':
                        post_order['id_product'] = key[2:]
                        post_order['product_case_number'] = value
                        try:
                            TOrders.update(post_order)
                        except (exc.SQLAlchemyError, exc.DBAPIError) as e:
                            flash("Peut-être que tu essaies de faire quelque chose qui n'est pas cohérent.")
                            flash(e)
                            return render_template(
                                'error.html', 
                                title="Houps ! Une erreur s'est produite"
                            )
                        
                q = db.session.query(VGroupOrdersDetail)
                q = q.filter(and_(VGroupOrdersDetail.id_delivery == id_delivery, VGroupOrdersDetail.id_group == id_group))
                group_order = [go.as_dict() for go in q.all()]
                group_order_sum = VGroupOrdersSum.get_one((id_delivery, id_group))
                return render_template(
                    'info_group_order.html',
                    user_right=user_right, 
                    group_order=group_order, 
                    group_order_sum=group_order_sum, 
                    group=group, 
                    delivery=delivery, 
                    title="Résumé de votre commande (livraison du " + delivery['delivery_date'] +")"
                )
            else:
                errors = form.errors
                flash(errors)
        
        return render_template(
            'order.html', is_update=is_update, nbcase=nbcase,  form=form, title=title
        )
    else:
        flash("Aucune modification n'est possible sur cette commande.")
        return render_template(
            'error.html', 
            title="La commande est fermée."
        )


@route.route('order/delete/<id_delivery>/<id_group>', methods=['GET', 'POST'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def delproduct(id_delivery, id_group):
    """
    Route qui supprime la commande d'un relais dont les id_delivery et id_group sont en paramètres
    Retourne une redirection vers la liste des commandes
    """
     # get products in t_products table with id_delivery filter
    q = db.session.query(TProducts)
    q = q.filter(TProducts.id_delivery == id_delivery)
    try:
        for p in q.all():
            TOrders.delete((id_group, p.id_product))
        return redirect(url_for('order.info',id_delivery=id_delivery))
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
    form.group_discount.process_data(order['group_discount'])
    form.hidden_group_discount.process_data(order['group_discount'])
    return form
