from flask import Flask, render_template
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
    return render_template("home.html", categories=mock_categories, items=mock_items)


@app.route("/signup")
def signup():
    form = SignupForm()
    return render_template("signup.html", form=form)


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    return render_template("confirm_logout.html")


# category CRUD
@app.route("/catalog_categories/add_category")
def add_category():
    form = AddCategoryForm()
    return render_template("add_category.html", form=form)


@app.route("/catalog_categories/<string:category_name>/items")
def show_category(category_name):
    return render_template("category_items.html")


@app.route("/catalog_categories/<string:category_name>/edit")
def edit_category(category_name):
    form = EditCategoryForm()
    return render_template("category_edit.html", form=form)


@app.route("/catalog_categories/<string:category_name>/delete")
def delete_category(category_name):
    return render_template("category_confirm_delete.html")


# items CRUD
@app.route("/catalog_items/add_item")
def add_item():
    form = AddItemForm()
    return render_template("add_item.html", form=form)


@app.route("/catalog_items/<string:item_name>")
def show_item_details(item_name):
    return render_template("item_details.html")


@app.route("/catalog_items/<string:item_name>/edit")
def edit_item_details(item_name):
    form = EditItemForm()
    return render_template("item_edit.html", form=form)


@app.route("/catalog_items/<string:item_name>/delete")
def delete_item_details(item_name):
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
