from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, DecimalField, RadioField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from dbms import DB


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        db = DB('site.db')
        if db.is_email(email.data):
            raise ValidationError('That email is taken. Please choose a different one.')

    def validate_username(self, username):
        db = DB('site.db')
        if db.is_username(username.data):
            raise ValidationError('That username is taken. Please choose a different one.')


class LoginForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    password = PasswordField('Password', validators=[DataRequired()])

    remember = BooleanField('Remember Me')

    submit = SubmitField('Log In')


class AccountForm(FlaskForm):

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])

    submit = SubmitField('Submit')


class PostForm(FlaskForm):

    title = StringField('Title', validators=[DataRequired()])

    content = StringField('Content', validators=[DataRequired()])

    submit = SubmitField('Post')


class ResetForm1(FlaskForm):

    username = StringField('Username', validators=[DataRequired()])

    submit = StringField('Request Code')

    code = StringField('Enter the Code sent to your Email address', validators=[DataRequired()])

    def validate_username(self, username):
        db = DB('site.db')
        if db.is_username(username.data):
            raise ValidationError('There is no account with that Username.')


class ResetForm2(FlaskForm):

    password = PasswordField('Password', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Reset')


class BuyorSellForm(FlaskForm):

    buyorsell = SelectField('What are you interested in?', choices=[('buying', 'Buying'), ('selling', 'Selling')],
                            validators=[DataRequired()])

    submit = SubmitField('Go')


class SellForm(FlaskForm):

    name = StringField('Name', validators=[DataRequired()])

    image = FileField('Upload Picture of the Crop', validators=[FileAllowed(['jpg', 'png', 'jpeg']), FileRequired('File was empty!')])

    price = DecimalField('Price', validators=[DataRequired()])

    units = RadioField('Units', choices=['per Ton', 'per Quintal', 'per Kilogram', 'per Gram'],
                       validators=[DataRequired()])

    info = TextAreaField('Information', validators=[DataRequired(), Length(min=2, max=200)])

    location = StringField('Location', validators=[DataRequired()])

    verified = BooleanField('AgriHero Verified')

    negotiable = BooleanField('Negotiable Price')

    submit = SubmitField('List to Sell')





