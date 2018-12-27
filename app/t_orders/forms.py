'''
    Définition du formulaire : création/modification d'une commande
'''

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, HiddenField, SelectField, 
    IntegerField, validators
)
from wtforms.validators import DataRequired, InputRequired

# from app.env import db, URL_REDIRECT
# from app.models import TProducts

class Order(FlaskForm):
    id_group = SelectField(
        'Je choisi mon relais', 
        coerce=int, 
        choices=[], 
        default=0,
        validators=[DataRequired(message = "Merci de choisir un relais.")]
    )
    submit = SubmitField('Enregistrer')

    @classmethod
    def append_nbcase(cls, name, label):
        setattr(cls, name, IntegerField(label, validators=[InputRequired(message = 'Le nombre de caisse est obligatoire. Aucune = "0"')]))
        return cls

class OrderChoice(FlaskForm):
    id_delivery = SelectField(
        'Je choisi une livraison', 
        coerce=int, 
        choices=[],
        default=0, 
        validators=[DataRequired(message = "Merci de choisir une livraison.")]
    )
    id_group = SelectField(
        'Je choisi mon relais', 
        coerce=int, 
        choices=[], 
        default=0,
        validators=[DataRequired(message = "Merci de choisir un relais.")]
    )
    submit = SubmitField("C'est parti")

