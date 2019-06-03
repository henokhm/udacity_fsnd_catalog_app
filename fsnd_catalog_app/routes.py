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
    all_categories = Category.query.order_by(Category.id.desc()).all()
    all_items = Item.query.order_by(Item.id.desc()).all()
    number_of_items = len(list(all_items))
    return render_template("home.html", categories=all_categories, items=all_items,
                            selected_category=None, number_of_items=number_of_items)


@app.route("/catalog/<int:selected_category_id>")
def catalog_category(selected_category_id):
    all_categories = Category.query.order_by(Category.id.desc()).all()
    selected_category = Category.query.filter_by(id=selected_category_id).first()
    items_of_selected_category = Item.query.order_by(Item.id.desc()).filter_by(cat_id=selected_category.id)
    number_of_items = len(list(items_of_selected_category))
    return render_template("home.html", categories=all_categories, items=items_of_selected_category,
                           selected_category=selected_category, selected_category_id=selected_category_id,
                           number_of_items=number_of_items)


@app.route("/gconnect", methods=['POST'])
def gconnect():
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
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
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

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['access_token'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    if not User.query.filter_by(name=data['name']).first():
        # user is not in our database
        User.add_user(google_auth=True, username=data['name'], email=data['email'])
        flash('Your account has been created!')

    # login the user
    user = User.query.filter_by(name=data['name']).first()
    login(user)
    flash('You have successfully logged in!')
    return redirect(url_for("catalog"))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # a user already signed in shouldn't be able to get to this page
    if current_user.is_authenticated:
        return redirect(url_for('catalog'))

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
    return render_template("signup.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    # a user already signed in shouldn't be able to get to this page
    if current_user.is_authenticated:
        return redirect(url_for('catalog'))

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    session['state'] = state

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.hashed_password, form.password.data): # correct password provided
                login_user(user)
                flash('You have successfully logged in!')
                return redirect(url_for("catalog"))
            else: #wrong password
                flash("The password you provided is incorrect. Please try again.")
                return redirect(url_for("login"))
        else:
            flash("That username doesn't exist. Please sign up.")
            return redirect(url_for("signup"))
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out!")
    return redirect(url_for("catalog"))


# category CRUD
@app.route("/catalog_categories/add_category", methods=['GET', 'POST'])
@login_required
def add_category():
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
    form = EditCategoryForm()
    category = Category.query.filter_by(id=category_id).first()
    if form.validate_on_submit():
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
    form = DeleteCategoryForm()
    category = Category.query.filter_by(id=category_id).first()
    if form.validate_on_submit():
        print('form validated')
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
    form = AddItemForm()
    if form.validate_on_submit():
        category = Category.query.filter_by(name=form.item_category.data).first()
        Item.add_item(name=form.item_name.data,
                      description=form.item_details.data,
                      category=category,
                      user_id=current_user.id)
        flash('You have successfully added the item "{}"'.format(form.item_name.data))
        return redirect(url_for('catalog'))
    return render_template("add_item.html", form=form)


@app.route("/catalog_items/<string:selected_item_id>")
@login_required
def show_item_details(selected_item_id):
    selected_item = Item.query.filter_by(id=selected_item_id).first()
    return render_template("item_details.html", item=selected_item)


@app.route("/catalog_items/<int:selected_item_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_item(selected_item_id):
    form = EditItemForm()
    selected_item = Item.query.filter_by(id=selected_item_id).first()
    if form.validate_on_submit():
        if selected_item.user_id == current_user.id:
            Item.edit_item(item_to_edit=selected_item,
                           name=form.item_name.data,
                           description=form.item_details.data,
                           cat_id=form.item_category.data)
            flash('You have successfully edited {} item'.format(form.item_name.data))
        else:
            flash('You cannot edit item "{}" because you didn\'t create it'.format(selected_item.name))
        return redirect(url_for("catalog"))
    return render_template("item_edit.html", form=form, item=selected_item)


@app.route("/catalog_items/<int:selected_item_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_item(selected_item_id):
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
    all_categories = Category.query.order_by(Category.id.desc()).all()
    return jsonify("Full_Catalog",
                   [category.serialize for category in all_categories])


@app.route("/category/<int:category_id>.json")
def full_category_json(category_id):
    category = Category.query.filter_by(id=category_id).first()
    return jsonify("Category", category.serialize)


@app.route("/item/<int:item_id>.json")
def single_item_json(item_id):
    item = Item.query.filter_by(id=item_id).first()
    return jsonify("Item", item.serialize)

