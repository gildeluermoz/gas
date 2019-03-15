from flask_wtf import FlaskForm
from wtforms import StringField, DateField, DecimalField, BooleanField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, InputRequired, NumberRange


class Delivery(FlaskForm):

    """
    Classe du formulaire des livraisons
    """

    active = BooleanField('Actif', default=True, false_values=(False, 'false'))
    is_open = BooleanField('Commandes ouvertes', default=False, false_values=(False, 'false'))
    delivery_name = StringField('Nom de la livraison', validators=[DataRequired()])
    delivery_date = DateField('Date de livraison')
    order_limit_date = DateField('Date limite de commande')
    delivery_comment = StringField('Commentaire')
    delivery_organization = TextAreaField('Organisation de la livraison')
    delivery_discount = DecimalField(
        "Remise/frais global (remise = valeur négative, frais = valeur positive ; de -100% à +100%",
        default=0.0,
        validators=[
            InputRequired(message='Information obligatoire. Frais de 5% = 5.00 ; Aucune = 0 ; remise de 2% = -2.00 ; Gratuité = -100.00'),
            NumberRange(min=-100, max=100, message="La valeur doit être comprise entre -100 et +100")
        ]
    )
    id_delivery = HiddenField('id')
    submit = SubmitField('Enregistrer')
