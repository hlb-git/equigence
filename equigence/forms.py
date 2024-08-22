from flask_wtf import FlaskForm
from equigence import state_dropdown, db
from equigence.models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class Register(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        existingEmail = db.db.user.find_one({"email": email.data})
        if existingEmail:
            raise ValidationError('Email already exists!')


class Login(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class New(FlaskForm):
    symbol = StringField('Symbol')
    singleSearchQtr = SelectField('Number of Quarters (Max 8)', choices=[(1, '1'), (2, '2'), 
                                                                         (3, '3'), (4, '4'), 
                                                                         (5, '5'), (6, '6'),
                                                                         (7, '7'), (8, '8')],
                                    validators=[DataRequired()])
    metric = SelectField('Analysis Metric', choices=[('NPM', 'Net Profit Margin (N/M)'),
                                                       ('PTE', 'Price to Earnings (P/E)')],
                                                       validators=[DataRequired()])
    compare = BooleanField('Compare Equities?')
    compareStock = StringField('Equities to Compare (e.g AAPL, MSF, TSLA)')
    compareMetric = SelectField('Comparison Metric', choices=[('NPM', 'Net Profit Margin (N/M)'),
                                                       ('PTE', 'Price to Earnings (P/E)')],
                                validators=[DataRequired()])
    compareSearchQtr = SelectField('Number of Quarters (Max 5)', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
                                    validators=[DataRequired()])
    submit = SubmitField('Analyse')

class Filter(FlaskForm):
    state = SelectField('State', choices=state_dropdown)
    city = StringField('City/ Town', render_kw={"placeholder": "Enter City"})
    type = SelectField('Rent Type', choices=[('', '(Select Rent Type)'),
                                              ('Single Room', 'Single Room'),
                                              ('Self Contain', 'Self Contain'),
                                              ('Flat', 'Flat'),
                                              ('Duplex', 'Duplex')])
    submit = SubmitField('Filter')

