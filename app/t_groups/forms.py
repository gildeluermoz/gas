from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired
from config import config


class Group(FlaskForm):
    """
    Classe du formulaire des relais
    """

    active = BooleanField('Actif', default = True, false_values=(False, 'false'))
    group_name = StringField("Nom du " + config.WORD_GROUP, validators = [DataRequired(message = 'Le nom du ' + config.WORD_GROUP + ' est obligatoire')])
    group_leader = StringField("Responsable du " + config.WORD_GROUP)
    group_main_email = StringField("Email principal")
    group_main_tel = StringField("Téléphone principal")
    group_comment = TextAreaField("Commentaire")
    id_group = HiddenField('Id')
    submit = SubmitField('Enregistrer')