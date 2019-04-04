'''
    Définition du formulaire : création/modification d'une commande
'''
import inspect
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, HiddenField, SelectField, 
    IntegerField, validators, DecimalField
)
from wtforms.validators import DataRequired, InputRequired, NumberRange
from config import config


class Order(FlaskForm):
    id_group = SelectField(
        "Je choisi mon " + config.WORD_GROUP, 
        coerce=int, 
        choices=[], 
        validators=[DataRequired(message="Merci de choisir un " + config.WORD_GROUP)]
    )
    group_discount = DecimalField(
        "Remise " +config.WORD_GROUP + " en pourcentage (de -100 à 0)",
        default=0.0,
        validators=[
            InputRequired(message='La remise est obligatoire. Aucune = 0, Gratuité = -100.00'),
            NumberRange(min=-100, max=0, message="La valeur de la remise est négative et doit être comprise entre -100 et 0")
        ]
    )
    hidden_group_discount = HiddenField(default=0.0)
    submit = SubmitField('Enregistrer')

    @classmethod
    def append_nbcase(cls, name, label):
        setattr(cls, name, IntegerField(label, validators=[InputRequired(message='La quantité est obligatoire. Aucune = "0"')]))
        return cls

    @classmethod
    def clean_attr(cls):
        attributes = inspect.getmembers(cls, lambda a:not(inspect.isroutine(a)))
        for a in attributes:
            if a[0].startswith('nb'):
                delattr(cls, a[0])
        return cls

class OrderChoice(FlaskForm):
    id_delivery = SelectField(
        'Je choisi une livraison',
        coerce=str,
        choices=[],
        default=[],
        validators=[DataRequired(message="Merci de choisir une livraison.")]
    )
    id_group = SelectField(
        "Je choisi mon " + config.WORD_GROUP,
        coerce=int,
        choices=[],
        default=[],
        validators=[DataRequired(message="Merci de choisir un " + config.WORD_GROUP)]
    )
    submit = SubmitField("C'est parti")
