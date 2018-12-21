'''
    Définition du formulaire : création/modification d'une commande
'''

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField, HiddenField, SelectField, 
    IntegerField, validators
)
from wtforms.validators import DataRequired

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
    # product_case_number = IntegerField(
    #     'Nombre de caisses', 
    #     validators=[DataRequired(message = 'Le nombre de caisse est obligatoire. Aucune = "0"')]
    # )
    
    # id_product = HiddenField('id')
    submit = SubmitField('Enregistrer')

    @classmethod
    def append_nbcase(cls, name, label):
        setattr(cls, name, IntegerField(label, validators=[DataRequired(message = 'Le nombre de caisse est obligatoire. Aucune = "0"')]))
        return cls


