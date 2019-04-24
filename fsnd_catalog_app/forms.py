from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Required

from fsnd_catalog_app.models import Category
from fsnd_catalog_app import db


class SignupForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AddCategoryForm(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Save')


class EditCategoryForm(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Save')


class AddItemForm(FlaskForm):
    categories = Category.query.all()
    STATE_CHOICES = [(category.name, category.name) for category in categories]
    item_name = StringField('Item Name', validators=[DataRequired()])
    item_category = SelectField(label='Category', choices=STATE_CHOICES, validators=[Required()])
    item_details = StringField('Item Details', validators=[DataRequired()])
    submit = SubmitField('Save')


class EditItemForm(FlaskForm):
    categories = Category.query.all()
    STATE_CHOICES = [(category.name, category.name) for category in categories]
    item_name = StringField('Item Name', validators=[DataRequired()])
    item_category = SelectField(label='Category', choices=STATE_CHOICES, validators=[Required()])
    item_details = StringField('Item Details', validators=[DataRequired()])
    submit = SubmitField('Save')
