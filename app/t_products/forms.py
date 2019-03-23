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
    active = BooleanField("Actif", default = True, false_values=(False, 'false'))
    product_name = StringField("Nom", validators=[DataRequired(message = 'Le nom du produit est obligatoire')])
    product_unit = StringField("Unité (ex: caisse, bidon, carton...)", validators=[DataRequired(message = "L'unité de vente du produit est obligatoire (ex: caisse, bidon, carton...)")])
    product_comment = TextAreaField("Commentaire")
    id_delivery = SelectField("Choisir la livraison pour ce produit", coerce=str, choices=[], default=[])
    buying_price = DecimalField("Prix d'achat")
    selling_price = DecimalField("Prix de vente")
    case_weight = DecimalField("Poids de l'unité")
    id_product = HiddenField("id")
    submit = SubmitField("Enregistrer")



