from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class ProductoForm(FlaskForm):

    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(),
            Length(min=3, max=50)
        ]
    )

    descripcion = StringField(
        "Descripción",
        validators=[
            DataRequired(),
            Length(min=5, max=100)
        ]
    )

    precio = DecimalField(
        "Precio",
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ]
    )

    stock = IntegerField(
        "Stock",
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ]
    )

    enviar = SubmitField("Guardar")