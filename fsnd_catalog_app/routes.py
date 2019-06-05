from flask import render_template, request, flash, url_for, redirect, g, jsonify, session
from fsnd_catalog_app import app, bcrypt
from fsnd_catalog_app.models import Category, Item, User
from fsnd_catalog_app.forms import (SignupForm, LoginForm, AddCategoryForm, EditCategoryForm,
                                    DeleteCategoryForm, AddItemForm, EditItemForm, DeleteItemForm)
from flask_login import login_user, current_user, logout_user, login_required

import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests



CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "CatalogApp"


@app.route("/")
@app.route("/catalog/all")
def catalog():
    """
    View function for home page.
    :return: Rendered template of home page.
    """
    all_categories = Category.query.order_by(Category.id.desc()).all()
    all_items = Item.query.order_by(Item.id.desc()).all()
    number_of_items = len(list(all_items))
    return render_template("home.html", categories=all_categories, items=all_items,
                            selected_category=None, number_of_items=number_of_items)


@app.route("/catalog/<int:selected_category_id>")
def catalog_category(selected_category_id):
    """
    View function for homepage with category selected.
    :param selected_category_id: Integer id identifying category in the database.
    :return: Rendered template of homepage showing items of only selected category.
    """
    all_categories = Category.query.order_by(Category.id.desc()).all()
    selected_category = Category.query.filter_by(id=selected_category_id).first()
    items_of_selected_category = Item.query.order_by(Item.id.desc()).filter_by(cat_id=selected_category.id)
    number_of_items = len(list(items_of_selected_category))
    return render_template("home.html", categories=all_categories, items=items_of_selected_category,
                           selected_category=selected_category, selected_category_id=selected_category_id,
                           number_of_items=number_of_items)


@app.route("/gconnect", methods=['POST'])
def gconnect():
    """
    Used to authenticate user via Google.
    :return: Redirect to home page.
    """
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={}'.format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    print(1)
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    print(3)
    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    print("access token: ", credentials.access_token)
    session['gplus_id'] = gplus_id

    print(4)
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    print(5)
    data = answer.json()
    if not User.query.filter_by(username=data['name']).first():
        # user is not in our database
        User.add_user(google_auth=True, username=data['name'], email=data['email'])
        flash('Your account has been created!')

    print(6)
    # login the user"
    user = User.query.filter_by(username=data['name']).first()
    print(7)
    login_user(user)
    print(8)
    flash('You have successfully logged in!')
    print(9)
    return redirect(url_for("catalog"))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """
    View to sign up user.
    :return: If form submitted, run logic to process sign up. If successful,
    redirects to home page. If form not submitted, returns rendered sign up form.
    """
    # a user already signed in shouldn't be able to get to this page, eg. they
    # manage to get the url somehow and paste it in the browser
    if current_user.is_authenticated:
        return redirect(url_for('catalog'))

    # state to use for Google sign in, if user opts
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state

    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # add user to database
        User.add_user(google_auth=False, username=form.username.data,
                      email=form.email.data, hashed_password=hashed_password)
        user = User.query.filter_by(username=form.username.data).first()
        # login the user
        login_user(user)
        flash('Welcome! Your account has been created.')
        return redirect(url_for("catalog"))
    return render_template("signup.html", form=form, STATE=session['state'])


