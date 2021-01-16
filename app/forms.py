from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired

class RegIDForm(FlaskForm):
    level = RadioField("Level", choices=["P6", "S3", "S6"])
    regid = StringField("Registration ID")
    who   = RadioField("Results for", choices=["Me", "Class"])
    submit= SubmitField("")
