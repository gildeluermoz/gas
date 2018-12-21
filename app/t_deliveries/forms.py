from flask_wtf import FlaskForm
from wtforms import StringField, DateField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired 





class Delivery(FlaskForm):

    """
    Classe du formulaire des livraisons
    """
        
    active = BooleanField('Actif', default = True, false_values=(False, 'false'))
    delivery_name = StringField('Nom de la livraison', validators=[DataRequired()])
    delivery_date = DateField('Date de livraison', format='%d/%m/%Y')
    delivery_comment = StringField('Commentaire')
    id_delivery = HiddenField('id')
    submit = SubmitField('Enregistrer')