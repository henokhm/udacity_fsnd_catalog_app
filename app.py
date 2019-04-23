from flask import Flask, render_template, request, flash, url_for, redirect
from forms import (SignupForm, LoginForm, AddCategoryForm, EditCategoryForm,
                   AddItemForm, EditItemForm)
app = Flask(__name__)
app.config['SECRET_KEY'] = '6@kr$IhQ%teki}Juetg*x]U/QmKz{P<g'


mock_categories = ['Soccer', 'Baseball', 'Swimming']
mock_items = [
    {
        'name': 'Soccer Cleats',
        'category_id': 0,
        'description': 'Soccer Cleats description...'
    },
    {
        'name': 'Soccer Ball',
        'category_id': 0,
        'description': 'Soccer Ball description...'
    },
    {
        'name': 'Baseball Bat',
        'category_id': 1,
        'description': 'Baseball Bat description...'
    },
    {
        'name': 'Baseball Gloves',
        'category_id': 1,
        'description': 'Baseball Gloves description...'
    },
    {
        'name': 'Swim Suit',
        'category_id': 2,
        'description': 'Swim Suit description ...'
    },
    {
        'name': 'Swimming Goggles',
        'category_id': 2,
        'description': 'Swimming Goggles description...'
    },
]


@app.route("/")
@app.route("/catalog")
def catalog():
    # show edit, delete buttons only if user logged in
    return render_template("home.html", categories=mock_categories, items=mock_items)


# only if not already signed in
@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        # validate form, username not used
        # add user to database
        # login the user
        flash('Your account has been created!')
        return redirect(url_for("catalog"))
    return render_template("signup.html", form=form)


# only if not already signed in
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        # validate username password combination
        # login user
        flash('You have successfully logged in!')
        return redirect(url_for("catalog"))
    return render_template("login.html", form=form)


# login required
@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        # log user out
        flash("You have successfully logged out!")
        return redirect(url_for("catalog"))
    return render_template("confirm_logout.html")


# category CRUD
# login required
@app.route("/catalog_categories/add_category", methods=['GET', 'POST'])
def add_category():
    form = AddCategoryForm()
    if request.method == "POST":
        # validate form
        # set owner of category to current user
        # add category to database
        flash('You have successfully added *** category')
        return redirect(url_for("catalog"))
    return render_template("add_category.html", form=form)


@app.route("/catalog_categories/<string:category_name>/items")
def show_category(category_name):
    # show edit, delete buttons only if user logged in
    # and owns category
    return render_template("category_items.html")


# login required
# category has to belong to current user
@app.route("/catalog_categories/<string:category_name>/edit", methods=['GET', 'POST'])
def edit_category(category_name):
    form = EditCategoryForm()
    if request.method == 'POST':
        # validate form
        # make sure category belongs to current user
        # get category from db
        # save changes
        flash ('You have successfully edited *** category')
        return redirect(url_for("catalog"))
    return render_template("category_edit.html", form=form, current_category=category_name)


# login required
# category has to belong to current user
@app.route("/catalog_categories/<string:category_name>/delete", methods=['GET', 'POST'])
def delete_category(category_name):
    if request.method == 'POST':
        # get category from db
        # make sure category belongs to current user
        # capture category name
        # delete category from db
        flash('You have successfully deleted the "***" category!'.format())
        return redirect(url_for('catalog'))

    return render_template("category_confirm_delete.html", category_name=category_name)


# items CRUD
# login required
@app.route("/catalog_items/add_item", methods = ['GET', 'POST'])
def add_item():
    form = AddItemForm()
    if request.method == 'POST':
        # validate  form
        # set owner of item to current user
        # add item to database
        flash('You have succussfully added the item ***'.format())
        return redirect(url_for('catalog'))
    return render_template("add_item.html", form=form)


@app.route("/catalog_items/<string:item_name>")
def show_item_details(item_name):
    # show edit, delete buttons only if user logged in
    # and owns item
    return render_template("item_details.html")


# login required
# item has to belong to current user
@app.route("/catalog_items/<string:item_name>/edit", methods=['GET', 'POST'])
def edit_item_details(item_name):
    form = EditItemForm()
    if request.method == 'POST':
        # validate form
        # make sure item belongs to current user
        # get item from db
        # save changes
        flash('You have successfully edited *** item'.format())
        return redirect(url_for("catalog"))
    return render_template("item_edit.html", form=form, current_item=item_name)


# login required
# item has to belong to current user
@app.route("/catalog_items/<string:item_name>/delete", methods=['GET', 'POST'])
def delete_item_details(item_name):
    if request.method == 'POST':
        # get item from db
        # make sure item belongs to current user
        # capture item name
        # delete item from db
        flash('You have successfully deleted the "***" item!'.format())
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


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
