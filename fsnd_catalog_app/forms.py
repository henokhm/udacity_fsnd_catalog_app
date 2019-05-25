from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Required, ValidationError

from fsnd_catalog_app.models import Category
from fsnd_catalog_app.models import User


class SignupForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # Custom validation to prevent users from trying to user the same email or username
    # to sign up for two accounts
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("An account with that username already exists. Please choose"
                                  "a different name.")


class LoginForm(FlaskForm):
    email = StringField('',
                        validators=[DataRequired(), Email()])
    password = PasswordField('', validators=[DataRequired()])
    submit = SubmitField('Sign in')


class AddCategoryForm(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Add Category')


class EditCategoryForm(FlaskForm):
    category_name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Save Changes')


class DeleteCategoryForm(FlaskForm):
    submit = SubmitField('Delete')


class AddItemForm(FlaskForm):
    categories = Category.query.all()
    STATE_CHOICES = [(category.name, category.name) for category in categories]
    item_name = StringField('Item Name', validators=[DataRequired()])
    item_category = SelectField(label='Category', choices=STATE_CHOICES, validators=[Required()])
    item_details = StringField('Item Details', validators=[DataRequired()])
    submit = SubmitField('Add Item')


class EditItemForm(FlaskForm):
    categories = Category.query.all()
    STATE_CHOICES = [(category.name, category.name) for category in categories]
    item_name = StringField('Item Name', validators=[DataRequired()])
    item_category = SelectField(label='Category', choices=STATE_CHOICES, validators=[Required()])
    item_details = StringField('Item Details', validators=[DataRequired()])
    submit = SubmitField('Save Changes')


class DeleteItemForm(FlaskForm):
    submit = SubmitField('Delete')
