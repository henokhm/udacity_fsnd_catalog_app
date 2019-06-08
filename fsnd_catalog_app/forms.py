from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField,
                     SubmitField, TextAreaField, SelectField)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from fsnd_catalog_app.models import Category, User


def length(min=-1, max=-1):
    message = 'length of input must be between %d ' \
              'and %d characters long.' % (min, max)

    def _length(form, field):
        length = len(field.data)
        if length < min or max != -1 and length > max:
            raise ValidationError(message)

    return _length


class SignupForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(), length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     length(min=6, max=60)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField('Sign Up')

    # Custom validation to prevent users from trying to user
    # the same email or username to sign up for two accounts
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("An account with that username already "
                                  "exists. Please choose another username.")


class LoginForm(FlaskForm):
    email = StringField('',
                        validators=[DataRequired(), Email(), length(max=120)])
    password = PasswordField('', validators=[DataRequired(), length(max=60)])
    submit = SubmitField('Sign in')


class AddCategoryForm(FlaskForm):
    category_name = StringField('Category Name',
                                validators=[DataRequired(), length(max=80)])
    submit = SubmitField('Add Category')


class EditCategoryForm(FlaskForm):
    category_name = StringField('Category Name',
                                validators=[DataRequired(),
                                            length(min=2, max=80)])
    submit = SubmitField('Save Changes')


class DeleteCategoryForm(FlaskForm):
    submit = SubmitField('Delete')


class AddEditItemForm(FlaskForm):
    item_name = StringField('Item Name',
                            validators=[DataRequired(), length(max=80)])
    item_category = SelectField('Category', validators=[DataRequired()])
    item_details = TextAreaField('Item Details',
                                 validators=[DataRequired(),
                                             length(max=250)])

    def __init__(self):
        super(AddEditItemForm, self).__init__()
        self.item_category.choices = [(c.name, c.name)
                                      for c in Category.query.all()]


class AddItemForm(AddEditItemForm):
    submit = SubmitField('Add Item')


class EditItemForm(AddEditItemForm):
    submit = SubmitField('Save Changes')


class DeleteItemForm(FlaskForm):
    submit = SubmitField('Delete')
