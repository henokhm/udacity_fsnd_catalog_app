from fsnd_catalog_app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


class Category(db.Model):
    __tablename__ = 'category'
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
    __tablename__ = 'item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(350))

    # category of item
    cat_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    # creator of item
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @staticmethod
    def add_item(name, description, category, creator):   # potential bug: creator vs creator.id
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


class User(db.Model, UserMixin):
    __tablename__ = 'user'
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

