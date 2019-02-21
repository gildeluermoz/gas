'''
    Définition du formulaire : création/modification d'une commande
'''

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, HiddenField, SelectField, 
    IntegerField, validators, DecimalField
)
from wtforms.validators import DataRequired, InputRequired, NumberRange
from config import config
# from app.env import db, URL_REDIRECT
# from app.models import TProducts

class Order(FlaskForm):
    id_group = SelectField(
        "Je choisi mon " + config.WORD_GROUP, 
        coerce=int, 
        choices=[], 
        default=0,
        validators=[DataRequired(message = "Merci de choisir un " + config.WORD_GROUP)]
    )
    group_discount = DecimalField(
        "Remise " +config.WORD_GROUP + " en pourcentage (de 0 à 100)",
        default=0.0,
        validators=[
            InputRequired(message = 'La remise est obligatoire. Aucune = "0", Gratuité = "100"'),
            NumberRange(min=0, max=100, message="La valeur de la remise doit être comprise entre 0 et 100")
        ]
    )
    hidden_group_discount = HiddenField(default=0.0)
    submit = SubmitField('Enregistrer')

    @classmethod
    def append_nbcase(cls, name, label):
        setattr(cls, name, IntegerField(label, validators=[InputRequired(message = 'La quantité est obligatoire. Aucune = "0"')]))
        return cls

class OrderChoice(FlaskForm):
    id_delivery = SelectField(
        'Je choisi une livraison', 
        coerce=str, 
        choices=[],
        default=[], 
        validators=[DataRequired(message = "Merci de choisir une livraison.")]
    )
    id_group = SelectField(
        "Je choisi mon " + config.WORD_GROUP, 
        coerce=int, 
        choices=[], 
        default=[],
        validators=[DataRequired(message = "Merci de choisir un " + config.WORD_GROUP)]
    )
    submit = SubmitField("C'est parti")
