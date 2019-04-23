from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Required


class SignupForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
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
    Category_Name = StringField('Category Name', validators=[DataRequired()])
    submit = SubmitField('Save')


class AddItemForm(FlaskForm):
    category_choices = 10
    item_name = StringField('Item Name', validators=[DataRequired()])
    item_category = SelectField(u'Field name', choices = category_choices, validators = [Required()])
    item_details = StringField('Item Details', validators=[DataRequired()])
    submit = SubmitField('Save')


class EditItemForm(FlaskForm):
    category_choices = 10
    item_name = StringField('Item Name', validators=[DataRequired()])
    item_category = SelectField(u'Field name', choices = category_choices, validators = [Required()])
    item_details = StringField('Item Details', validators=[DataRequired()])
    submit = SubmitField('Save')