@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    View function to log in user.
    :return: If form submitted, process login and if successful, redirect to homepage.
    If form not submitted or login logic fails, simply return rendered form.
    """
    # a user already signed in shouldn't be able to get to this page
    if current_user.is_authenticated:
        return redirect(url_for('catalog'))

    # State value for use with Google OAuth
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.hashed_password, form.password.data):
                # correct password provided
                login_user(user)
                flash('You have successfully logged in!')
                return redirect(url_for("catalog"))
            else:
                #wrong password
                flash("The password you provided is incorrect. Please try again.")
                return redirect(url_for("login"))
        else:
            # user not found in database
            flash("That username doesn't exist. Please sign up.")
            return redirect(url_for("signup"))
    return render_template("login.html", form=form, STATE=session['state'])


@app.route("/logout")
@login_required
def logout():
    # if user was authenticated using Google, first revoke token
    print(session)
    if current_user.google_auth:
        access_token = session.get('access_token')
        if access_token is None:
            response = make_response(json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        url = 'https://accounts.google.com/o/oauth2/revoke?token={}'.format(session['access_token'])
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        if result['status'] == '200':
            del session['access_token']
            del session['gplus_id']
            return redirect(url_for('logout'))
        else:
            response = make_response(json.dumps('Failed to revoke token for given user.', 400))
            response.headers['Content-Type'] = 'application/json'
            return response

    logout_user()
    flash("You have successfully logged out!")
    return redirect(url_for("catalog"))


# category CRUD
@app.route("/catalog_categories/add_category", methods=['GET', 'POST'])
@login_required
def add_category():
    """
    View function for add category page.
    :return: If form submitted and validated, add category and redirect to home page.
    Otherwise, return rendered add category form.
    """
    form = AddCategoryForm()
    if form.validate_on_submit():
        # add category to database
        # with creator of category set to current user
        Category.add_category(form.category_name.data, user_id=current_user.id)
        flash('You have successfully added "{}" category'.format(form.category_name.data))
        return redirect(url_for("catalog"))
    return render_template("add_category.html", form=form)


@app.route("/catalog_categories/<int:category_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    """
    View function of edit category form.
    :param category_id: Integer identifying the category being edited in our database
    :return: If form submitted and validation successful, save edited category and redirect to home page.
    Otherwise return rendered edit category form.
    """
    form = EditCategoryForm()
    category = Category.query.filter_by(id=category_id).first()
    if form.validate_on_submit():
        # If the category doesn't belong to the user, they shouldn't be able to edit it
        if category.creator == current_user:
            Category.edit_category(category, form.category_name.data)
            flash('You have successfully edited the "{}" category!'.format(category.name))
        else:
            flash("You cannot edit this category because you are not its creator.")
        return redirect(url_for('catalog'))
    return render_template("category_edit.html", form=form, category=category)


@app.route("/catalog_categories/<int:category_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    """
    View function to confirm delete category page.
    :param category_id: Integer identifying category to be deleted from database
    :return: If form submitted and authorization sufficient, delete category and
    redirect to home page. Otherwise, return rendered template.
    """
    form = DeleteCategoryForm()
    category = Category.query.filter_by(id=category_id).first()
    if form.validate_on_submit():
        # If user is not the creator of the category, they shouldn't be able to delete it
        if category.creator == current_user:
            Category.delete_category(category)
            flash('You have successfully deleted the "{}" category!'.format(category.name))
        else:
            flash("You cannot delete this category because you are not its creator.")
        return redirect(url_for('catalog'))
    return render_template("category_confirm_delete.html", form=form, category=category)


# items CRUD
@app.route("/catalog_items/add_item", methods=['GET', 'POST'])
@login_required
def add_item():
    """
    View function of add item form.
    :return: If form submitted and validation successful, add item to database and redirect
    to home page. Otherwise, return rendered template of add-item form.
    """
    form = AddItemForm()
    if form.validate_on_submit():
        category = Category.query.filter_by(name=form.item_category.data).first()
        # remember to store the user_id so that Edit and Delete operations can
        # confirm the creator of the item
        Item.add_item(name=form.item_name.data,
                      description=form.item_details.data,
                      category=category,
                      user_id=current_user.id)
        flash('You have successfully added the item "{}"'.format(form.item_name.data))
        return redirect(url_for('catalog'))
    return render_template("add_item.html", form=form)


@app.route("/catalog_items/<int:selected_item_id>")
def show_item_details(selected_item_id):
    """
    View function of show item details page.
    :param selected_item_id: Integer identifying selected item in database.
    :return:
    """
    selected_item = Item.query.filter_by(id=selected_item_id).first()
    return render_template("item_details.html", item=selected_item)


@app.route("/catalog_items/<int:selected_item_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_item(selected_item_id):
    """
    View function for edit item page
    :param selected_item_id: Integer identifying item to be edited in database.
    :return: If form submitted and form validation successful, save the changes made to the item
    in database and redirect to home page. Otherwise, return rendered item-edit page.
    """
    form = EditItemForm()
    selected_item = Item.query.filter_by(id=selected_item_id).first()
    if form.validate_on_submit():
        # only the user that created the item should be able to edit it
        if selected_item.user_id == current_user.id:
            category = Category.query.filter_by(name=form.item_category.data).first()
            Item.edit_item(item_to_edit=selected_item,
                           name=form.item_name.data,
                           description=form.item_details.data,
                           category=category)
            flash('You have successfully edited {} item'.format(form.item_name.data))
        else:
            flash('You cannot edit item "{}" because you didn\'t create it'.format(selected_item.name))
        return redirect(url_for("catalog"))
    return render_template("item_edit.html", form=form, item=selected_item)


@app.route("/catalog_items/<int:selected_item_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_item(selected_item_id):
    """
    View function to delete-item page.
    :param selected_item_id: Integer identifying the item to be deleted in database.
    :return: If form submitted and authorization sufficient, delete item, and redirect to homepage.
    """
    form = DeleteItemForm()
    selected_item = Item.query.filter_by(id=selected_item_id).first()
    if request.method == 'DELETE':
        if selected_item.user_id == current_user.id:
            Item.delete_item(selected_item)
            flash('You have successfully deleted the "{}" item!'.format(selected_item.name))
        else:
            flash('You cannot delete item "{}" because you didn\'t create it'.format(selected_item.name))
        return redirect(url_for('catalog'))
    return render_template("item_confirm_delete.html", form=form, item=selected_item)


@app.route("/catalog.json")
def full_catalog_json():
    """
    Function to get JSON representatio of full of catalog(that is, all categories and all items).
    :return: JSON representing full catalog.
    """
    all_categories = Category.query.order_by(Category.id.desc()).all()
    return jsonify("Full_Catalog",
                   [category.serialize for category in all_categories])


@app.route("/category/<int:category_id>.json")
def full_category_json(category_id):
    """
    Function to get JSON representation of selected category (including all items in it)
    :param category_id: Integer identifying category in database
    :return: JSON representing full category.
    """
    category = Category.query.filter_by(id=category_id).first()
    return jsonify("Category", category.serialize)


@app.route("/item/<int:item_id>.json")
def single_item_json(item_id):
    """
    Function to get JSON representation of an item.
    :param item_id: Integer identifying item in database.
    :return: JSON representing a single item.
    """
    item = Item.query.filter_by(id=item_id).first()
    return jsonify("Item", item.serialize)

