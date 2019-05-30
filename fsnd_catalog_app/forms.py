from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Required, ValidationError

from fsnd_catalog_app.models import Category, User


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
                                  "a different username.")


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


class AddEditItemForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    item_category = SelectField('Category', validators=[DataRequired()])
    item_details = TextAreaField('Item Details', validators=[DataRequired()])

    def __init__(self):
        super(AddEditItemForm, self).__init__()
        self.item_category.choices = [(c.name, c.name) for c in Category.query.all()]


class AddItemForm(AddEditItemForm):
    submit = SubmitField('Add Item')


class EditItemForm(AddEditItemForm):
    submit = SubmitField('Save Changes')


class DeleteItemForm(FlaskForm):
    submit = SubmitField('Delete')
