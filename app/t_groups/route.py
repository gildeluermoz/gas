from flask import (
    redirect, url_for, render_template,
    Blueprint, request, flash
)

from sqlalchemy import exc

from app.pypnusershub import route as fnauth
from app.pypnusershub.db.tools import user_from_token

from app.env import db, URL_REDIRECT
from app.t_groups import forms as groupforms
from app.models import TGroups, TUsers
from config import config

route = Blueprint('group', __name__)


@route.route('groups/group', methods=['GET', 'POST'])
@fnauth.check_auth(2, False, URL_REDIRECT)
def groups():
    """
    Route qui affiche la liste des relais
    Retourne un template avec pour paramètres :
        - les droits de l'utilisateur selon son porfil --> user_right
        - une entête de tableau --> fLine
        - le nom des colonnes de la base --> line
        - le contenu du tableau --> table
        - le chemin de mise à jour --> pathU
        - le chemin de suppression --> pathD
        - le chemin d'ajout --> pathA
        - le chemin des membres du relais --> pathP
        - une clé (clé primaire dans la plupart des cas) --> key
        - un nom (nom de la table) pour le bouton ajout --> name
        - un nom de relais --> name_list
        - ajoute une colonne de bouton ('True' doit être de type string)--> otherCol
        - nom affiché sur le bouton --> Members
    """

    user_profil = user_from_token(request.cookies['token']).id_profil
    user_right = list()
    if user_profil >= 4:
        user_right = ['C','R','U','D']
    else:
        user_right = ['R']
    fLine = ['Actif', 'ID', 'Nom', 'Responsable', 'email', 'tel', 'Remarques']
    columns = ['active', 'id_group', 'group_name', 'group_leader', 'group_main_email', 'group_main_tel','group_comment']
    contents = TGroups.get_all(columns)
    return render_template(
        'table_database.html',
        user_right=user_right,
        fLine=fLine,
        line=columns,
        table=contents,
        key="id_group",
        pathI=config.URL_APPLICATION + '/group/info/',
        pathU=config.URL_APPLICATION + "/group/update/",
        pathD=config.URL_APPLICATION + "/group/delete/",
        pathA=config.URL_APPLICATION + '/group/add/new',
        pathP=config.URL_APPLICATION + '/group/members/',
        name="un relais",
        name_list="Relais",
        otherCol='True',
        Members="Membres",
        see='False'
    )


@route.route('group/add/new', defaults={'id_group': None}, methods=['GET', 'POST'])
@route.route('group/update/<id_group>', methods=['GET', 'POST'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def addorupdate(id_group):
    """
    Route affichant un formulaire vierge ou non (selon l'url) pour ajouter ou mettre à jour un relais
    L'envoie du formulaire permet l'ajout ou la maj du relais dans la base
    Retourne un template accompagné d'un formulaire pré-rempli ou non selon le paramètre id_group
    Une fois le formulaire validé on retourne une redirection vers la liste des relais
    """

    form = groupforms.Group()
    if id_group == None:
        if request.method == 'POST':
            if form.validate_on_submit() and form.validate():
                form_group = pops(form.data)
                form_group.pop('id_group')
                TGroups.post(form_group)
                return redirect(url_for('group.groups'))
        return render_template('group.html', form=form, title="Formulaire des relais")
    else:
        group = TGroups.get_one(id_group)
        if request.method == 'GET':
            form = process(form, group)
        if request.method == 'POST':
            if form.validate_on_submit() and form.validate():
                form_group = pops(form.data)
                form_group['id_group'] = group['id_group']
                TGroups.update(form_group)
                return redirect(url_for('group.groups'))
        return render_template('group.html', form=form, title="Formulaire Liste")


@route.route('group/members/<id_group>', methods=['GET', 'POST'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def membres(id_group):
    """
    Route retournant la liste des users appartenant au relais
    Avec pour paramètre un id de relais (id_group)
    """

    q = db.session.query(TUsers)
    q = q.order_by(TUsers.last_name)
    q = q.filter(TUsers.id_group == id_group) 
    tab = [data.as_dict() for data in q.all()]
    group = TGroups.get_one(id_group)
    return render_template(
        "info_relais.html",
        table=tab,
        group=group,
        name_list="Membres du relais"
    )
    


@route.route('group/delete/<id_group>', methods=['GET', 'POST'])
@fnauth.check_auth(4, False, URL_REDIRECT)
def delete(id_group):
    """
    Route qui supprime un relais dont l'id est donné en paramètres dans l'url
    Retourne une redirection vers la liste des relais
    """

    try:
        TGroups.delete(id_group)
        return redirect(url_for('group.groups'))
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


def process(form, group):
    """
    Methode qui rempli le formulaire par les données de l'éléments concerné
    Avec pour paramètres un formulaire et un relais
    """

    form.active.process_data(group['active'])
    form.group_name.process_data(group['group_name'])
    form.group_leader.process_data(group['group_leader'])
    form.group_comment.process_data(group['group_comment'])
    form.group_main_email.process_data(group['group_main_email'])
    form.group_main_tel.process_data(group['group_main_tel'])
    return form
