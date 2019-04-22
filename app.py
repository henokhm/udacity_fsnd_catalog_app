from flask import Flask
app = Flask(__name__)


@app.route("/")
@app.route("/catalog")
def catalog():
    return "Home Page | Catalog"


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
@app.route("/add_category")
def add_category():
    return "Add New Category Page"


@app.route("/catalog/<string:category_name>/items")
def show_category(category_name):
    return "Display Page for {} Items".format(category_name)


@app.route("/catalog/<string:category_name>/edit")
def edit_category(category_name):
    return "Edit Category Page for {}".format(category_name)


@app.route("/catalog/<string:category_name>/delete")
def delete_category(category_name):
    return "Delete Category Page for {}".format(category_name)


# items CRUD
@app.route("/catalog/add_item")
def add_item():
    return "Add new Item Page"


@app.route("/catalog/<string:item_name>")
def show_item_details(category_name, item_name):
    return "Item details Page for item:{} in category:{}".format(item_name, category_name)


@app.route("/catalog/<string:item_name>/edit")
def edit_item_details(item_name):
    return "Edit Item details Page for item:{}".format(item_name)


@app.route("/catalog/<string:item_name>/delete")
def delete_item_details(item_name):
    return "Edit Item details Page for item:{}".format(item_name)


@app.route("/catalog/json")
def full_catalog_json():
    return "Full catalog JSON"


@app.route("/<string:category_name>.json")
def full_category_json():
    return "Full Category JSON"


@app.route("/<string:category_name>/<string:item_name>.json")
def single_item_json():
    return "Single Item JSON"


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
