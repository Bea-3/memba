from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField
from wtforms.validators import DataRequired,Email,Length,EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed

class ContactForm(FlaskForm):
    screenshot = FileField("upload screenshot", validators=[FileRequired(), FileAllowed(['jpg','png'],"Ensure you upload the right extension!")])
    email = StringField("Your Email: ",validators=[Email(message="Hello, your email should be valid"),DataRequired
    (message="we will get back to you")])
    confirm_email=StringField("Confirm Email:", validators=[EqualTo('email')])
    message = TextAreaField("Message",validators=[DataRequired(message="Cannot submit empty field"),Length(min=10)])
    submit=SubmitField("Send Message")