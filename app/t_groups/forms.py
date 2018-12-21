from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired


class Group(FlaskForm):
    """
    Classe du formulaire des relais
    """

    active = BooleanField('Actif', default = True, false_values=(False, 'false'))
    group_name = StringField("Nom du relais", validators = [DataRequired(message = 'Le nom du relais est obligatoire')])
    group_leader = StringField("Responsable du relais")
    group_main_email = StringField("Email principal")
    group_main_tel = StringField("Téléphone principal")
    group_comment = TextAreaField("Commentaire")
    id_group = HiddenField('Id')
    submit = SubmitField('Enregistrer')