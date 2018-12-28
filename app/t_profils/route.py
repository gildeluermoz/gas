from flask import (
    redirect, url_for, render_template,
    Blueprint, request,  flash, jsonify
)

from sqlalchemy import exc

from app.pypnusershub import route as fnauth
from app.pypnusershub.db.tools import user_from_token

from app.env import URL_REDIRECT
from app.t_profils import forms as t_profilsforms
from app.models import (
    TProfils, TUsers, CorUserProfil
)
from config import config

route = Blueprint('profil', __name__)

"""
Routes des profils
"""


@route.route('profils/list', methods=['GET', 'POST'])
@fnauth.check_auth(6, False, URL_REDIRECT)
def profils():
    """
    Route qui affiche la liste des profils
    Retourne un template avec pour paramètres :
        - les droits de l'utilisateur selon son porfil --> user_right
        - une entête de tableau --> fLine
        - le nom des colonnes de la base --> line
        - le contenu du tableau --> table
        - le chemin de mise à jour --> pathU
        - le chemin de suppression --> pathD
        - le chemin d'ajout --> pathA
        - le chemin des roles du profil --> pathP
        - une clé (clé primaire dans la plupart des cas) --> key
        - un nom (nom de la table) pour le bouton ajout --> name
        - un nom de listes --> name_list
        - ajoute une colonne de bouton ('True' doit être de type string)--> otherCol
        - nom affiché sur le bouton --> Members
    """
    user_profil = user_from_token(request.cookies['token']).id_profil
    user_right = list()
    if user_profil == 6:
        user_right = ['C','R','U','D']
    else:
        user_right = ['R']
    fLine = ['Code', 'Nom', 'Description']
    columns = ['id_profil',  'profil_code', 'profil_name', 'profil_comment']
    tab = [data for data in TProfils.get_all()]
    return render_template(
        'table_database.html',
        user_right=user_right,
        fLine=fLine,
        line=columns,
        table=tab,
        key='id_profil',
        pathU=config.URL_APPLICATION + '/profil/update/',
        pathD=config.URL_APPLICATION + '/profil/delete/',
        pathA=config.URL_APPLICATION + '/profil/add/new',
        pathP=config.URL_APPLICATION + "/profil/users/",
        name="un profil",
        name_list="Profils",
        otherCol='True',
        Members="Utilisateurs"
     )


@route.route('profil/users/<id_profil>', methods=['GET', 'POST'])
@fnauth.check_auth(6, False, URL_REDIRECT)
def users(id_profil):
    """
    Route affichant la liste des users du profil et ceux dispobles.
    Avec pour paramètre un id de profil
    Retourne un template avec pour paramètres:
        - une entête des tableaux --> fLine
        - le nom des colonnes de la base --> data
        - liste des profils utilisables --> table
        - liste des profils non utilisables mais disponibles --> table2
    """
    users_in_profil = TUsers.get_users_in_profil(id_profil)
    users_out_profil = TUsers.get_users_out_profil(id_profil)
    header = ['ID', 'User']
    data = ['id_user', 'full_name']
    profil = TProfils.get_one(id_profil)
    if request.method == 'POST':
        data = request.get_json()
        new_users = data["tab_add"]
        delete_users = data["tab_del"]
        try:
            CorUserProfil.add_cor(new_users,id_profil)
            CorUserProfil.del_cor(delete_users,id_profil)
            return jsonify({"msg":"Enregistrement réussi"})
        except (exc.SQLAlchemyError, exc.DBAPIError) as e:
            return jsonify({"msg":"Quelque chose s'est mal passé :" + e})
    return render_template(
        'tobelong.html',
        fLine=header,
        data=data,
        table=users_out_profil,
        table2=users_in_profil,
        info='Utilisateurs ayant le profil  "' + profil['profil_name'] + '"'
    )


@route.route('profil/delete/<id_profil>', methods=['GET', 'POST'])
@fnauth.check_auth(6, False, URL_REDIRECT)
def delete(id_profil):
    """
    Route qui supprime un profil dont l'id est donné en paramètres dans l'url
    Retourne une redirection vers la liste de profil
    """

    try:
        TProfils.delete(id_profil)
        return redirect(url_for('profil.profils'))
    except (exc.SQLAlchemyError, exc.DBAPIError) as e:
        flash("Peut-être que tu essaies de faire quelque chose qui n'est pas cohérent.")
        flash(e)
        return render_template(
            'error.html', 
            title="Houps ! Une erreur s'est produite"
        )


@route.route('profil/add/new', defaults={'id_profil': None}, methods=['GET', 'POST'])
@route.route('profil/update/<id_profil>', methods=['GET', 'POST'])
@fnauth.check_auth(6, False, URL_REDIRECT)
def addorupdate(id_profil):
    """
    Route affichant un formulaire vierge ou non (selon l'url) pour ajouter ou mettre à jour un profil
    L'envoie du formulaire permet l'ajout ou la maj du profil dans la base
    Retourne un template accompagné d'un formulaire pré-rempli ou non selon le paramètre id_profil
    Une fois le formulaire validé on retourne une redirection vers la liste de profil
    """

    form = t_profilsforms.Profil()
    if id_profil == None:
        if request.method == 'POST':
            if form.validate() and form.validate_on_submit():
                form_profil = pops(form.data)
                form_profil.pop('id_profil')
                TProfils.post(form_profil)
                return redirect(url_for('profil.profils'))
        return render_template('profil.html', form=form, title="Formulaire Profil")
    else:
        profil = TProfils.get_one(id_profil)
        if request.method == 'GET':
            form = process(form, profil)
        if request.method == 'POST':
            if form.validate() and form.validate_on_submit():
                form_profil = pops(form.data)
                form_profil['id_profil'] = profil['id_profil']
                TProfils.update(form_profil)
                return redirect(url_for('profil.profils'))
        return render_template('profil.html', form=form, title="Formulaire Profil")


def pops(form):
    """
    Methode qui supprime les éléments indésirables du formulaires
    Avec pour paramètre un formulaire
    """

    form.pop('csrf_token')
    form.pop('submit')
    return form


def process(form, profil):
    """
    Methode qui rempli le formulaire par les données de l'éléments concerné
    Avec pour paramètres un formulaire et un profil
    """

    form.profil_name.process_data(profil['profil_name'])
    form.profil_code.process_data(profil['profil_code'])
    form.profil_comment.process_data(profil['profil_comment'])
    return form
