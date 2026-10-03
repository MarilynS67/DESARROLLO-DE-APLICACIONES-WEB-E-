from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class FacturacionForm(FlaskForm):
    cliente = StringField(
        'Cliente',
        validators=[
            DataRequired(message='El cliente es obligatorio.')
        ]
    )

    producto = StringField(
        'Producto',
        validators=[
            DataRequired(message='El producto es obligatorio.')
        ]
    )

    cantidad = DecimalField(
        'Cantidad',
        validators=[
            DataRequired(message='La cantidad es obligatoria.'),
            NumberRange(min=1, message='La cantidad debe ser mayor o igual a 1.')
        ]
    )

    precio = DecimalField(
        'Precio',
        validators=[
            DataRequired(message='El precio es obligatorio.'),
            NumberRange(min=0, message='El precio no puede ser negativo.')
        ]
    )

    submit = SubmitField('Guardar factura')