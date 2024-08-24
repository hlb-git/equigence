"""User model module."""
from equigence import app, db
from equigence.superclass import Superclass
from equigence import login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    """Fetch user by user_id."""
    user_data = db.db.Users.find_one({'id': user_id})
    if user_data:
        user = User(firstname=user_data['firstname'],
                        lastname=user_data['lastname'],
                        email=user_data['email'], 
                        password=user_data['password'],
                        id=user_data['id'],)
        return user
    return None

class User(Superclass, UserMixin):
    """The User class."""
    # __tablename__ = 'users'
    firstname = None
    lastname = None
    email = None
    password = None
    equities = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"""
    Class: {self.__class__.__name__}
    Id: {self.id}
    Full Name: {self.firstname} {self.lastname}
    Email: {self.email}
    Date Registered: {self.createdAt}
    """
