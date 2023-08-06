# -*- coding: utf-8 -*-
"""
Login blueprint using flask-login

# TODO https://flask-login.readthedocs.org/en/latest/#alternative-tokens
# TODO: Hash the passwords

"""

__author__ = "daniel.lindh@renter.se"
__copyright__ = "Copyright 2015, Renter AB"

from flask import Blueprint
from flask import render_template, redirect, url_for, request

from flask.ext.login import login_user, logout_user, login_required
from flask.ext.login import LoginManager, UserMixin
from wtforms import StringField, BooleanField, PasswordField, validators
from flask.ext.wtf import Form


#
# Create blueprint
#


login_pages = Blueprint(
    'login_pages', __name__,
    static_folder='login-static', template_folder='templates'
)

# The name of the python def that should be redirected too when logging in.
dashboard_func_name= None

# User/Password dictionary for users that can login.
user_database = {"user": "password"}

# Flask-login LoginManager, handles login sessions etc.
login_manager = LoginManager()


def init_app(app, func_name, users):
    """
    Initialize the blueprint before register on an application.

    :param app: A flask application that the blueprint should be registered on.
    :param func_name: The name of the python def that should be redirected too
                      when logging in.
    :param users: A dictionary with users(key) and passwords(value).
    :return:
    """
    global dashboard_func_name, user_database
    dashboard_func_name = func_name
    user_database = users
    login_manager.init_app(app)
    login_manager.login_view = 'login_pages.login'
    login_manager.session_protection = "strong"


@login_manager.user_loader
def load_user(userid):
    """Returns an User object."""
    user = User.get(userid)
    return user


class User(UserMixin):
    """User representation

    This is returned by load_user() and existing in the global current_user
    provided by flask-login after a successful login.
    """

    def __init__(self, username, password):
        self.id = username
        self.username = username
        self.password = password

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    @classmethod
    def get(cls, id):
        password = user_database.get(id)
        if password is not None:
            return User(id, password)
        else:
            return None

    @classmethod
    def validate(cls, username, password):
        user = cls.get(username)
        if user is not None:
            if user.password == password:
                return user
        return None


class LoginForm(Form):
    """WTForm representation of login.html"""
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

    def __init__(self, *args, **kwargs):
        try:
            Form.__init__(self, *args, **kwargs)
        except Exception as ex:
            exx =ex
            pass

        self.user = None

    def validate(self):
        """Validate login against user_database."""
        rv = Form.validate(self)
        if not rv:
            return False

        self.user = User.validate(self.username.data, self.password.data)
        if self.user is None:
            self.username.errors.append('Unknown username or password')
            return False
        else:
            return True


#
# Views/Routes
#


@login_pages.route('/login', methods=['GET', 'POST'])
def login():
    """Login view."""
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember_me.data)
        return redirect(request.args.get("next") or url_for(dashboard_func_name))
    return render_template("login.html", form=form)



@login_pages.route('/logout')
@login_required
def logout():
    """Logout view."""
    logout_user()
    return redirect(url_for(dashboard_func_name))
