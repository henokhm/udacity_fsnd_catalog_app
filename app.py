from flask import Flask, render_template, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from forms import (SignupForm, LoginForm, AddCategoryForm, EditCategoryForm,
                   AddItemForm, EditItemForm)
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = '6@kr$IhQ%teki}Juetg*x]U/QmKz{P<g'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# If app being run for first time, check if sqlite database
# already exists. If not, create it.
exists = os.path.isfile('/catalog.db')
if not exists:
    db.create_all()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    # items in category
    items = db.relationship('Item', backref='category', lazy=True)

    # creator of category
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @staticmethod
    def add_category(name, creator):
        c = Category(name=name, creator=creator)
        db.session.add(c)
        db.session.commit()

    @staticmethod
    def edit_category(category_to_edit, new_category_obj):
        category_to_edit.name = new_category_obj.name
        db.session.commit()

    @staticmethod
    def delete_category(category_to_delete):
        db.session.delete(category_to_delete)
        db.session.commit()

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'creator': self.creator,
            'items': [i.serialize() for i in self.items]
        }


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(350))

    # category of item
    cat_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    # creator of item
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @staticmethod
    def add_item(name, description, category, creator): #potential bug: creator vs creator.id
        i = Item(name=name, descriptoon=description, cat_id=category.id, user_id=creator.id)
        db.session.add(i)
        db.session.commit()

    @staticmethod
    def edit_item(item_to_edit, name, description, cat_id, user_id):
        item_to_edit.name = name
        item_to_edit.description = description
        item_to_edit.cat_id = cat_id
        item_to_edit.user_id = user_id
        db.session.commit()

    @staticmethod
    def delete_item(item_to_delete):
        db.session.delete(item_to_delete)
        db.session.commit()

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.cat.id,
            'description': self.description,
            'creator': self.creator
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(60), nullable=False)

    # categories created by user:
    categories = db.relationship('Category', backref='creator', lazy=True)
    # items created by user
    items = db.relationship('Item', backref='creator', lazy=True)

    @staticmethod
    def add_user(username, email, hashed_password):
        u = User(username=username, email=email, hashed_password=hashed_password)
        db.session.add(u)
        db.session.commit()

    @staticmethod
    def edit_user(user_to_edit, username, email, hashed_password):
        user_to_edit.username = username
        user_to_edit.email = email
        user_to_edit.hashed_password = hashed_password
        db.session.commit()

    @staticmethod
    def delete_user(user_to_delete):
        db.session.delete(user_to_delete)
        db.session.commit()


# Temporary usr for testing
current_user = User.add_user(username='henok', email='henokhm2@gmail.com',
                             hashed_password=bcrypt.generate_password_hash("1234").decode('utf-8'))



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
        Category.add_category(form.category_name.data, creator=current_user)
        flash('You have successfully added *** category')
        return redirect(url_for("catalog"))
    return render_template("add_category.html", form=form)


# login required
# TODO
@app.route("/catalog_categories/<string:category_name>/edit", methods=['GET', 'POST'])
def edit_category(category_name):
    form = EditCategoryForm()
    category = Category.qurey.filter_by(name=category_name).first()
    if form.validate_on_submit():
        if category.creator == current_user: # make sure category belongs to current user
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
        if category.creator == current_user:  # make sure category belongs to current user
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
                      creator=current_user.id)
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
        if item.user_id == current_user.id:
            # save changes to db
            Item.edit_item(item_to_edit=item,
                           name=form.item_name.data,
                           description=form.item_details.data,
                           cat_id=form.item_category.data,
                           user_id=current_user.id)
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
        if item.user_id == current_user.id:
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


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
