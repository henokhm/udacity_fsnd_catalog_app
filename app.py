from flask import Flask, render_template
app = Flask(__name__)


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
    return render_template("home.html")


@app.route("/signup")
def signup():
    return "Sign up Page"


@app.route("/login")
def login():
    return "Login Page"


@app.route("/logout")
def logout():
    return "Log out Page"


# category CRUD
@app.route("/catalog_categories/add_category")
def add_category():
    return "Add New Category Page"


@app.route("/catalog_categories/<string:category_name>/items")
def show_category(category_name):
    return "Display Page for {} Items".format(category_name)


@app.route("/catalog_categories/<string:category_name>/edit")
def edit_category(category_name):
    return "Edit Category Page for {}".format(category_name)


@app.route("/catalog_categories/<string:category_name>/delete")
def delete_category(category_name):
    return "Delete Category Page for {}".format(category_name)


# items CRUD
@app.route("/catalog_items/add_item")
def add_item():
    return "Add new Item Page"


@app.route("/catalog_items/<string:item_name>")
def show_item_details(item_name):
    return "Item details Page for item:{}".format(item_name)


@app.route("/catalog_items/<string:item_name>/edit")
def edit_item_details(item_name):
    return "Edit Item details Page for item:{}".format(item_name)


@app.route("/catalog_items/<string:item_name>/delete")
def delete_item_details(item_name):
    return "Delete Item details Page for item:{}".format(item_name)


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
