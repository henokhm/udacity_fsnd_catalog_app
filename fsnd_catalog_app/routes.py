from flask import render_template, request, flash, url_for, redirect, g
from fsnd_catalog_app import app, bcrypt
from fsnd_catalog_app.models import Category, Item, User
from fsnd_catalog_app.forms import (SignupForm, LoginForm, AddCategoryForm, EditCategoryForm,
                   AddItemForm, EditItemForm)


@app.route("/")
@app.route("/catalog")
def catalog():
    all_categories = Category.query.all()
    all_items = Item.query.all()
    # show edit, delete buttons only if user logged in
    # TODO
    return render_template("home.html", categories=all_categories, items=all_items)


# only if not already signed in
# TODO
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # add user to database
        User.add_user(username=form.username.data, email=form.email.data, hashed_password=hashed_password)
        # login the user
        # TODO
        flash('Your account has been created!')
        return redirect(url_for("catalog"))
    return render_template("signup.html", form=form)


# only if not already signed in
# TODO
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.all().filter_by(username=form.username.data).first()
        if user: # user exists in database
            if bcrypt.check_password_hash(user.password, form.password.data): # correct password provided

                # login user
                # TODO
                flash('You have successfully logged in!')
                return redirect(url_for("catalog"))
            else: #wrong password
                flash("The password you provided is incorrect!")
                return redirect(url_for("login"))
        else:
            flash("That username doesn't exist. Please sign up")
            return redirect(url_for("signup.html"))
    return render_template("login.html", form=form)


# login required
# TODO
@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        # log user out
        # TODO
        flash("You have successfully logged out!")
        return redirect(url_for("catalog"))
    return render_template("confirm_logout.html")


# category CRUD
# login required
# TODO
@app.route("/catalog_categories/add_category", methods=['GET', 'POST'])
def add_category():
    form = AddCategoryForm()
    if form.validate_on_submit():
        # add category to database
        # with creator of category set to current user
        Category.add_category(form.category_name.data, creator=g.current_user)
        flash('You have successfully added "{}" category'.format(form.category_name.data))
        return redirect(url_for("catalog"))
    return render_template("add_category.html", form=form)


# login required
# TODO
@app.route("/catalog_categories/<string:category_name>/edit", methods=['GET', 'POST'])
def edit_category(category_name):
    form = EditCategoryForm()
    category = Category.qurey.filter_by(name=category_name).first()
    if form.validate_on_submit():
        if category.creator == g.current_user: # make sure category belongs to current user
            Category.edit_category(category, form.category_name.data)
            flash('You have successfully edited the "{}" category!'.format(category.name))
        else:
            flash("You cannot edit this category because you are not its creator.")
        return redirect(url_for('catalog'))
    return render_template("category_edit.html", form=form, current_category=category_name)


# login required
# TODO
@app.route("/catalog_categories/<string:category_name>/delete", methods=['GET', 'POST'])
def delete_category(category_name):
    category = Category.qurey.filter_by(name=category_name).first()
    if request.method == 'POST':
        if category.creator == g.current_user:  # make sure category belongs to current user
            Category.delete_category(category)
            flash('You have successfully deleted the "{}" category!'.format(category_name))
        else:
            flash("You cannot delete this category because you are not its creator.")
        return redirect(url_for('catalog'))
    return render_template("category_confirm_delete.html", category_name=category_name)


# items CRUD
# login required
# TODO
@app.route("/catalog_items/add_item", methods=['GET', 'POST'])
def add_item():
    form = AddItemForm()
    if form.validate_on_submit():
        # set owner of item to current user
        # add item to database
        Item.add_item(name=form.item_name.data,
                      description=form.item_details.data,
                      category=form.item_category.data,
                      creator=g.current_user.id)
        flash('You have succussfully added the item "{}"'.format(form.item_name.data))
        return redirect(url_for('catalog'))
    return render_template("add_item.html", form=form)


@app.route("/catalog_items/<string:item_name>")
def show_item_details(item_name):
    # show edit, delete buttons only if user logged in
    # and owns item
    # TODO
    item = Item.query.filter_by(item_name=item_name)
    return render_template("item_details.html", item=item)


# login required
# TODO
@app.route("/catalog_items/<string:item_name>/edit", methods=['GET', 'POST'])
def edit_item_details(item_name):
    form = EditItemForm()
    item = Item.query.filter_by(item_name=item_name)
    if form.validate_on_submit():
        if item.user_id == g.current_user.id:
            # save changes to db
            Item.edit_item(item_to_edit=item,
                           name=form.item_name.data,
                           description=form.item_details.data,
                           cat_id=form.item_category.data,
                           user_id=g.current_user.id)
            flash('You have successfully edited *** item'.format())
        else:
            flash('You cannot edit item "{}" because you didn\'t create it'.format(item.name))
        return redirect(url_for("catalog"))
    return render_template("item_edit.html", form=form, current_item=item_name)


# login required
# item has to belong to current user
@app.route("/catalog_items/<string:item_name>/delete", methods=['GET', 'POST'])
def delete_item_details(item_name):
    if request.method == 'POST':
        item = Item.query.filter_by(item_name=item_name)
        if item.user_id == g.current_user.id:
            Item.delete_item(item)
            flash('You have successfully deleted the "{}" item!'.format(item_name))
        else:
            flash('You cannot delete item "{}" because you didn\'t create it'.format(item.name))
        return redirect(url_for('catalog'))
    return render_template("item_confirm_delete.html")


@app.route("/catalog.json")
def full_catalog_json():
    return "Full catalog JSON"


@app.route("/category/<string:category_name>.json")
def full_category_json(category_name):
    return "Full Category JSON"


@app.route("/item/<string:item_name>.json")
def single_item_json(item_name):
    return "Single Item JSON"

