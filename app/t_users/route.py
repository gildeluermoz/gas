from flask import (
    redirect, url_for, render_template,
    Blueprint, request, flash
)

from flask_bcrypt import (
    generate_password_hash
)

from app.pypnusershub import routes as fnauth

from app.env import URL_REDIRECT
from app.t_users import forms as t_usersforms
from app.models import TUsers, TGroups

from config import config


route = Blueprint('user', __name__)


@route.route('users/list', methods=['GET'])
@fnauth.check_auth(3, False, URL_REDIRECT)
def users():

    """
    Route qui affiche la liste des utilisateurs
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
    fLine = ['Actif', 'Id', 'Identifiant', 'Nom', 'Prenom', 'Email', 'Relais', 'Remarques']  # noqa
    columns = ['active', 'id_user', 'identifiant', 'last_name', 'first_name', 'email', 'group_name', 'user_comment']  # noqa
    contents = TUsers.get_all(columns)
    tab = []
    for data in contents:
        g = data
        g['group_name'] = data['group_rel']['group_name']
        tab.append(g)

    return render_template(
        "table_database.html",
        fLine=fLine,
        line=columns,
        table=tab,
        see="False",
        key="id_user",
        pathI=config.URL_APPLICATION + "/user/info/",
        pathU=config.URL_APPLICATION + "/user/update/",
        pathD=config.URL_APPLICATION + "/user/delete/",
        pathA=config.URL_APPLICATION + "/user/add/new",
        name="un utilisateur",
        name_list="Utilisateurs"
    )


@route.route('user/add/new', defaults={'id_user': None}, methods=['GET', 'POST'])
@route.route('user/update/<id_user>', methods=['GET', 'POST'])
@fnauth.check_auth(6, False, URL_REDIRECT)
def addorupdate(id_user):

    """
    Route affichant un formulaire vierge ou non (selon l'url) pour ajouter ou mettre à jour un utilisateurs
    L'envoie du formulaire permet l'ajout ou la mise à jour de l'utilisateur dans la base
    Retourne un template accompagné du formulaire pré-rempli ou non selon le paramètre id_user
    Une fois le formulaire validé on retourne une redirection vers la liste des users
    """
    form = t_usersforms.Utilisateur()
    form.id_group.choices = TGroups.selectActiveGroups()

    if id_user is not None:
        user = TUsers.get_one(id_user)
        if request.method == 'GET':
            form = process(form, user)

    if request.method == 'POST':
        if form.validate_on_submit() and form.validate():
            form_user = pops(form.data)
            form_user.pop('id_user')

            if form.pass_plus.data:
                try:
                    (
                        form_user['pass_plus']
                    ) = TUsers.set_password(
                        form.pass_plus.data, form.mdpconf.data
                    )
                except Exception as exp:
                    flash(str(exp))
                    return render_template(
                        'user.html', form=form, title="Formulaire Utilisateur"
                    )
            else:
                form_user.pop('pass_plus')

            if id_user is not None:
                form_user['id_user'] = user['id_user']
                TUsers.update(form_user)
            else:
                TUsers.post(form_user)
            return redirect(url_for('user.users'))

        else:
            errors = form.errors
            flash(errors)

    return render_template(
        'user.html', form=form, title="Formulaire Utilisateur"
    )


@route.route('user/delete/<id_user>', methods=['GET', 'POST'])
@fnauth.check_auth(6, False, URL_REDIRECT)
def deluser(id_user):
    """
    Route qui supprime un utilisateur dont l'id est donné en paramètres dans l'url
    Retourne une redirection vers la liste d'utilisateurs
    """
    TUsers.delete(id_user)
    return redirect(url_for('user.users'))


def pops(form):
    """
    Methode qui supprime les éléments indésirables du formulaires
    Avec pour paramètre un formulaire
    """
    form.pop('mdpconf')
    form.pop('submit')
    form.pop('csrf_token')
    return form


def process(form, user):
    """
    Methode qui rempli le formulaire par les données de l'éléments concerné
    Avec pour paramètres un formulaire et un user
    """

    form.active.process_data(user['active'])
    form.id_group.process_data(user['id_group'])
    form.last_name.process_data(user['last_name'])
    form.first_name.process_data(user['first_name'])
    form.email.process_data(user['email'])
    form.user_comment.process_data(user['user_comment'])
    form.identifiant.process_data(user['identifiant'])
    return form
