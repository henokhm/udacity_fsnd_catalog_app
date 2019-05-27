from flask import render_template, request, flash, url_for, redirect, g, jsonify
from fsnd_catalog_app import app, bcrypt
from fsnd_catalog_app.models import Category, Item, User
from fsnd_catalog_app.forms import (SignupForm, LoginForm, AddCategoryForm, EditCategoryForm,
                                    DeleteCategoryForm, AddItemForm, EditItemForm, DeleteItemForm)
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/catalog/all")
def catalog():
    all_categories = Category.query.order_by(Category.id.desc()).all()
    all_items = Item.query.order_by(Item.id.desc()).all()
    return render_template("home.html", categories=all_categories, items=all_items,
                            selected_category=None)


@app.route("/catalog/<int:selected_category_id>")
def catalog_category(selected_category_id):
    all_categories = Category.query.all()
    selected_category = Category.query.filter_by(id=selected_category_id).first()
    items_of_selected_category = Item.query.order_by(Item.id.desc()).filter_by(cat_id=selected_category.id)
    return render_template("home.html", categories=all_categories, items=items_of_selected_category,
                           selected_category=selected_category, selected_category_id=selected_category_id)


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
    if request.method == 'POST':
        if category.creator == current_user:  # make sure category belongs to current user
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
                      creator=current_user)
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
    items_category = Category.query.filter_by(id=selected_item.id).first()
    if form.validate_on_submit():
        if selected_item.user_id == current_user.id:
            # save changes to db
            Item.edit_item(item_to_edit=selected_item,
                           name=form.item_name.data,
                           description=form.item_details.data,
                           cat_id=form.item_category.data,
                           user_id=current_user.id)
            flash('You have successfully edited {} item'.format(form.item_name.data))
        else:
            flash('You cannot edit item "{}" because you didn\'t create it'.format(selected_item.name))
        return redirect(url_for("catalog"))
    return render_template("item_edit.html", form=form, item=selected_item, items_category=items_category)


@app.route("/catalog_items/<int:selected_item_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_item(selected_item_id):
    form = DeleteItemForm()
    selected_item = Item.query.filter_by(id=selected_item_id).first()
    if request.method == 'POST':
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

