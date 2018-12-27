'''
    Définition du formulaire : création/modification d'un utilisateur
'''

from flask_wtf import FlaskForm
from wtforms import (
    StringField, SubmitField, HiddenField, SelectField, DecimalField, 
    IntegerField, BooleanField, TextAreaField, validators
)
from wtforms.validators import DataRequired, Email


class Product(FlaskForm):
    active = BooleanField('Actif', default = True, false_values=(False, 'false'))
    product_name = StringField('Nom', validators=[DataRequired(message = 'Le nom du produit est obligatoire')])
    product_comment = TextAreaField('Commentaire')
    id_delivery = SelectField('Livraison', coerce=str, choices=[], default=0)
    buying_price = DecimalField("Prix d'achat")
    selling_price = DecimalField("Prix de vente")
    case_weight = IntegerField('Poids de la caisse')
    id_product = HiddenField('id')
    submit = SubmitField('Enregistrer')



