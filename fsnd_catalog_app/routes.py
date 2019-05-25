from flask import render_template, request, flash, url_for, redirect, g
from fsnd_catalog_app import app, bcrypt
from fsnd_catalog_app.models import Category, Item, User
from fsnd_catalog_app.forms import (SignupForm, LoginForm, AddCategoryForm, EditCategoryForm,
                                    DeleteCategoryForm, AddItemForm, EditItemForm, DeleteItemForm)
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/catalog")
def catalog():
    all_categories = Category.query.all()
    all_items = Item.query.all()
    # show edit, delete buttons only if user logged in
    # TODO
    return render_template("home.html", categories=all_categories, items=all_items)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # a user already signed in shouldn't be able to get to this page
    if current_user.is_authenticated:
        return redirect(url_for('catalog'))

    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # add user to database
        User.add_user(username=form.username.data, email=form.email.data, hashed_password=hashed_password)
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

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.all().filter_by(username=form.username.data).first()
        if user: # user exists in database
            if bcrypt.check_password_hash(user.password, form.password.data): # correct password provided
                # login user
                login_user(user)
                flash('You have successfully logged in!')
                return redirect(url_for("catalog"))
            else: #wrong password
                flash("The password you provided is incorrect. Please try again.")
                return redirect(url_for("login"))
        else:
            flash("That username doesn't exist. Please sign up.")
            return redirect(url_for("signup.html"))
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
        Category.add_category(form.category_name.data, creator=current_user)
        flash('You have successfully added "{}" category'.format(form.category_name.data))
        return redirect(url_for("catalog"))
    return render_template("add_category.html", form=form)


@app.route("/catalog_categories/<string:category_name>/edit", methods=['GET', 'POST'])
@login_required
def edit_category(category_name):
    form = EditCategoryForm()
    category = Category.query.filter_by(name=category_name).first()
    if form.validate_on_submit():
        if category.creator == current_user: # make sure category belongs to current user
            Category.edit_category(category, form.category_name.data)
            flash('You have successfully edited the "{}" category!'.format(category.name))
        else:
            flash("You cannot edit this category because you are not its creator.")
        return redirect(url_for('catalog'))
    return render_template("category_edit.html", form=form, current_category=category_name)


@app.route("/catalog_categories/<string:category_name>/delete", methods=['GET', 'POST'])
@login_required
def delete_category(category_name):
    form = DeleteCategoryForm()
    category = Category.query.filter_by(name=category_name).first()
    if request.method == 'POST':
        if category.creator == current_user:  # make sure category belongs to current user
            Category.delete_category(category)
            flash('You have successfully deleted the "{}" category!'.format(category_name))
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
        # set owner of item to current user
        # add item to database
        Item.add_item(name=form.item_name.data,
                      description=form.item_details.data,
                      category=form.item_category.data,
                      creator=current_user)
        flash('You have successfully added the item "{}"'.format(form.item_name.data))
        return redirect(url_for('catalog'))
    return render_template("add_item.html", form=form)


@app.route("/catalog_items/<string:item_name>")
@login_required
def show_item_details(item):
    return render_template("item_details.html", item=item)


@app.route("/catalog_items/<string:item_name>/edit", methods=['GET', 'POST'])
@login_required
def edit_item(item_name):
    form = EditItemForm()
    item = Item.query.filter_by(item_name=item_name)
    if form.validate_on_submit():
        if item.user_id == current_user.id:
            # save changes to db
            Item.edit_item(item_to_edit=item,
                           name=form.item_name.data,
                           description=form.item_details.data,
                           cat_id=form.item_category.data,
                           user_id=current_user.id)
            flash('You have successfully edited {} item'.format(form.item_name.data))
        else:
            flash('You cannot edit item "{}" because you didn\'t create it'.format(item.name))
        return redirect(url_for("catalog"))
    return render_template("item_edit.html", form=form, current_item=item_name)


@app.route("/catalog_items/<string:item_name>/delete", methods=['GET', 'POST'])
@login_required
def delete_item(item_name):
    form = DeleteItemForm()
    item = Item.query.filter_by(item_name=item_name)
    if request.method == 'POST':
        if item.user_id == current_user.id:
            Item.delete_item(item)
            flash('You have successfully deleted the "{}" item!'.format(item_name))
        else:
            flash('You cannot delete item "{}" because you didn\'t create it'.format(item.name))
        return redirect(url_for('catalog'))
    return render_template("item_confirm_delete.html", form=form, item=item)


@app.route("/catalog.json")
def full_catalog_json():
    return "Full catalog JSON"


@app.route("/category/<string:category_name>.json")
def full_category_json(category_name):
    return "Full Category JSON"


@app.route("/item/<string:item_name>.json")
def single_item_json(item_name):
    return "Single Item JSON"

