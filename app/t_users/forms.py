'''
    Définition du formulaire : création/modification d'un utilisateur
'''

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, HiddenField, SelectField,
    RadioField, BooleanField, TextAreaField, widgets,
    validators
)
from wtforms.validators import DataRequired, Email


class Utilisateur(FlaskForm):
    active = BooleanField('Actif', default = True, false_values=(False, 'false'))
    last_name = StringField('Nom', validators=[DataRequired()])
    first_name = StringField('Prenom')
    user_comment = TextAreaField('Commentaire')
    id_group = SelectField('Relais', coerce=int, choices=[], default=0)
    identifiant = StringField('Identifiant')
    pass_plus = PasswordField('Mot de passe')
    mdpconf = PasswordField('Confirmation')
    email = StringField('E-mail', validators=[validators.Optional(), Email()])
    id_user = HiddenField('id')
    submit = SubmitField('Enregistrer')



